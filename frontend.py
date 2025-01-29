import requests

backend_url = "http://127.0.0.1:5000/generate_resume"

data = {"name": "Prince"}  # Example test data

response = requests.post(backend_url, json=data)

# Print response for debugging
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

# Attempt to parse JSON only if status code is 200
if response.status_code == 200:
    resume_text = response.json().get("resume", "Error generating resume")
else:
    resume_text = f"Error: {response.status_code} - {response.text}"
