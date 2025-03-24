import uvicorn
import json
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, File, UploadFile, Form


from models.email_request import EmailRequest

from services.email_extraction import (
    # extract_email_content_with_nlp,
    # extract_contextual_data,
    extract_pdf_content_with_fitz,
    extract_attachments_from_eml,
    extract_docx_content,
    extract_email_body_and_subject,
)
from services.classification import classify_with_gemini
from services.duplicate_detection import (
    check_duplicate_email,
    store_email_in_elasticsearch,
)

# from services import (
#     extract_email_content_with_nlp,
#     classify_with_gemini,
#     check_duplicate_email,
#     store_email_in_elasticsearch,
#     extract_contextual_data,
# )

app = FastAPI()


@app.post("/classify_email")
async def classify_email(request_data: str = Form(...), file: UploadFile = File(...)):
    try:
        request_dict = json.loads(request_data)

        request = EmailRequest(**request_dict)

        eml_content = await file.read()
        # print(content)
        attachments = extract_attachments_from_eml(eml_content)

        attachment_texts = []
        # Print or process the extracted attachments
        for attachment in attachments:
            if attachment["filename"].lower().endswith(".pdf"):
                # Extract text from the PDF file using fitz
                pdf_text = extract_pdf_content_with_fitz(attachment["content"])
                attachment_texts.append(
                    {"filename": attachment["filename"], "content": pdf_text}
                )

            elif attachment["filename"].lower().endswith(".docx"):
                # Extract text from the .docx file using python-docx
                docx_text = extract_docx_content(attachment["content"])
                attachment_texts.append(
                    {"filename": attachment["filename"], "content": docx_text}
                )

            print(
                f"Attachment: {attachment['filename']} (size: {len(attachment['content'])} bytes)"
            )

        print(extract_email_body_and_subject(eml_content).get("subject"))

        # file_path = request.file_path
        sender = request.sender

        user_disputes_duplicate = (
            request.user_disputes_duplicate
            if hasattr(request, "user_disputes_duplicate")
            else False
        )

        # email_text, attachment_text = extract_email_content_with_nlp(file_path)
        email_text = extract_email_body_and_subject(eml_content).get("body")
        subject = extract_email_body_and_subject(eml_content).get("subject")
        attachment_text = " ".join(
            [attachment["content"] for attachment in attachment_texts]
        )

        predefined_categories = request.predefined_categories or {}
        priority_rules = request.priority_rules or {
            "content_weightage": 0.7,
            "attachment_weightage": 0.3,
            "keywords_priority": {},
        }

        is_duplicate, duplicate_id, score = check_duplicate_email(
            email_text + "\n" + attachment_text,
        )

        if is_duplicate and not user_disputes_duplicate:
            return {
                "message": "Duplicate email detected",
                "is_duplicate": True,
                "reason": "Similar content found in Elasticsearch",
                "duplicate_email_id": duplicate_id,
                "score": score,
            }

        classification = classify_with_gemini(
            email_text,
            attachment_text,
            subject,
            sender,
            priority_rules,
            predefined_categories,
        )
        store_email_in_elasticsearch(
            email_text + "\n" + attachment_text,
            sender,
            subject,
            classification,
        )

        response = {
            "classification": classification.get("classification", None),
            "is_duplicate": False,
            "extracted_context": classification.get("key_entities", None),
            "email_content": email_text,
            "attachment_content": attachment_text,
        }
        return response

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
