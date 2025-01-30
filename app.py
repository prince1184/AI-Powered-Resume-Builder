from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def generate_mock_resume(data):
    """Generate a mock resume for demonstration purposes"""
    resume_template = f"""
PROFESSIONAL RESUME

{data['name'].upper()}
{data['email']} | {data.get('phone', 'Phone not provided')}
{data.get('location', 'Location not provided')}

PROFESSIONAL SUMMARY
--------------------
Experienced {data['title']} with {data.get('years_experience', 0)} years of professional experience.

SKILLS
-------
{', '.join(data['skills'])}

EDUCATION
---------
{data['education']}

PROFESSIONAL EXPERIENCE
----------------------
{data['experience']}

Note: This is a demo resume. For production use, please configure a valid OpenAI API key.
"""
    return resume_template

@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    try:
        data = request.get_json()
        logger.info("Received resume generation request")
        
        # Validate required fields
        required_fields = ['name', 'email', 'title', 'skills', 'education', 'experience']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.warning(error_msg)
            return jsonify({"error": error_msg}), 400

        # Convert skills to list if it's a string
        if isinstance(data['skills'], str):
            data['skills'] = [skill.strip() for skill in data['skills'].split(',')]

        # Generate mock resume
        resume_content = generate_mock_resume(data)
        
        if resume_content:
            logger.info("Successfully generated resume")
            return jsonify({"resume": resume_content})
        else:
            error_msg = "Failed to generate resume"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 500

    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

if __name__ == "__main__":
    logger.info("Starting Flask server in demo mode...")
    logger.warning("Running with mock resume generation. For production use, please configure a valid OpenAI API key.")
    app.run(debug=True, port=8000)
