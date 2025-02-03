# AI-Powered Resume Builder 

A modern web application that helps users create professional resumes with ease. The system includes both a user-facing resume builder and an admin panel for monitoring.

## Features 

### For Users
- Create professional resumes with different template styles
- View and manage your resume history
- Download resumes in PDF format
- Track resume statistics (downloads, scores)

### For Admins
- Secure admin panel with JWT authentication
- Monitor system statistics
- View all users and resumes
- Track usage metrics

## Technology Stack 

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **PDF Generation**: ReportLab
- **Development Tools**: Python 3.11+

## Project Structure 

```
AI-Powered-Resume-Builder/
├── app.py              # FastAPI backend server
├── frontend.py         # User-facing Streamlit interface
├── admin_panel.py      # Admin dashboard (Streamlit)
├── database.py         # Database models and configuration
├── requirements.txt    # Python dependencies
└── static/
    └── resumes/       # Generated PDF resumes
```

## Setup Instructions 

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AI-Powered-Resume-Builder.git
cd AI-Powered-Resume-Builder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the servers:
```bash
# Start FastAPI backend (Terminal 1)
python app.py

# Start Admin Panel (Terminal 2)
streamlit run admin_panel.py --server.port 8091

# Start User Frontend (Terminal 3)
streamlit run frontend.py --server.port 8092
```

4. Access the applications:
- User Frontend: http://localhost:8092
- Admin Panel: http://localhost:8091
- API Documentation: http://localhost:8090/docs

## Usage Guide 

### For Users
1. Visit http://localhost:8092
2. Choose "Create Resume"
3. Fill in your details and select a template style
4. Generate and download your resume
5. View your resume history using your email

### For Admins
1. Visit http://localhost:8090/docs
2. Create an admin account using the `/admin/create` endpoint
3. Visit http://localhost:8091
4. Log in with your admin credentials
5. Access the admin dashboard

## API Endpoints 

### User Endpoints
- `POST /generate_resume`: Create a new resume
- `GET /user/resumes`: Get user's resume history
- `GET /download_resume/{resume_id}`: Download a specific resume

### Admin Endpoints
- `POST /admin/create`: Create admin account
- `POST /token`: Admin login
- `GET /admin/stats`: Get system statistics
- `GET /admin/users`: List all users
- `GET /admin/resumes`: List all resumes

## Security Features 

- JWT-based authentication for admin access
- Password hashing using bcrypt
- Input validation and sanitization
- Secure file handling for PDFs

## Contributing 

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 

This project is licensed under the MIT License - see the LICENSE file for details.
