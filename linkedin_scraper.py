from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

def fetch_linkedin_profile(email, password):
    driver = webdriver.Chrome()
    driver.get("https://www.linkedin.com/login")

    driver.find_element("id", "username").send_keys(email)
    driver.find_element("id", "password").send_keys(password + Keys.RETURN)
    
    time.sleep(5)  # Wait for page load
    profile_data = driver.page_source  # Scrape data
    driver.quit()
    
    return profile_data
