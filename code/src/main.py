import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from models.email_request import EmailRequest

from services.email_extraction import (
    extract_email_content_with_nlp,
    extract_contextual_data,
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
async def classify_email(request: EmailRequest):
    try:
        file_path = request.file_path
        sender = request.sender

        user_disputes_duplicate = (
            request.user_disputes_duplicate
            if hasattr(request, "user_disputes_duplicate")
            else False
        )

        email_text, attachment_text = extract_email_content_with_nlp(file_path)
        print(email_text, attachment_text)
        extracted_context = extract_contextual_data(email_text, attachment_text)
        subject = extracted_context.get("subject", "Unknown Subject")

        predefined_categories = request.predefined_categories or {}
        priority_rules = request.priority_rules or {
            "content_weightage": 0.7,
            "attachment_weightage": 0.3,
            "keywords_priority": {},
        }

        is_duplicate, duplicate_id, score = check_duplicate_email(email_text)
        print(user_disputes_duplicate)
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
            sender,
            subject,
            priority_rules,
            predefined_categories,
        )
        store_email_in_elasticsearch(
            email_text, attachment_text, sender, subject, classification
        )

        response = {
            "classification": classification,
            "is_duplicate": False,
            "extracted_context": extracted_context,
            "email_content": email_text,
            "attachment_content": attachment_text,
        }
        return response

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
