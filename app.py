from fastapi import FastAPI, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import os
import logging
import aiofiles
from database import get_db, Admin, User, Resume
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Resume Builder API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AdminBase(BaseModel):
    username: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class AdminResponse(AdminBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: EmailStr
    title: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    title: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeBase(BaseModel):
    template_style: str
    score: int = 0
    pdf_path: str

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    template_style: str
    score: int
    pdf_path: str
    downloaded_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeRequest(BaseModel):
    # User info
    name: str
    email: EmailStr
    title: str
    
    # Resume info
    template_style: str
    score: int = 0
    pdf_path: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_admin(username: str, password: str, db: Session):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    admin = db.query(Admin).filter(Admin.username == token_data.username).first()
    if admin is None:
        raise credentials_exception
    return admin

# Routes
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        # Debug: Check if admin exists
        admin = db.query(Admin).filter(Admin.username == form_data.username).first()
        if not admin:
            logger.warning(f"Admin not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Debug: Check password
        logger.info(f"Verifying password for admin: {form_data.username}")
        if not verify_password(form_data.password, admin.hashed_password):
            logger.warning(f"Invalid password for admin: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": admin.username}, expires_delta=access_token_expires
        )
        logger.info(f"Successful login for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise

@app.post("/admin/create", response_model=Token)
async def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating new admin user: {admin.username}")
    try:
        # Check if admin already exists
        db_admin = db.query(Admin).filter(
            (Admin.username == admin.username) | (Admin.email == admin.email)
        ).first()
        if db_admin:
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered"
            )
            
        # Create new admin
        db_admin = Admin(
            username=admin.username,
            email=admin.email,
            hashed_password=get_password_hash(admin.password)
        )
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        
        # Generate token
        access_token = create_access_token(data={"sub": admin.username})
        logger.info(f"Successfully created admin user: {admin.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        db.rollback()
        raise

@app.post("/generate_resume", response_model=ResumeResponse)
async def generate_resume(request: ResumeRequest, db: Session = Depends(get_db)):
    """Generate a new resume for a user"""
    logger.info(f"Generating resume for user: {request.email}")
    try:
        # Create or get existing user
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            user = User(
                name=request.name,
                email=request.email,
                title=request.title
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {user.email}")
        
        # Ensure resumes directory exists
        os.makedirs("static/resumes", exist_ok=True)
        
        # Generate PDF path
        pdf_filename = f"{user.email.replace('@', '_').replace('.', '_')}_{int(datetime.utcnow().timestamp())}.pdf"
        pdf_path = os.path.join("static/resumes", pdf_filename)
        
        # Create resume entry
        resume = Resume(
            user_id=user.id,
            template_style=request.template_style,
            score=request.score,
            pdf_path=pdf_path,
            downloaded_count=0
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        logger.info(f"Created resume entry: {resume.id}")
        
        # Create a simple PDF (placeholder)
        try:
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.drawString(100, 750, f"Name: {user.name}")
            c.drawString(100, 730, f"Email: {user.email}")
            c.drawString(100, 710, f"Title: {user.title}")
            c.drawString(100, 690, f"Template: {resume.template_style}")
            c.save()
            logger.info(f"Generated PDF: {pdf_path}")
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF"
            )
        
        return resume
        
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/admin/stats", dependencies=[Depends(get_current_admin)])
async def get_admin_stats(db: Session = Depends(get_db)):
    logger.info("Fetching admin stats")
    try:
        total_users = db.query(User).count()
        total_resumes = db.query(Resume).count()
        total_downloads = db.query(func.sum(Resume.downloaded_count)).scalar() or 0
        
        logger.info("Admin stats fetched successfully")
        return {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "total_downloads": total_downloads
        }
    except Exception as e:
        logger.error(f"Error fetching admin stats: {str(e)}")
        raise

@app.get("/admin/users", response_model=List[UserResponse], dependencies=[Depends(get_current_admin)])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    logger.info("Fetching all users")
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        logger.info("Users fetched successfully")
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise

@app.get("/admin/resumes", response_model=List[ResumeResponse], dependencies=[Depends(get_current_admin)])
async def get_all_resumes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    logger.info("Fetching all resumes")
    try:
        resumes = db.query(Resume).offset(skip).limit(limit).all()
        logger.info("Resumes fetched successfully")
        return resumes
    except Exception as e:
        logger.error(f"Error fetching resumes: {str(e)}")
        raise

@app.get("/user/resumes", response_model=list[ResumeResponse])
async def get_user_resumes(email: str, db: Session = Depends(get_db)):
    """Get all resumes for a specific user by email"""
    logger.info(f"Fetching resumes for user: {email}")
    try:
        # Get user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.warning(f"User not found: {email}")
            return []
            
        # Get resumes
        resumes = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).all()
        logger.info(f"Found {len(resumes)} resumes for user: {email}")
        return resumes
        
    except Exception as e:
        logger.error(f"Error fetching user resumes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/download_resume/{resume_id}")
async def download_resume(resume_id: int, db: Session = Depends(get_db)):
    """Download a specific resume by ID"""
    logger.info(f"Downloading resume: {resume_id}")
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Increment download count
        resume.downloaded_count += 1
        db.commit()
        
        # Return PDF file
        return FileResponse(
            resume.pdf_path,
            media_type="application/pdf",
            filename=f"resume_{resume_id}.pdf"
        )
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8090,
        reload=True,
        log_level="debug",
        access_log=True
    )
