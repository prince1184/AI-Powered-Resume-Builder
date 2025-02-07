# 🚀 AI-Powered Resume Builder Pro

A modern, intelligent resume builder that helps you create professional resumes with AI-powered suggestions and beautiful templates.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.0+-blue.svg)

## ✨ Features

- 🎨 **Modern Templates**: Choose from multiple professionally designed resume templates
  - Modern
  - Professional
  - Creative
  - Minimalist
  - Executive

- 🤖 **AI-Powered Suggestions**
  - Smart skill recommendations based on job title
  - Action word suggestions for experience descriptions
  - Content improvement tips
  - Real-time resume scoring

- 📊 **Resume Analysis**
  - Detailed scoring system
  - Personalized feedback
  - Content improvement suggestions
  - Format optimization tips

- 📱 **User-Friendly Interface**
  - Clean, modern design
  - Intuitive form sections
  - Real-time preview
  - Dark mode support

- 📄 **Export Options**
  - Professional PDF generation
  - Text format export
  - Multiple template styles
  - Custom formatting

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Flask
- **PDF Generation**: FPDF
- **Styling**: Custom CSS
- **Data Format**: JSON
- **HTTP Client**: Requests

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AI-Powered-Resume-Builder.git
   cd AI-Powered-Resume-Builder
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask backend server:
   ```bash
   python app.py
   ```

2. Start the Streamlit frontend:
   ```bash
   streamlit run frontend.py
   ```

3. Open your browser and navigate to:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8090

## 🎯 Usage Guide

1. **Select a Template**
   - Choose from various professional templates in the sidebar
   - Preview template styles before starting

2. **Fill in Your Details**
   - Personal Information
   - Professional Experience
   - Education & Skills

3. **Get AI Suggestions**
   - Receive smart skill recommendations
   - Get action word suggestions
   - See content improvement tips

4. **Generate & Export**
   - Preview your resume
   - Check your resume score
   - Download in PDF or text format

## 🎨 Templates

- **Modern**: Clean and contemporary design
- **Professional**: Traditional corporate style
- **Creative**: Dynamic layout for creative roles
- **Minimalist**: Simple and elegant design
- **Executive**: Sophisticated design for senior positions

## 📝 Features in Detail

### AI-Powered Suggestions
- Job-specific skill recommendations
- Action word suggestions for stronger impact
- Content length and quality analysis
- Format and structure recommendations

### Resume Scoring System
- Content quality assessment
- Skills relevance check
- Experience description analysis
- Education details evaluation
- Overall format scoring

### Professional PDF Generation
- Custom fonts and styling
- Professional formatting
- Multiple template options
- High-quality output

## 🔧 Configuration

The application can be configured through environment variables:

```bash
FLASK_PORT=8090              # Backend server port
STREAMLIT_PORT=8501          # Frontend server port
DEBUG_MODE=True              # Enable/disable debug mode
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Streamlit for the amazing web framework
- Flask for the robust backend
- FPDF for PDF generation
- All contributors and users of this project
