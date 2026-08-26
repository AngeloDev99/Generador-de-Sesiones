# utils/document_parser.py
import docx
import pdfplumber

def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.name
    text = ""
    
    if filename.endswith('.docx'):
        doc = docx.Document(uploaded_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    elif filename.endswith('.pdf'):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    return text