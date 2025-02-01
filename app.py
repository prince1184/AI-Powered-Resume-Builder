from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import os
from datetime import datetime
from fpdf import FPDF
import json
import re
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Create directories for temporary files
TEMP_DIR = Path("temp_pdfs")
TEMP_DIR.mkdir(exist_ok=True)
PREVIEW_DIR = Path("template_previews")
PREVIEW_DIR.mkdir(exist_ok=True)

# Resume templates with more variety and styling
TEMPLATES = {
    "modern": {
        "name": "Modern",
        "description": "Clean and contemporary design with a focus on readability",
        "color_scheme": {"primary": "#1E88E5", "secondary": "#F5F5F5"},
        "font": "Arial",
        "sections": ["summary", "skills", "experience", "education"]
    },
    "professional": {
        "name": "Professional",
        "description": "Traditional format ideal for corporate positions",
        "color_scheme": {"primary": "#2E7D32", "secondary": "#E8F5E9"},
        "font": "Times New Roman",
        "sections": ["experience", "skills", "education", "achievements"]
    },
    "creative": {
        "name": "Creative",
        "description": "Dynamic layout perfect for creative industries",
        "color_scheme": {"primary": "#6200EA", "secondary": "#EDE7F6"},
        "font": "Helvetica",
        "sections": ["skills", "projects", "experience", "education"]
    },
    "minimalist": {
        "name": "Minimalist",
        "description": "Simple and elegant design that focuses on content",
        "color_scheme": {"primary": "#212121", "secondary": "#F5F5F5"},
        "font": "Calibri",
        "sections": ["summary", "experience", "skills", "education"]
    },
    "executive": {
        "name": "Executive",
        "description": "Sophisticated design for senior positions",
        "color_scheme": {"primary": "#B71C1C", "secondary": "#FFEBEE"},
        "font": "Georgia",
        "sections": ["summary", "achievements", "experience", "education"]
    }
}

# AI-powered suggestions
SKILL_SUGGESTIONS = {
    "software": ["Python", "JavaScript", "Java", "C++", "SQL", "AWS", "Docker", "Git"],
    "marketing": ["Digital Marketing", "SEO", "Social Media", "Content Strategy", "Analytics"],
    "design": ["UI/UX", "Adobe Creative Suite", "Figma", "Sketch", "Typography"],
    "management": ["Project Management", "Team Leadership", "Agile", "Scrum", "Budget Planning"]
}

ACTION_WORDS = {
    "leadership": ["Led", "Managed", "Directed", "Supervised", "Orchestrated"],
    "achievement": ["Achieved", "Exceeded", "Improved", "Increased", "Reduced"],
    "development": ["Developed", "Created", "Designed", "Implemented", "Built"],
    "collaboration": ["Collaborated", "Partnered", "Coordinated", "Facilitated"]
}

def get_skill_suggestions(title):
    """Get relevant skill suggestions based on job title"""
    title_lower = title.lower()
    suggestions = []
    
    if any(word in title_lower for word in ["developer", "engineer", "programmer"]):
        suggestions.extend(SKILL_SUGGESTIONS["software"])
    if any(word in title_lower for word in ["marketing", "seo", "content"]):
        suggestions.extend(SKILL_SUGGESTIONS["marketing"])
    if any(word in title_lower for word in ["designer", "creative", "artist"]):
        suggestions.extend(SKILL_SUGGESTIONS["design"])
    if any(word in title_lower for word in ["manager", "director", "lead"]):
        suggestions.extend(SKILL_SUGGESTIONS["management"])
    
    return list(set(suggestions))

def get_action_word_suggestions(experience):
    """Suggest action words to improve experience descriptions"""
    suggestions = []
    exp_lower = experience.lower()
    
    if any(word in exp_lower for word in ["team", "group", "department"]):
        suggestions.extend(ACTION_WORDS["leadership"])
    if any(word in exp_lower for word in ["improve", "increase", "reduce"]):
        suggestions.extend(ACTION_WORDS["achievement"])
    if any(word in exp_lower for word in ["create", "build", "develop"]):
        suggestions.extend(ACTION_WORDS["development"])
    if any(word in exp_lower for word in ["team", "partner", "collaborate"]):
        suggestions.extend(ACTION_WORDS["collaboration"])
    
    return list(set(suggestions))

def score_resume(data):
    """Enhanced resume scoring with more detailed feedback"""
    score = 0
    feedback = []
    suggestions = []
    
    # Content length and quality
    if len(data['experience']) > 200:
        score += 15
    else:
        feedback.append("Add more detail to your experience section")
    
    # Skills analysis
    skills = [s.strip() for s in data['skills'].split(',')]
    if len(skills) >= 5:
        score += 15
    else:
        feedback.append("List at least 5 relevant skills")
    
    # Suggested skills
    suggested_skills = get_skill_suggestions(data['title'])
    missing_important_skills = [s for s in suggested_skills if s not in skills]
    if missing_important_skills:
        suggestions.append(f"Consider adding these relevant skills: {', '.join(missing_important_skills[:3])}")
    
    # Education details
    if len(data['education']) > 100:
        score += 15
    else:
        feedback.append("Provide more details about your education")
    
    # Contact information
    if all([data['email'], data['phone'], data['location']]):
        score += 15
    else:
        feedback.append("Include all contact information")
    
    # Action words in experience
    action_words = get_action_word_suggestions(data['experience'])
    exp_lower = data['experience'].lower()
    action_word_count = sum(1 for word in action_words if word.lower() in exp_lower)
    
    if action_word_count >= 3:
        score += 20
    else:
        suggestions.append(f"Try using these action words: {', '.join(action_words[:3])}")
    
    # Length of professional experience
    if data.get('years_experience', 0) > 0:
        score += 10
    
    # Formatting and structure
    if len(data['experience'].split('\n')) > 3:
        score += 10
    else:
        feedback.append("Break down your experience into more bullet points")
    
    return score, feedback, suggestions

def generate_pdf_resume(data, template_style="modern"):
    """Enhanced PDF generation with better styling"""
    template = TEMPLATES[template_style]
    pdf = FPDF()
    pdf.add_page()
    
    # Set colors
    primary_color = template["color_scheme"]["primary"]
    secondary_color = template["color_scheme"]["secondary"]
    
    # Header
    pdf.set_fill_color(int(primary_color[1:3], 16), int(primary_color[3:5], 16), int(primary_color[5:7], 16))
    pdf.rect(0, 0, 210, 40, 'F')
    
    # Name and title
    pdf.set_font(template["font"], 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 20, data['name'], ln=True, align='C')
    
    pdf.set_font(template["font"], '', 14)
    pdf.cell(0, 10, data['title'], ln=True, align='C')
    
    # Contact information
    pdf.set_text_color(0, 0, 0)
    pdf.set_font(template["font"], '', 10)
    contact_info = f"{data['email']} | {data['phone']} | {data['location']}"
    pdf.cell(0, 10, contact_info, ln=True, align='C')
    
    # Skills section
    pdf.set_font(template["font"], 'B', 14)
    pdf.cell(0, 10, "Skills", ln=True)
    pdf.set_font(template["font"], '', 12)
    skills_text = ", ".join(data['skills'].split(","))
    pdf.multi_cell(0, 10, skills_text)
    
    # Experience section
    pdf.ln(10)
    pdf.set_font(template["font"], 'B', 14)
    pdf.cell(0, 10, "Professional Experience", ln=True)
    pdf.set_font(template["font"], '', 12)
    pdf.multi_cell(0, 10, data['experience'])
    
    # Education section
    pdf.ln(10)
    pdf.set_font(template["font"], 'B', 14)
    pdf.cell(0, 10, "Education", ln=True)
    pdf.set_font(template["font"], '', 12)
    pdf.multi_cell(0, 10, data['education'])
    
    # Save PDF
    pdf_path = TEMP_DIR / f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(str(pdf_path))
    return pdf_path

def generate_mock_resume(data, template_style="modern"):
    """Generate a mock resume with enhanced styling"""
    template = TEMPLATES[template_style]
    
    resume_template = f"""
{template['name'].upper()} RESUME TEMPLATE

{data['name'].upper()}
{data['title']}
{data['email']} | {data.get('phone', 'Phone not provided')} | {data.get('location', 'Location not provided')}

PROFESSIONAL SUMMARY
--------------------
{data['title']} with {data.get('years_experience', 0)} years of experience, specializing in {data['skills'].split(',')[0]}.

SKILLS
-------
{', '.join(data['skills'].split(','))}

EDUCATION
---------
{data['education']}

PROFESSIONAL EXPERIENCE
----------------------
{data['experience']}

Note: This is a demo resume. For production use, please configure a valid OpenAI API key.
"""
    return resume_template

@app.route("/get_templates", methods=["GET"])
def get_templates():
    """Get available resume templates"""
    return jsonify(TEMPLATES)

@app.route("/get_suggestions", methods=["POST"])
def get_suggestions():
    """Get AI-powered suggestions for resume improvement"""
    try:
        data = request.get_json()
        skill_suggestions = get_skill_suggestions(data.get('title', ''))
        action_word_suggestions = get_action_word_suggestions(data.get('experience', ''))
        
        return jsonify({
            "skill_suggestions": skill_suggestions,
            "action_word_suggestions": action_word_suggestions
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

        # Get template style
        template_style = data.get('template_style', 'modern')
        if template_style not in TEMPLATES:
            template_style = 'modern'

        # Generate resume content
        resume_content = generate_mock_resume(data, template_style)
        
        # Generate PDF
        pdf_path = generate_pdf_resume(data, template_style)
        
        # Score resume and get suggestions
        score, feedback, suggestions = score_resume(data)
        
        if resume_content:
            logger.info("Successfully generated resume")
            return jsonify({
                "resume": resume_content,
                "score": score,
                "feedback": feedback,
                "suggestions": suggestions,
                "pdf_path": str(pdf_path.name)
            })
        else:
            error_msg = "Failed to generate resume"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 500

    except Exception as e:
        error_msg = f"Server error: {str(e)}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route("/download_pdf/<filename>", methods=["GET"])
def download_pdf(filename):
    """Download generated PDF resume"""
    try:
        return send_file(
            TEMP_DIR / filename,
            as_attachment=True,
            download_name=f"resume_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    logger.info("Starting Flask server in demo mode...")
    logger.warning("Running with mock resume generation. For production use, please configure a valid OpenAI API key.")
    app.run(debug=True, port=8090)
