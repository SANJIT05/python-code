import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

# Set up Flask app
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
EXTRACT_FOLDER = 'output'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create a function to handle PDF extraction
def extract_text_and_images(pdf_path, extract_dir):
    doc = fitz.open(pdf_path)
    text_dir = os.path.join(extract_dir, "extracted_text")
    images_dir = os.path.join(extract_dir, "extracted_images")
    
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        text_file_path = os.path.join(text_dir, f"page_{page_num+1}.txt")
        with open(text_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_name = f"image_page{page_num+1}_{img_index+1}.{image_ext}"
            image_path = os.path.join(images_dir, image_name)
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
    
    return text_dir, images_dir

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extract_dir = os.path.join(EXTRACT_FOLDER, f"extraction_{timestamp}")
        text_dir, images_dir = extract_text_and_images(file_path, extract_dir)

        return redirect(url_for('show_extracted', text_dir=text_dir, images_dir=images_dir))

@app.route('/extracted')
def show_extracted():
    text_dir = request.args.get('text_dir')
    images_dir = request.args.get('images_dir')

    # Collect text and images for display
    texts = []
    images = []

    for file in sorted(os.listdir(text_dir)):
        with open(os.path.join(text_dir, file), 'r', encoding='utf-8') as f:
            texts.append((file, f.read()))

    for img_file in sorted(os.listdir(images_dir)):
        images.append(img_file)

    return render_template('extracted.html', texts=texts, images=images, images_dir=images_dir)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(EXTRACT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
