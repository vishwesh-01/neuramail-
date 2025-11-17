import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI( model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY, temperature=0 )


class EmailPriorityAnalysis(BaseModel):
    summary: str = Field(description="Brief summary of the main topic in the email")
    category: str = Field(description="based on the primary intent of the email. Classify it as 'Work Progress, Security Alerts, Account Management, Educational Notifications, Job Opportunities, Promotions, Payment Notifications, Personal Communications, Technical Support, Compliance, and Others' to reflect its core purpose and content")
    from_: str = Field(description="person or organization send the email")
    urgency: str = Field(description="Priority level based on urgency and impact: 'high', 'medium', or 'low'")

analysis_prompt = ChatPromptTemplate.from_template("""
You're assisting a professional by analyzing incoming emails. Extract the most relevant insights and assign a priority level.
Instructions:
- Summarize the main topic or request described in the email in a clear and concise manner.
- Classify the email into one of the following categories based on its primary purpose:
  - Work Progress
  - Security Alerts
  - Account Management
  - Educational Notifications
  - Job Opportunities
  - Promotions
  - Payment Notifications
  - Personal Communications
  - Technical Support
  - Compliance
  - Others
- Identify the sender (person or organization) from whom the email was received.
- Determine the urgency of the email based on its content:
  - Use 'high' if the message includes complaints, system failures, urgent requests, or time-sensitive issues.
  - Use 'medium' if the email contains important but non-urgent inquiries, business updates, or general feedback.
  - Use 'low' if the email is routine, contains general praise, or does not require immediate action.

Email:
{email}

Output Format:
```json
{{
  "summary": "Brief summary of the email",
  "category": "Email category (Work Progress, Security Alerts, Account Management, Educational Notifications, Job Opportunities, Promotions, Payment Notifications, Personal Communications, Technical Support, Compliance, or Others)",
  "from_": "Name or email of the sender",
  "urgency": "high | medium | low"
}}
""")

single_email_chain = analysis_prompt | llm | JsonOutputParser()
# import time

# results = []
# for i, email in enumerate(emails):
#     print(f"Processing email {i+1}/{len(emails)}...")
#     result = single_email_chain.invoke({"email": email})
#     print("=" * 60)
#     print(result)  # Print immediately after processing each email
#     results.append(result)
#     time.sleep(60)

def classify_emails(emails):
    results = single_email_chain.batch([{"email": email} for email in emails])
    return results
    # # Print results
    # for i, res in enumerate(results):
    #     print(f"Email {i + 1} analysis:")
    #     print(res)
    #     print("=" * 50)