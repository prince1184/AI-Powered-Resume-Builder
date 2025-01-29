from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(200, 10, "Generated Resume", ln=True, align="C")

def generate_pdf(resume_text, filename="resume.pdf"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, resume_text)
    pdf.output(filename)

    return filename
