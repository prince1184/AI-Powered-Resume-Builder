import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import logging
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8090"

# Page config
st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 0.75rem;
        border-radius: 5px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    .form-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def create_resume():
    st.title("Create Your Professional Resume")
    
    with st.form("resume_form"):
        # Personal Details
        st.subheader("📋 Personal Details")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name*", placeholder="John Doe")
            email = st.text_input("Email*", placeholder="john@example.com")
            phone = st.text_input("Phone", placeholder="+1 234 567 8900")
        with col2:
            title = st.text_input("Professional Title", placeholder="Software Engineer")
            location = st.text_input("Location", placeholder="City, Country")
            
        # Online Presence
        st.subheader("🌐 Online Presence")
        col1, col2, col3 = st.columns(3)
        with col1:
            website = st.text_input("Website", placeholder="https://yourwebsite.com")
        with col2:
            linkedin = st.text_input("LinkedIn", placeholder="linkedin.com/in/username")
        with col3:
            github = st.text_input("GitHub", placeholder="github.com/username")
            
        # Professional Summary
        st.subheader("📝 Professional Summary")
        summary = st.text_area("Summary", placeholder="Brief overview of your professional background and career objectives")
        
        # Experience
        st.subheader("💼 Professional Experience")
        experience = st.text_area("Experience", placeholder="Company Name - Position\nMM/YYYY - MM/YYYY\n• Key responsibilities and achievements\n• Use bullet points for better readability")
        
        # Education
        st.subheader("🎓 Education")
        education = st.text_area("Education", placeholder="Degree - Institution\nMM/YYYY - MM/YYYY\n• Major/Specialization\n• Relevant coursework or achievements")
        
        # Skills
        st.subheader("🛠️ Skills")
        skills = st.text_area("Skills", placeholder="Python, JavaScript, React, Machine Learning, etc. (comma-separated)")
        
        # Languages
        st.subheader("🌍 Languages")
        languages = st.text_input("Languages", placeholder="English (Native), Spanish (Fluent), etc.")
        
        # Certificates
        st.subheader("📜 Certifications")
        certificates = st.text_area("Certificates", placeholder="Certification Name - Issuing Organization\nMM/YYYY\n• Brief description or credential ID")
        
        # Template Selection
        st.subheader("🎨 Choose Template")
        template_style = st.selectbox(
            "Template Style",
            ["modern", "professional", "creative", "minimal", "executive"]
        )
        
        submitted = st.form_submit_button("Generate Resume")
        
        if submitted:
            if not name or not email:
                st.error("Please fill in all required fields marked with *")
                return
            
            try:
                with st.spinner("Generating your resume..."):
                    resume_data = {
                        "name": name,
                        "email": email,
                        "title": title,
                        "phone": phone,
                        "location": location,
                        "website": website,
                        "linkedin": linkedin,
                        "github": github,
                        "summary": summary,
                        "experience": experience,
                        "education": education,
                        "skills": skills,
                        "languages": languages,
                        "certificates": certificates,
                        "template_style": template_style
                    }
                    
                    response = requests.post(
                        f"{API_URL}/generate_resume",
                        json=resume_data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Resume generated successfully! 🎉")
                        
                        # Show download button
                        with open(result["pdf_path"], "rb") as file:
                            st.download_button(
                                label="📥 Download Resume",
                                data=file,
                                file_name=f"resume_{name.lower().replace(' ', '_')}.pdf",
                                mime="application/pdf"
                            )
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                        
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the server. Please try again later. Error: {str(e)}")
                logger.error(f"Error generating resume: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred. Please try again. Error: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}")

def view_resumes():
    st.title("Your Resume History")
    
    email = st.text_input("Enter your email to view your resumes")
    
    if email:
        try:
            response = requests.get(
                f"{API_URL}/user/resumes/{email}",
                timeout=10
            )
            
            if response.status_code == 200:
                resumes = response.json()
                if resumes:
                    # Statistics
                    st.subheader("📊 Resume Statistics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Resumes", len(resumes))
                    with col2:
                        total_downloads = sum(r["downloaded_count"] for r in resumes)
                        st.metric("Total Downloads", total_downloads)
                    with col3:
                        avg_score = sum(r["score"] for r in resumes) / len(resumes)
                        st.metric("Average Score", f"{avg_score:.1f}/100")
                    
                    # Resume List
                    st.subheader("📄 Your Resumes")
                    for resume in resumes:
                        with st.expander(f"Resume {resume['id']} - {resume['template_style'].title()} Style"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Created:** {resume['created_at']}")
                                st.markdown(f"**Template:** {resume['template_style'].title()}")
                            with col2:
                                st.markdown(f"**Score:** {resume['score']}/100")
                                st.markdown(f"**Downloads:** {resume['downloaded_count']}")
                            
                            st.markdown("---")
                            st.markdown(f"[📥 Download Resume](http://localhost:8090/download_resume/{resume['id']})")
                else:
                    st.info("No resumes found. Create your first resume!")
                    if st.button("Create Resume Now"):
                        st.session_state["page"] = "Create Resume"
                        st.experimental_rerun()
            else:
                st.error(f"Error fetching resumes: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to fetch resumes. Please try again. Error: {str(e)}")

def main():
    st.sidebar.title("AI Resume Builder")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio("📍 Navigation", ["Create Resume", "View Resumes"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        ### 💡 Pro Tips
        - Use action verbs in experience
        - Quantify achievements
        - Keep it concise
        - Customize per job
    """)
    
    if page == "Create Resume":
        create_resume()
    else:
        view_resumes()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <div style='text-align: center;'>
            Made with ❤️ by AI Resume Builder<br>
            &copy; 2025 All rights reserved
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
