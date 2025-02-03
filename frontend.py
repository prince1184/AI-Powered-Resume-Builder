import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8090"

def create_resume():
    st.title("Create Your Resume")
    
    # Personal Information
    st.header("Personal Information")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    title = st.text_input("Professional Title")
    
    # Resume Style
    st.header("Resume Style")
    template_style = st.selectbox(
        "Choose Template Style",
        ["modern", "classic", "professional", "creative"]
    )
    
    if st.button("Generate Resume"):
        if not all([name, email, title]):
            st.error("Please fill in all required fields")
            return
            
        try:
            # Create user and resume
            user_data = {
                "name": name,
                "email": email,
                "title": title
            }
            
            resume_data = {
                "template_style": template_style,
                "score": 0,  # Initial score
                "pdf_path": f"static/resumes/{email.replace('@', '_').replace('.', '_')}.pdf"
            }
            
            response = requests.post(
                f"{API_URL}/generate_resume",
                json={**user_data, **resume_data},
                timeout=10
            )
            
            if response.status_code == 200:
                resume = response.json()
                st.success("Resume generated successfully!")
                st.markdown(f"[Download Resume](http://localhost:8090/download_resume/{resume['id']})")
            else:
                st.error("Failed to generate resume. Please try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

def view_resumes():
    st.title("Your Resume History")
    
    email = st.text_input("Enter your email to view your resumes")
    
    if email:
        try:
            logger.info(f"Fetching resumes for email: {email}")
            response = requests.get(
                f"{API_URL}/user/resumes",
                params={"email": email},
                timeout=5
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            if response.status_code == 200:
                resumes = response.json()
                if resumes:
                    # Convert to DataFrame for display
                    df = pd.DataFrame(resumes)
                    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
                    
                    st.markdown("### 📊 Resume Statistics")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Resumes", len(resumes))
                    with col2:
                        total_downloads = sum(r["downloaded_count"] for r in resumes)
                        st.metric("Total Downloads", total_downloads)
                    
                    st.markdown("### 📄 Your Resumes")
                    st.dataframe(
                        df[["template_style", "score", "downloaded_count", "created_at"]],
                        use_container_width=True
                    )
                    
                    st.markdown("### 📥 Download Your Resumes")
                    for resume in resumes:
                        with st.expander(f"Resume {resume['id']} - {resume['template_style'].title()} Style"):
                            st.markdown(f"- **Created:** {resume['created_at']}")
                            st.markdown(f"- **Score:** {resume['score']}/100")
                            st.markdown(f"- **Downloads:** {resume['downloaded_count']}")
                            st.markdown(f"[Download Resume PDF](http://localhost:8090/download_resume/{resume['id']})")
                else:
                    st.info("No resumes found for this email. Create your first resume!")
                    if st.button("Create Resume"):
                        st.session_state["page"] = "Create Resume"
                        st.experimental_rerun()
            else:
                st.error(f"Error: {response.json().get('detail', 'Failed to fetch resumes')}")
                
        except Exception as e:
            logger.error(f"Error viewing resumes: {str(e)}")
            st.error("Failed to fetch resumes. Please try again.")

def main():
    st.sidebar.title("Resume Builder")
    
    # Navigation
    page = st.sidebar.radio("Select Action", ["Create Resume", "View Resumes"])
    
    if page == "Create Resume":
        create_resume()
    else:
        view_resumes()

if __name__ == "__main__":
    main()
