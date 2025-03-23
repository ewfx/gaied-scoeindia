from google import genai
import json
from google.genai import types
import os

def remove_first_and_last_line(input_string):
    lines = input_string.splitlines()
    return "\n".join(lines[1:-1])  # Exclude the first and last lines

def classify_with_gemini(email_text, attachment_text, sender, priority_rules, predefined_categories):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.2,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text="""You are part of commercial bank lending service team, you have to classify the email/service request into the following request and sub request types if request and sub request types are not mentioned in user query.  There can be multiple classifications also. Also extract the key entities from the email in the given format. Output should be in a json array format like this. return in order of the confidence_score in descending order, the first should be the primary result having more score than others. Return 3 results if not user does not mention the number of results.
Return the output strictly in json in the following format:
```
{
    "classification":[{
        \"request_type\":\"\",
        \"sub_request_type\":\"\",
        \"confidence_score\":\"\"
    }],
    "key_entities":{
        "deal_name": "", // deal name if mentioned in mail
        "amount": "",  //transaction amount if mentioned in mail
        "expiration_date": "", //expiration date if mentioned in mail
        "subject": "", //subject of email
        // can add more key entities if found
    }
}
```

Use these Request and sub request types if not mentioend in  user query
```
I. Loan Adjustments & Changes:
* Adjustment:
    * Interest Rate Adjustment (Floating to Fixed, etc.)
    * Payment Schedule Adjustment
    * Covenant Adjustment
    * Loan Term Adjustment
* Commitment Change:
    * Commitment Increase
    * Commitment Decrease
    * Cashless Roll
    * Reallocation Principal
* Fee Adjustments:
    * Amendment Fee
    * Reallocation Fee
    * Late Payment Fee Waiver/Adjustment
    * Fee Dispute/Resolution
II. Account User (AU) & Access Management:
* AU Transfer:
    * Transfer of Account Ownership/Responsibility
    * Change of Authorized Signatories
    * User Access Modification (Add/Remove)
    * Online Banking Access Management
III. Loan Closure & Termination:
* Closing Notice:
    * Loan Payoff Notification
    * Account Closure Confirmation
    * Final Statement Generation
    * Sub Fee breakdowns.
        * reallocation fee
        * amendment fee
* Loan Termination:
    * Early Loan Termination.
    * Scheduled Loan Termination.
IV. Fee Management:
* Fee Payment:
    * Ongoing Fee Payment (e.g., annual maintenance)
    * Letter of Credit Fee Payment
    * Wire Transfer Fee Payment
    * Document Preparation Fee Payment
    * Loan syndication Fee.
V. Money Movement (Funds Transfer):
* Money Movement: Inbound:
    * Principal Payment
    * Interest Payment
    * Principal + Interest Payment
    * Principal + Interest + Fee Payment
    * Loan draw down.
* Money Movement: Outbound:
    * Time-Bound Transfer
    * Foreign Currency Transfer
    * Disbursement to Vendor/Third Party
    * Loan proceeds dispersal.
    * Escrow disbursement.
VI. Loan Documentation & Reporting:
* Document Requests:
    * Loan Agreement Copies
    * Security Agreement Copies
    * Compliance Certificates
    * Financial Statement Submissions
* Reporting:
    * Loan Balance Reports
    * Interest Accrual Reports
    * Payment History Reports
    * Custom Report Generation

VII. Specialized Requests:
* Letter of Credit (LC) Requests:
    * LC Issuance
    * LC Amendment
    * LC Payment
    * LC Cancellation.
* Trade Finance Requests:
    * Import Financing.
    * Export Financing.
    * Documentary Collections.
* Syndicated loan requests.
    * syndicate participant change.
    * syndicate information request.
    * syndicate payment distribution.
```"""
            ),
        ],
    )

    model = "gemini-2.0-flash"
    rules= None
    if(priority_rules):
        if(priority_rules.get("content_weightage")):
            rules = f"Weightage of 'Content' should be: {priority_rules.get('content_weightage')}\n"
        if(priority_rules.get("attachment_weightage")):
            rules += f"Weightage of 'Attachment' should be: {priority_rules.get('attachment_weightage')}\n"
        if(priority_rules.get("keywords_priority")):  
            rules += f"Weightage of following keywords should be: {priority_rules.get('keywords_priority')}"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""Classify This Email {"into these "+predefined_categories if predefined_categories else ""}-
                    Email:
                    ```
                    Sender: {sender}
                    Content: {email_text}
                    Attachment: {attachment_text}
                    ```
                    {"While evaluating, Follow these priority rules: \n"+rules if rules else ""}Return top 3 results.
                    """
                ),
            ],
        )
    ]


    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    return json.loads(remove_first_and_last_line(response.text))  # Ensure correct JSON parsing
