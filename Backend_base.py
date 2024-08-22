import os
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import cv2
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
from selenium import webdriver

# Convert PDF to Image
def pdf_to_image(pdf_path, image_path):
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        image_file_path = os.path.join(image_path, f"page_{i + 1}.png")
        image.save(image_file_path, "PNG")
    return os.path.join(image_path, "page_1.png")

# Extract text using OCR from an image
def extract_text_from_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

# Detect QR code from the image
def detect_qr_code(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    decoded_objects = decode(gray_image)
    url = ""
    for obj in decoded_objects:
        url = obj.data.decode('utf-8')
        break  # Assuming there's only one QR code to detect
    return url

# Take a screenshot of the webpage
def take_screenshot(url, save_path, width=2500, height=1500):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.set_window_size(width, height)
        driver.get(url)
        driver.save_screenshot(save_path)
    except Exception as e:
        print(f"Error taking screenshot: {e}")
    finally:
        driver.quit()

# Main Verification Process
def verify_certificate(pdf_file_path, image_output_path, screenshot_path):
    # Step 1: Convert PDF to Image and extract text
    pdf_image_path = pdf_to_image(pdf_file_path, image_output_path)
    pdf_text = extract_text_from_image(pdf_image_path)

    # Step 2: Detect QR code and extract the URL
    qr_code_url = detect_qr_code(pdf_image_path)
    if not qr_code_url:
        print("No QR code detected.")
        return
    
    # Step 3: Take a screenshot from the QR code URL and extract text
    take_screenshot(qr_code_url, screenshot_path)
    screenshot_text = extract_text_from_image(screenshot_path)

    # Step 4: Compare details (name, marks) between the PDF and screenshot
    name_in_pdf = extract_detail_from_text(pdf_text, "Name")  # Example: Extracting Name
    marks_in_pdf = extract_detail_from_text(pdf_text, "Marks")  # Example: Extracting Marks

    name_in_screenshot = extract_detail_from_text(screenshot_text, "Name")
    marks_in_screenshot = extract_detail_from_text(screenshot_text, "Marks")
    print("details:\n",name_in_pdf,name_in_screenshot,marks_in_pdf,marks_in_screenshot)
    if name_in_pdf == name_in_screenshot and marks_in_pdf == marks_in_screenshot:
        print("\nVerification successful: The name and marks match!")
    else:
        print("\nVerification failed: The details do not match.")

# Helper function to extract specific details from text (modify as needed)
def extract_detail_from_text(text, detail_name):
    for line in text.split('\n'):
        if detail_name.lower() in line.lower():
            return line.split(':')[-1].strip()  # Assuming the format is "Detail: Value"
    return None

if __name__ == "__main__":
    pdf_file_path = "dataset/185001003_Deep Learning_E-certificate - Aarthi V S.pdf"
    image_output_path = "certificate"
    screenshot_path = "screenshot.png"

    if not os.path.exists(image_output_path):
        os.makedirs(image_output_path)

    verify_certificate(pdf_file_path, image_output_path, screenshot_path)
