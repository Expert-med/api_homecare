from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import json
import re
import io
import os

app = Flask(__name__)
CORS(app)

def extract_pdf_to_json(pdf_file):
    pdf_content = {
        "pages": []
    }
    
    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            pdf_content["pages"].append({
                "page_number": page_num,
                "text": text
            })
    
    return pdf_content

def extract_material(text):
    start_index = text.lower().find("rotina")
    
    if start_index == -1:
        return []
    
    material_text = text[start_index + len("rotina"):].strip()
    materials = [line.strip() for line in material_text.split('\n') if line.strip()]
    
    return materials

def filter_materials(materials):
    filtered_materials = []
    code_pattern = re.compile(r'^\d+ .*')
    
    for material in materials:
        if code_pattern.match(material):
            filtered_materials.append(material)
    
    return filtered_materials

def parse_material(material):
    # Regex para encontrar o código, nome, quantidade e tipo
    match = re.match(r'^(\d+)\s+(.+?)\s+(\d+)\s+(\w+)$', material)
    
    if match:
        cod = match.group(1)
        nome = match.group(2)
        quantidade = int(match.group(3))
        tipo = match.group(4)
        
        return {
            "cod": cod,
            "nome": nome,
            "quantidade": quantidade,
            "tipo": tipo
        }
    
    # Separar de trás para frente
    parts = material.rsplit(' ', 3)
    if len(parts) == 4:
        cod = parts[0]
        nome = " ".join(parts[1:-2])
        quantidade = int(parts[-2])
        tipo = parts[-1]
        
        return {
            "cod": cod,
            "nome": nome,
            "quantidade": quantidade,
            "tipo": tipo
        }
    
    return None

def format_json(pdf_content):
    formatted_materials = []
    
    for page in pdf_content['pages']:
        text = page['text']
        materials = extract_material(text)
        filtered_materials = filter_materials(materials)
        
        formatted_materials.extend([parse_material(material) for material in filtered_materials if parse_material(material) is not None])
    
    return {
        "prod": formatted_materials
    }

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        pdf_content = extract_pdf_to_json(io.BytesIO(file.read()))
        formatted_json = format_json(pdf_content)
        return jsonify(formatted_json)
    else:
        return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8083)))
