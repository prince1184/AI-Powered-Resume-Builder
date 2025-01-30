import requests
import streamlit as st
import json

# Configure the page
st.set_page_config(
    page_title="AI-Powered Resume Builder",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# Backend URL
backend_url = "http://127.0.0.1:8000/generate_resume"

# Title and description
st.title("🚀 AI-Powered Resume Builder")
st.markdown("### Create a professional resume in seconds using AI")

# Create two columns for input fields
col1, col2 = st.columns(2)

with col1:
    # Personal Information
    st.subheader("Personal Information")
    name = st.text_input("Full Name*", placeholder="John Doe")
    email = st.text_input("Email*", placeholder="john.doe@email.com")
    phone = st.text_input("Phone Number", placeholder="+1 (123) 456-7890")
    location = st.text_input("Location", placeholder="City, Country")

with col2:
    # Professional Summary
    st.subheader("Professional Details")
    title = st.text_input("Professional Title*", placeholder="Software Engineer")
    years_experience = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
    skills = st.text_area("Key Skills (comma-separated)*", 
                         placeholder="Python, JavaScript, Machine Learning, Project Management")
    
# Education and Experience
st.subheader("Education & Experience")
education = st.text_area("Education Background*", 
                        placeholder="Degree, Institution, Year\nExample: Bachelor's in Computer Science, MIT, 2020")
experience = st.text_area("Work Experience*",
                         placeholder="Position, Company, Duration, Key Achievements\nExample: Software Engineer, Google, 2020-2023, Led development of key features")

if st.button("Generate Resume 📄"):
    # Validate required fields
    required_fields = {
        "name": name,
        "email": email,
        "title": title,
        "skills": skills,
        "education": education,
        "experience": experience
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value.strip()]
    
    if missing_fields:
        st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
    else:
        # Show loading spinner
        with st.spinner("Generating your resume..."):
            # Prepare data for API
            data = {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "title": title,
                "years_experience": years_experience,
                "skills": [skill.strip() for skill in skills.split(",")],
                "education": education,
                "experience": experience
            }
            
            try:
                response = requests.post(backend_url, json=data)
                
                if response.status_code == 200:
                    resume_data = response.json()
                    resume_text = resume_data.get("resume", "Error generating resume")
                    
                    # Display the generated resume in a nice format
                    st.success("Resume generated successfully! 🎉")
                    st.markdown("### Generated Resume")
                    st.text_area("", resume_text, height=400)
                    
                    # Add download button
                    st.download_button(
                        label="Download Resume",
                        data=resume_text,
                        file_name=f"{name.lower().replace(' ', '_')}_resume.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the server: {str(e)}")
                st.info("Please make sure the backend server is running at " + backend_url)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by AI-Powered Resume Builder")
