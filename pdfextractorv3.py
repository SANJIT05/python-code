import fitz  # PyMuPDF
import os
from datetime import datetime

def create_output_folders(base_dir="output"):
    # Get current timestamp to ensure unique directory names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a parent directory with a timestamp
    parent_dir = os.path.join(base_dir, f"extraction_{timestamp}")
    text_dir = os.path.join(parent_dir, "extracted_text")
    images_dir = os.path.join(parent_dir, "extracted_images")
    
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    return text_dir, images_dir, parent_dir

def extract_text_and_images(pdf_path, base_dir="output"):
    # Create output directories
    text_dir, images_dir, parent_dir = create_output_folders(base_dir)
    
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Get each page

        # Extract text from the page
        text = page.get_text("text")
        
        # Save the text of each page in a separate file
        text_file_path = os.path.join(text_dir, f"page_{page_num+1}.txt")
        with open(text_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

        # Extract images from the page
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Get the image format (e.g., png, jpeg)
            image_ext = base_image["ext"]

            # Create image file name
            image_name = f"image_page{page_num+1}_{img_index+1}.{image_ext}"

            # Save the image
            image_path = os.path.join(images_dir, image_name)
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

    print(f"Text and images have been extracted to '{parent_dir}'")

# Usage example
pdf_file = "sample2.pdf"  # Replace with your PDF file path
extract_text_and_images(pdf_file)
