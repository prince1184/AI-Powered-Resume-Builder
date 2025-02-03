import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from requests.exceptions import RequestException
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:8090"

def check_server():
    try:
        response = requests.get(f"{API_URL}/docs", timeout=2)
        return response.status_code == 200
    except:
        return False

def login():
    st.title("Admin Login")
    
    # Check server status
    if not check_server():
        st.error("⚠️ Backend server is not running. Please start the server first.")
        if st.button("Retry Connection"):
            st.experimental_rerun()
        return
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            with st.spinner("Logging in..."):
                logger.info(f"Attempting login with username: {username}")
                
                # Debug: Print request details
                logger.info(f"Sending request to: {API_URL}/token")
                logger.info(f"Request data: username={username}")
                
                response = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password},
                    timeout=5
                )
                
                # Debug: Print response details
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response headers: {response.headers}")
                logger.info(f"Response content: {response.text}")
                
                if response.status_code == 200:
                    st.session_state["token"] = response.json()["access_token"]
                    st.success("Successfully logged in!")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
                    logger.warning(f"Login failed. Status code: {response.status_code}")
        except RequestException as e:
            st.error("Could not connect to the backend server. Please make sure it's running.")
            logger.error(f"Connection error: {str(e)}")
            if st.button("Retry"):
                st.experimental_rerun()

def show_dashboard():
    st.title("Resume Builder Admin Dashboard")
    
    try:
        # Get stats
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        
        with st.spinner("Loading dashboard..."):
            stats_response = requests.get(f"{API_URL}/admin/stats", headers=headers, timeout=5)
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                
                # Display metrics in a nice layout
                st.markdown("### 📊 Overview")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("👥 Total Users", stats["total_users"])
                with col2:
                    st.metric("📄 Total Resumes", stats["total_resumes"])
                with col3:
                    st.metric("⬇️ Total Downloads", stats["total_downloads"])
                
                # Show users
                st.markdown("### 👥 Recent Users")
                users_response = requests.get(f"{API_URL}/admin/users", headers=headers, timeout=5)
                if users_response.status_code == 200:
                    users = users_response.json()
                    if users:
                        users_df = pd.DataFrame(users)
                        users_df["created_at"] = pd.to_datetime(users_df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
                        st.dataframe(users_df[["name", "email", "title", "created_at"]], use_container_width=True)
                    else:
                        st.info("No users found")
                
                # Show resumes
                st.markdown("### 📄 Recent Resumes")
                resumes_response = requests.get(f"{API_URL}/admin/resumes", headers=headers, timeout=5)
                if resumes_response.status_code == 200:
                    resumes = resumes_response.json()
                    if resumes:
                        resumes_df = pd.DataFrame(resumes)
                        resumes_df["created_at"] = pd.to_datetime(resumes_df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
                        st.dataframe(resumes_df[["id", "template_style", "score", "downloaded_count", "created_at"]], use_container_width=True)
                    else:
                        st.info("No resumes found")
                        
            elif stats_response.status_code == 401:
                st.error("Session expired. Please login again.")
                del st.session_state["token"]
                st.experimental_rerun()
            else:
                st.error(f"Error fetching data: {stats_response.status_code}")
                
    except RequestException as e:
        st.error("Could not connect to the backend server. Please make sure it's running.")
        logger.error(f"Connection error: {str(e)}")
        if st.button("Retry"):
            st.experimental_rerun()

def main():
    # Add a sidebar
    st.sidebar.title("Resume Builder Admin")
    
    if "token" not in st.session_state:
        login()
    else:
        show_dashboard()
        if st.sidebar.button("Logout"):
            del st.session_state["token"]
            st.experimental_rerun()

if __name__ == "__main__":
    main()
