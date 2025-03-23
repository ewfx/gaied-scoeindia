import os
import pytesseract
import fitz  # PyMuPDF for PDF processing
from pdf2image import convert_from_path
from docx import Document
from unstructured.partition.email import partition_email
import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_eml(eml_path):
    elements = partition_email(filename=eml_path)
    return "\n".join(str(element) for element in elements)


def extract_text_with_ocr(pdf_path):
    print(pdf_path)
    text = ""

    # images = convert_from_path(pdf_path)
    # print(images)
    # for image in images:
    #     print(image)
    #     text += pytesseract.image_to_string(image) + "\n"
    # print(text)

    return text.strip()


def extract_email_content_with_nlp(file_path):
    ext = file_path.split(".")[-1].lower()
    email_content, attachment_content = "", ""

    if ext == "pdf":
        email_content = extract_text_from_pdf(file_path)
        attachment_content = extract_text_with_ocr(file_path)
    elif ext == "docx":
        email_content = extract_text_from_docx(file_path)
    elif ext == "eml":
        email_content = extract_text_from_eml(file_path)

    return email_content, attachment_content


def extract_contextual_data(email_content, attachment_content):
    combined_text = email_content + "\n" + attachment_content
    doc = nlp(combined_text)

    extracted_data = {
        "deal_name": "Not Found",
        "amount": "Not Found",
        "expiration_date": "Not Found",
        "subject": "Unknown Subject",
    }

    for ent in doc.ents:
        if ent.label_ == "MONEY":
            extracted_data["amount"] = ent.text
        elif ent.label_ == "DATE":
            extracted_data["expiration_date"] = ent.text
        elif "deal" in ent.text.lower():
            extracted_data["deal_name"] = ent.text

    return extracted_data
