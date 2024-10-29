import fitz  # PyMuPDF
import os
from PIL import Image
import io

# Create directories for saving the text and images
text_dir = "extracted_text"
images_dir = "extracted_images"

os.makedirs(text_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

def extract_text_and_images(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # Initialize variables to store the extracted text
    text_output = ""

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Get each page

        # Extract text from the page
        text = page.get_text("text")
        text_output += f"--- Page {page_num + 1} ---\n"
        text_output += text + "\n\n"

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

    # Save the extracted text to a text file
    text_file_path = os.path.join(text_dir, "extracted_text.txt")
    with open(text_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(text_output)

    print(f"Text and images have been extracted to '{text_dir}' and '{images_dir}'")

# Usage example
pdf_file = "sample.pdf"  # Replace with your PDF file path
extract_text_and_images(pdf_file)
