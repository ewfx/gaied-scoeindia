from elasticsearch import Elasticsearch
import os
from google import genai
import json
from google.genai import types

cloud_id = os.environ.get("CLOUD_ID")
api_key = os.environ.get("ELASTIC_API_KEY")
es = Elasticsearch(
    cloud_id=cloud_id,
    api_key=api_key,
)

SIMILARITY_THRESHOLD = 0.9


def generate_embeddings_gemini(email_text):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    result = client.models.embed_content(
        model="text-embedding-004",
        contents=email_text,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
    )

    return result.embeddings[0].values


def get_elasticsearch_vector(email_text):
    """
    Use Elasticsearch's built-in text embedding model to generate a vector for the email text.

    :param email_text: The email content as a string
    :return: A dense vector representation of the text
    """
    response = es.ingest.simulate(
        id="text_embedding_pipeline",
        docs=[{"_source": {"text_field": email_text}}],
    )

    if "docs" in response and response["docs"]:
        return response["docs"][0]["doc"]["_source"]["text_embedding"][
            "predicted_value"
        ]
    return None


def check_duplicate_email(email_text):
    """
    Check if an email is a duplicate based on vector similarity.

    :param email_text: The email content as a string
    :return: (is_duplicate, matched_doc_id, similarity_score)
    """
    email_vector = generate_embeddings_gemini(email_text)
    if email_vector is None:
        return False, None, None

    query = {
        "size": 1,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",
                    "params": {"query_vector": email_vector},
                },
            }
        },
    }

    response = es.search(index="emails", body=query)

    if response["hits"]["total"]["value"] > 0:
        top_hit = response["hits"]["hits"][0]
        similarity_score = (top_hit["_score"]) / 2  # Normalize to 0-1
        print(">>>", similarity_score)
        if similarity_score > SIMILARITY_THRESHOLD:
            return True, top_hit["_id"], similarity_score

    return False, None, None


def store_email_in_elasticsearch(email_text, sender, subject, classification):
    """
    Convert email text to vector using Elasticsearch embeddings and store in Elasticsearch.

    :param email_text: The email content as a string
    :param sender: Sender of the email
    :param subject: Subject of the email
    :param classification: Classification of the email
    """
    email_vector = generate_embeddings_gemini(email_text)
    if email_vector is None:
        raise ValueError("Failed to generate vector for the email text.")

    doc = {
        "content_vector": email_vector,  # Store the generated vector
        "sender": sender,
        "subject": subject,
        "classification": classification,
    }
    es.index(index="emails", document=doc)
