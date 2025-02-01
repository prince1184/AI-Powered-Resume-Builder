import streamlit as st
import requests
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Resume Builder Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    
    .stApp header {
        background-color: transparent;
    }
    
    .css-1r6slb0 {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        padding: 2rem;
        background: white;
        transition: transform 0.3s ease;
    }
    
    .css-1r6slb0:hover {
        transform: translateY(-5px);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background-color: #ffffff;
        color: #333333;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6c63ff;
        box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.2);
    }
    
    .stButton > button {
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        background: linear-gradient(45deg, #6c63ff, #4c46b3);
        color: white;
        border: none;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
    }
    
    .template-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .template-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #6c63ff, #4c46b3);
        border-radius: 10px;
    }
    
    .feedback-item {
        background: #f8f9fa;
        border-left: 4px solid #6c63ff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
        transition: all 0.3s ease;
    }
    
    .feedback-item:hover {
        transform: translateX(5px);
        background: #f0f1f2;
    }
    
    .resume-preview {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
        border: 2px solid #e0e0e0;
    }
    
    .header-container {
        background: linear-gradient(45deg, #6c63ff, #4c46b3);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    @media (prefers-color-scheme: dark) {
        .css-1r6slb0 {
            background: #1e1e1e;
        }
        
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #2d2d2d;
            color: #ffffff;
            border-color: #404040;
        }
        
        .feedback-item {
            background: #2d2d2d;
        }
        
        .resume-preview {
            background: #1e1e1e;
            border-color: #404040;
            color: #ffffff;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://127.0.0.1:8090"

# Header section with gradient background
st.markdown("""
    <div class="header-container">
        <div class="header-title">AI Resume Builder Pro ✨</div>
        <div class="header-subtitle">Create a professional resume in minutes with AI-powered suggestions</div>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for template selection
if 'templates' not in st.session_state:
    try:
        response = requests.get(f"{BACKEND_URL}/get_templates")
        st.session_state.templates = response.json()
    except:
        st.session_state.templates = {
            "modern": {
                "name": "Modern",
                "description": "Clean and contemporary design"
            }
        }

# Sidebar with template selection and tips
with st.sidebar:
    st.markdown("""
        <div style='padding: 1rem 0;'>
            <h2 style='color: #6c63ff;'>✨ Resume Templates</h2>
        </div>
    """, unsafe_allow_html=True)
    
    selected_template = st.selectbox(
        "Choose Your Style",
        options=list(st.session_state.templates.keys()),
        format_func=lambda x: st.session_state.templates[x]["name"]
    )
    
    st.markdown(f"""
        <div class='template-card'>
            <h3 style='color: #6c63ff;'>{st.session_state.templates[selected_template]['name']}</h3>
            <p>{st.session_state.templates[selected_template]['description']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
        <div style='padding: 1rem 0;'>
            <h3 style='color: #6c63ff;'>💡 Pro Tips</h3>
            <ul style='color: #666;'>
                <li>Use action verbs to describe your experience</li>
                <li>Quantify achievements with numbers</li>
                <li>Keep descriptions concise and impactful</li>
                <li>Customize for each job application</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Main content tabs
tabs = st.tabs(["📝 Personal Info", "💼 Professional Details", "🎓 Education & Skills"])

# Personal Info Tab
with tabs[0]:
    st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name", placeholder="John Doe", help="Enter your full name as it should appear on your resume")
        email = st.text_input("Email", placeholder="john.doe@email.com", help="Enter your professional email address")
    
    with col2:
        phone = st.text_input("Phone", placeholder="+1 (123) 456-7890", help="Enter your contact number")
        location = st.text_input("Location", placeholder="City, Country", help="Enter your current location")
    st.markdown("</div>", unsafe_allow_html=True)

# Professional Details Tab
with tabs[1]:
    st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Professional Title", placeholder="Software Engineer", help="Enter your current or desired job title")
        years_experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
    
    with col2:
        experience = st.text_area(
            "Professional Experience",
            placeholder="Position: Senior Software Engineer\nCompany: Tech Corp Inc.\nDuration: 2020 - Present\n\nKey Achievements:\n• Led development of key features\n• Improved system performance by 40%\n• Managed a team of 5 developers",
            height=200
        )
    st.markdown("</div>", unsafe_allow_html=True)

# Education & Skills Tab
with tabs[2]:
    st.markdown("<div class='animate-fade-in'>", unsafe_allow_html=True)
    education = st.text_area(
        "Education",
        placeholder="Degree: Bachelor of Science in Computer Science\nUniversity: Example University\nGraduation Year: 2020\nGPA: 3.8/4.0",
        height=150
    )
    
    skills = st.text_area(
        "Skills",
        placeholder="Python, JavaScript, React, Node.js, AWS, Docker",
        help="Enter your skills separated by commas"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Generate Resume Button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✨ Generate Professional Resume", use_container_width=True):
    if not all([name, email, title, skills, education, experience]):
        st.error("⚠️ Please fill in all required fields!")
    else:
        with st.spinner("🎨 Crafting your professional resume..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate_resume",
                    json={
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "location": location,
                        "title": title,
                        "years_experience": years_experience,
                        "skills": skills,
                        "education": education,
                        "experience": experience,
                        "template_style": selected_template
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    resume_text = data.get("resume")
                    score = data.get("score", 0)
                    feedback = data.get("feedback", [])
                    suggestions = data.get("suggestions", [])
                    pdf_path = data.get("pdf_path")
                    
                    st.success("✅ Resume generated successfully!")
                    
                    # Display score and feedback in columns
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("""
                            <div style='text-align: center; padding: 2rem;'>
                                <h2 style='color: #6c63ff;'>Resume Score</h2>
                                <div style='font-size: 3rem; font-weight: 700; color: #6c63ff;'>
                                    {}%
                                </div>
                            </div>
                        """.format(score), unsafe_allow_html=True)
                        
                        st.progress(score/100)
                    
                    with col2:
                        st.markdown("<h3 style='color: #6c63ff;'>🎯 Feedback & Suggestions</h3>", unsafe_allow_html=True)
                        for item in feedback:
                            st.markdown(f"<div class='feedback-item'>✨ {item}</div>", unsafe_allow_html=True)
                        for item in suggestions:
                            st.markdown(f"<div class='feedback-item'>💡 {item}</div>", unsafe_allow_html=True)
                    
                    # Display resume preview
                    st.markdown("<h3 style='color: #6c63ff;'>📄 Your Professional Resume</h3>", unsafe_allow_html=True)
                    st.markdown(f"<div class='resume-preview'>{resume_text}</div>", unsafe_allow_html=True)
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download as Text",
                            data=resume_text,
                            file_name=f"{name.lower().replace(' ', '_')}_resume.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        if pdf_path:
                            st.markdown(f"""
                                <a href="{BACKEND_URL}/download_pdf/{pdf_path}" 
                                   target="_blank" 
                                   style="text-decoration: none; width: 100%;">
                                    <button style="width: 100%; background: linear-gradient(45deg, #6c63ff, #4c46b3);
                                                 color: white; padding: 0.8rem; border: none; border-radius: 10px;
                                                 font-weight: 600; cursor: pointer;">
                                        📥 Download as PDF
                                    </button>
                                </a>
                            """, unsafe_allow_html=True)
                
                else:
                    st.error(f"❌ Error: {response.json().get('error', 'Unknown error occurred')}")
            
            except requests.exceptions.RequestException as e:
                st.error("❌ Failed to connect to the server. Please make sure the backend is running.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 1.5rem; color: #666;'>
        <p>Made with ❤️ by AI Resume Builder Pro</p>
        <p>
            <a href="#" style="color: #6c63ff; text-decoration: none; margin: 0 1rem;">Documentation</a>
            <a href="#" style="color: #6c63ff; text-decoration: none; margin: 0 1rem;">Support</a>
            <a href="#" style="color: #6c63ff; text-decoration: none; margin: 0 1rem;">Privacy Policy</a>
        </p>
    </div>
""", unsafe_allow_html=True)
