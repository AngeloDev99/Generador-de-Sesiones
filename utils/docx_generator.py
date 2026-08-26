# utils/docx_generator.py
import docx
from io import BytesIO

def create_docx_from_text(content: str, title: str) -> BytesIO:
    doc = docx.Document()
    doc.add_heading(title, 0)
    
    lines = content.split('\n')
    for line in lines:
        if line.startswith('### '):
            doc.add_heading(line.replace('### ', ''), level=3)
        elif line.startswith('## '):
            doc.add_heading(line.replace('## ', ''), level=2)
        elif line.startswith('# '):
            doc.add_heading(line.replace('# ', ''), level=1)
        else:
            doc.add_paragraph(line)
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer