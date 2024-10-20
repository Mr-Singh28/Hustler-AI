import os
from dotenv import load_dotenv
import openai
import requests
from .brand_research import categorize_emails

# Load environment variables
load_dotenv()

# Set up API keys
openai.api_key = os.getenv('OPENAI_API_KEY')
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')

def get_enhanced_similar_brands(brand_name):
    """
    Use OpenAI to generate similar brands
    """
    prompt = f"List 5 companies similar to {brand_name} in the same industry. Provide the response as a comma-separated list."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides information about companies and industries."},
            {"role": "user", "content": prompt}
        ]
    )
    
    similar_brands = response.choices[0].message['content'].strip().split(', ')
    return similar_brands[:5]  # Ensure we only return 5 brands

def get_industry(brand_name):
    """
    Use OpenAI to determine the industry of a brand
    """
    prompt = f"What industry is {brand_name} primarily operating in? Provide a one-word answer."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides information about companies and industries."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message['content'].strip()

def find_company_emails(domain):
    """
    Use Hunter.io to find email addresses for a company
    """
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if 'data' in data and 'emails' in data['data']:
        return categorize_emails(data['data']['emails'])
    else:
        return {}

def generate_tailored_email(user_company_info, recipient_company, outreach_goal, cta):
    """
    Use OpenAI to generate a tailored email
    """
    prompt = f"""
    Create a professional outreach email with the following details:
    - Sender's company: {user_company_info}
    - Recipient company: {recipient_company}
    - Outreach goal: {outreach_goal}
    - Call to Action: {cta}

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

def enhanced_research_brand(brand_name, user_company_info, outreach_goal, cta):
    """
    Main function to perform enhanced brand research
    """
    results = {}
    similar_brands = get_enhanced_similar_brands(brand_name)
    results[brand_name] = {
        'similar_brands': similar_brands,
        'industry': get_industry(brand_name)
    }

    for brand in similar_brands:
        # Fix: Use double quotes for the f-string to avoid issues with apostrophes
        domain = f"www.{brand.lower().replace(' ', '').replace('''', '')}.com"
        emails = find_company_emails(domain)
        tailored_email = generate_tailored_email(user_company_info, brand, outreach_goal, cta)
        results[brand] = {
            'domain': domain,
            'emails': emails,
            'tailored_email': tailored_email
        }

    return results