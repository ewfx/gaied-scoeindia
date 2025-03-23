from elasticsearch import Elasticsearch
import os

cloud_id = os.environ.get("CLOUD_ID")
api_key = os.environ.get("ELASTIC_API_KEY")
es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key,
)


def check_duplicate_email(email_text):
    query = {"query": {"match": {"content": email_text}}}
    response = es.search(index="emails", body=query)
    if response["hits"]["total"]["value"] > 0:
        return (
            True,
            response["hits"]["hits"][0]["_id"],
            response["hits"]["hits"][0]["_score"],
        )
    return False, None, 0


def store_email_in_elasticsearch(
    email_text, attachment_text, sender, subject, classification
):
    doc = {
        "content": email_text + "\n" + attachment_text,
        "sender": sender,
        "subject": subject,
        "classification": classification,
    }
    es.index(index="emails", document=doc)
