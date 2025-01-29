# AI-Powered Resume Builder

## Description
This project is an AI-powered resume builder that generates professional resumes tailored for specific job roles using AI. Users can input their details, and the system will suggest optimized resumes with skills and formatting recommendations.

## Features
- AI-based suggestions for skills and formatting
- Real-time preview of the resume
- Export resume to PDF
- Integration with LinkedIn for fetching user data (optional)
- Built entirely using Python

---

## Tech Stack
- **Backend**: Flask (REST API)
- **Frontend**: Streamlit
- **Database**: SQLite/PostgreSQL
- **AI Model**: Transformers (GPT-based)
- **PDF Generation**: FPDF
- **Web Scraping (LinkedIn Integration)**: Selenium, BeautifulSoup

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-resume-builder.git
cd ai-resume-builder
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Usage

### 1. Start the Flask Backend
```bash
python app.py
```
The API will start on `http://127.0.0.1:5000/`

### 2. Start the Streamlit Frontend
```bash
streamlit run frontend.py
```
The UI will be available at `http://localhost:8501/`

---

## API Endpoints
- **POST /generate_resume**
  - **Description**: Generates a resume based on user input
  - **Request Body (JSON)**:
    ```json
    {
      "job_role": "Software Engineer",
      "user_data": "Name: John Doe, Experience: 3 years in Python, ..."
    }
    ```
  - **Response**:
    ```json
    {
      "resume": "Generated Resume Content"
    }
    ```

---

## Deployment
### **Deploy Backend on Render**
1. Push your project to **GitHub**.
2. Create a **new Web Service** on [Render](https://render.com/).
3. Select your GitHub repo and set the **start command**:
   ```bash
   gunicorn app:app
   ```
4. Deploy & get the API URL.

### **Deploy Frontend on Streamlit Cloud**
1. Go to [Streamlit Cloud](https://share.streamlit.io/).
2. Click **New App**, connect GitHub repo.
3. Set the **Main file path** as `frontend.py`.
4. Deploy & get the app URL.

---

## Future Enhancements
- AI-powered resume templates
- Resume ranking based on job descriptions
- Job application tracking system
- Advanced LinkedIn integration

---

## License
This project is licensed under the MIT License. Feel free to modify and distribute!

---

## Contact
For any issues, contact **PrinceSharma** at princesharma8894@gmail.com.

