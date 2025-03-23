from pydantic import BaseModel


class EmailRequest(BaseModel):
    file_path: str
    sender: str
    subject: str
    predefined_categories: dict = None
    priority_rules: dict = None
    user_disputes_duplicate: bool = False
