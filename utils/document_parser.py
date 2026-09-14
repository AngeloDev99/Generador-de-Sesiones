# utils/document_parser.py
import docx
import pdfplumber

def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.name
    text = ""
    
    if filename.endswith('.docx'):
        doc = docx.Document(uploaded_file)
        
        # Iterar sobre los elementos del XML del documento para capturar párrafos y tablas en orden
        for block in doc.element.body:
            if block.tag.endswith('}p'):  # Si el bloque es un párrafo (w:p)
                p = docx.text.paragraph.Paragraph(block, doc)
                if p.text.strip():
                    text += p.text + "\n"
                    
            elif block.tag.endswith('}tbl'):  # Si el bloque es una tabla (w:tbl)
                table = docx.table.Table(block, doc)
                for row in table.rows:
                    # Extraer el texto de cada celda, limpiarlo y unirlo con separadores (|)
                    row_data = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
                    text += "| " + " | ".join(row_data) + " |\n"
                text += "\n"  # Salto de línea al terminar la tabla
                
    elif filename.endswith('.pdf'):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                # layout=True ayuda a respetar los espacios visuales y tablas en los PDF
                extracted = page.extract_text(layout=True) 
                if extracted:
                    text += extracted + "\n"
                    
    return text