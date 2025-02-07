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
from fpdf import FPDF

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
    title: str = "Professional"
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""
    github: str = ""
    summary: str = ""
    experience: str = ""
    education: str = ""
    skills: str = ""
    languages: str = ""
    certificates: str = ""
    
    # Resume info
    template_style: str
    score: int = 0
    pdf_path: str = ""

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

def calculate_resume_score(resume: ResumeRequest) -> int:
    """Calculate a score for the resume based on content completeness and quality"""
    score = 0
    
    # Basic information (30 points)
    if resume.name: score += 5
    if resume.email: score += 5
    if resume.phone: score += 5
    if resume.location: score += 5
    if resume.title: score += 5
    if any([resume.website, resume.linkedin, resume.github]): score += 5
    
    # Professional Summary (10 points)
    if resume.summary and len(resume.summary.split()) >= 30:
        score += 10
    elif resume.summary:
        score += 5
    
    # Experience (25 points)
    if resume.experience:
        exp_lines = resume.experience.strip().split('\n')
        score += min(len(exp_lines) * 5, 25)
    
    # Education (15 points)
    if resume.education:
        edu_lines = resume.education.strip().split('\n')
        score += min(len(edu_lines) * 5, 15)
    
    # Skills (10 points)
    if resume.skills:
        skills_list = [s.strip() for s in resume.skills.split(',')]
        score += min(len(skills_list), 10)
    
    # Languages (5 points)
    if resume.languages:
        languages_list = resume.languages.split(',')
        score += min(len(languages_list) * 2, 5)
    
    # Certificates (5 points)
    if resume.certificates:
        cert_lines = resume.certificates.strip().split('\n')
        score += min(len(cert_lines) * 2, 5)
    
    return min(score, 100)

def generate_pdf_resume(resume: ResumeRequest, output_path: str):
    """Generate a PDF resume using FPDF"""
    from fpdf import FPDF
    
    # Create PDF object
    pdf = FPDF()
    pdf.add_page()
    
    # Set colors based on template
    colors = {
        "modern": {"primary": (44, 62, 80), "secondary": (52, 152, 219)},
        "professional": {"primary": (52, 73, 94), "secondary": (46, 204, 113)},
        "creative": {"primary": (142, 68, 173), "secondary": (231, 76, 60)},
        "minimal": {"primary": (44, 62, 80), "secondary": (149, 165, 166)},
        "executive": {"primary": (44, 62, 80), "secondary": (241, 196, 15)}
    }
    
    template = colors.get(resume.template_style, colors["modern"])
    
    # Header
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(*template["primary"])
    pdf.cell(0, 20, resume.name, ln=True, align='C')
    
    # Title
    pdf.set_font('Helvetica', 'I', 16)
    pdf.set_text_color(*template["secondary"])
    pdf.cell(0, 10, resume.title, ln=True, align='C')
    
    # Contact Info
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(*template["primary"])
    contact_info = []
    if resume.email: contact_info.append(resume.email)
    if resume.phone: contact_info.append(resume.phone)
    if resume.location: contact_info.append(resume.location)
    pdf.cell(0, 10, " | ".join(contact_info), ln=True, align='C')
    
    # Online Presence
    if any([resume.website, resume.linkedin, resume.github]):
        pdf.ln(5)
        online_info = []
        if resume.website: online_info.append(f"Website: {resume.website}")
        if resume.linkedin: online_info.append(f"LinkedIn: {resume.linkedin}")
        if resume.github: online_info.append(f"GitHub: {resume.github}")
        pdf.cell(0, 10, " | ".join(online_info), ln=True, align='C')
    
    # Summary
    if resume.summary:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*template["primary"])
        pdf.cell(0, 10, "Professional Summary", ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, resume.summary)
    
    # Experience
    if resume.experience:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*template["primary"])
        pdf.cell(0, 10, "Professional Experience", ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        for line in resume.experience.split('\n'):
            if line.strip():
                if line.startswith('•'):
                    pdf.cell(10)  # Indent bullet points
                pdf.multi_cell(0, 6, line)
    
    # Education
    if resume.education:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*template["primary"])
        pdf.cell(0, 10, "Education", ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        for line in resume.education.split('\n'):
            if line.strip():
                if line.startswith('•'):
                    pdf.cell(10)
                pdf.multi_cell(0, 6, line)
    
    # Skills
    if resume.skills:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*template["primary"])
        pdf.cell(0, 10, "Skills", ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        skills_list = [s.strip() for s in resume.skills.split(',')]
        skills_text = " • ".join(skills_list)
        pdf.multi_cell(0, 6, skills_text)
    
    # Languages
    if resume.languages:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*template["primary"])
        pdf.cell(0, 10, "Languages", ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        languages_list = [l.strip() for l in resume.languages.split(',')]
        languages_text = " • ".join(languages_list)
        pdf.multi_cell(0, 6, languages_text)
    
    # Certificates
    if resume.certificates:
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(*template["primary"])
        pdf.cell(0, 10, "Certifications", ln=True)
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(0, 0, 0)
        for line in resume.certificates.split('\n'):
            if line.strip():
                if line.startswith('•'):
                    pdf.cell(10)
                pdf.multi_cell(0, 6, line)
    
    # Save PDF
    try:
        pdf.output(output_path)
        return True
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return False

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
    try:
        # Find or create user
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
            logger.info(f"Created new user: {user.id}")
        
        # Generate unique filename
        pdf_filename = f"{user.email.replace('@', '_').replace('.', '_')}_{int(datetime.utcnow().timestamp())}.pdf"
        pdf_path = os.path.join("static/resumes", pdf_filename)
        
        # Calculate resume score
        score = calculate_resume_score(request)
        
        # Create resume entry
        resume = Resume(
            user_id=user.id,
            template_style=request.template_style,
            score=score,
            pdf_path=pdf_path,
            downloaded_count=0
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        logger.info(f"Created resume entry: {resume.id}")
        
        # Generate PDF
        if not generate_pdf_resume(request, pdf_path):
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF resume"
            )
        
        return resume
        
    except Exception as e:
        logger.error(f"Error in generate_resume: {str(e)}")
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
