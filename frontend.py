import requests
import streamlit as st
import json

# Page configuration
st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    
    h1, h2, h3 {
        color: #1E88E5;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 10px;
        border-radius: 5px;
        color: #000000;
        font-size: 16px;
    }
    
    /* Dark theme support */
    @media (prefers-color-scheme: dark) {
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #2b2b2b;
            color: #ffffff;
            border-color: #404040;
        }
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
    }
    
    .stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1976D2;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .css-1r6slb0 {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Dark theme support for content boxes */
    @media (prefers-color-scheme: dark) {
        .css-1r6slb0 {
            background-color: #1e1e1e;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
    }
    
    .resume-output {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        margin-top: 20px;
        border: 1px solid #e0e0e0;
        color: #000000;
    }
    
    /* Dark theme support for resume output */
    @media (prefers-color-scheme: dark) {
        .resume-output {
            background-color: #2b2b2b;
            color: #ffffff;
            border-color: #404040;
        }
    }
    
    .info-box {
        background-color: #E3F2FD;
        padding: 20px;
        border-radius: 5px;
        margin-bottom: 30px;
        border-left: 5px solid #1E88E5;
    }
    
    .required-field::after {
        content: " *";
        color: red;
    }
    
    .tab-content {
        padding: 20px;
        background-color: white;
        border-radius: 0 0 5px 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Dark theme support for tab content */
    @media (prefers-color-scheme: dark) {
        .tab-content {
            background-color: #1e1e1e;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
    }
    </style>
""", unsafe_allow_html=True)

# Backend URL
backend_url = "http://127.0.0.1:8000/generate_resume"

# Header section
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1>🚀 AI-Powered Resume Builder</h1>
        <div class='info-box'>
            <h3 style='color: #1976D2; margin-top: 0;'>Create Your Professional Resume in Minutes</h3>
            <p>Fill in your details below, and let our AI help you create a stunning resume that stands out!</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Create tabs for different sections
tabs = st.tabs(["📋 Personal Info", "💼 Professional Details", "🎓 Education & Experience"])

# Personal Info Tab
with tabs[0]:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            help="Enter your full name as it should appear on your resume"
        )
        email = st.text_input(
            "Email",
            placeholder="john.doe@email.com",
            help="Enter your professional email address"
        )
    
    with col2:
        phone = st.text_input(
            "Phone Number",
            placeholder="+1 (123) 456-7890",
            help="Enter your contact number with country code"
        )
        location = st.text_input(
            "Location",
            placeholder="City, Country",
            help="Enter your current location"
        )
    st.markdown("</div>", unsafe_allow_html=True)

# Professional Details Tab
with tabs[1]:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Professional Details")
    
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input(
            "Professional Title",
            placeholder="Software Engineer",
            help="Enter your current or desired job title"
        )
        years_experience = st.number_input(
            "Years of Experience",
            min_value=0,
            max_value=50,
            value=0,
            help="Enter your total years of professional experience"
        )
    
    with col2:
        skills = st.text_area(
            "Key Skills",
            placeholder="Python, JavaScript, Project Management...",
            help="Enter your skills separated by commas",
            height=100
        )
    st.markdown("</div>", unsafe_allow_html=True)

# Education & Experience Tab
with tabs[2]:
    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
    st.subheader("Education & Experience")
    
    education = st.text_area(
        "Education Background",
        placeholder="""Degree: Bachelor of Science in Computer Science
University: Example University
Graduation Year: 2020
GPA: 3.8/4.0

Add more education details...""",
        height=150
    )
    
    experience = st.text_area(
        "Professional Experience",
        placeholder="""Position: Senior Software Engineer
Company: Tech Corp Inc.
Duration: 2020 - Present
Key Achievements:
- Led development of key features
- Improved system performance by 40%
- Managed a team of 5 developers

Add more experience...""",
        height=200
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Generate Resume Button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("✨ Generate Professional Resume", use_container_width=True):
    if not all([name, email, title, skills, education, experience]):
        st.error("⚠️ Please fill in all required fields!")
    else:
        with st.spinner("🔄 Crafting your professional resume..."):
            try:
                response = requests.post(
                    backend_url,
                    json={
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "location": location,
                        "title": title,
                        "years_experience": years_experience,
                        "skills": skills,
                        "education": education,
                        "experience": experience
                    }
                )
                
                if response.status_code == 200:
                    resume_text = response.json().get("resume")
                    
                    # Success message
                    st.success("✅ Resume generated successfully!")
                    
                    # Display the generated resume
                    st.markdown("### 📄 Your Professional Resume")
                    st.markdown(f'<div class="resume-output">{resume_text}</div>', unsafe_allow_html=True)
                    
                    # Download button
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📥 Download Resume",
                            data=resume_text,
                            file_name=f"{name.lower().replace(' ', '_')}_resume.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                else:
                    st.error(f"❌ Error: {response.json().get('error', 'Unknown error occurred')}")
            
            except requests.exceptions.RequestException as e:
                st.error("❌ Failed to connect to the server. Please make sure the backend is running.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Made with ❤️ by AI Resume Builder</p>
        <p>Need help? Check out our <a href="#" style="color: #1E88E5;">documentation</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
