from transformers import pipeline

nlp = pipeline("text-generation", model="gpt-3.5-turbo")

def generate_resume(job_role, user_data):
    prompt = f"Generate a professional resume for {job_role} with the following details: {user_data}"
    response = nlp(prompt, max_length=300)[0]['generated_text']
    return response
