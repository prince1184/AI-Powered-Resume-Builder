import requests
import streamlit as st

# Ensure this URL matches your Flask backend
backend_url = "http://127.0.0.0:9000/generate_resume"

st.title("AI-Powered Resume Builder")

# User input
name = st.text_input("Enter your name:", "Prince")

if st.button("Generate Resume"):
    data = {"name": name}
    
    try:
        response = requests.post(backend_url, json=data)

        # Debugging output
        st.write(f"Status Code: {response.status_code}")
        st.write(f"Response Text: {response.text}")

        if response.status_code == 200:
            resume_text = response.json().get("resume", "Error generating resume")
        else:
            resume_text = f"Error: {response.status_code} - {response.text}"
        
        st.write("Generated Resume:")
        st.text_area("Resume Output", resume_text, height=200)

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
