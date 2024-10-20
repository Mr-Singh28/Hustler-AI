# src/email_campaign/email_campaign.py
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_email(sender_info, recipient_info):
    """
    Use OpenAI to generate a tailored email
    """
    prompt = f"""
    Create a professional outreach email with the following details:
    - Sender's company: {sender_info['brand']}
    - Sender's name: {sender_info['name']}
    - Sender's position: {sender_info['position']}
    - Sender's expertise: {sender_info['expertise']}
    - Recipient company: {recipient_info['brand']}
    - Recipient's industry: {recipient_info['industry']}
    
    The email should be concise, friendly, and tailored to the recipient company.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional email writer, crafting personalized outreach emails for business collaborations."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message['content'].strip()