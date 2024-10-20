import os
from openai import OpenAI
import requests
from dotenv import load_dotenv
import logging
import json

# Load environment variables
load_dotenv()

# Set up API keys
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def get_similar_brands(brand_name):
    """
    Use OpenAI to generate similar brands and reasons for similarity.
    """
    prompt = f"List 5 companies similar to {brand_name} in the same industry. For each company, provide a brief reason why it's similar. Format the response as a Python list of dictionaries, each with 'company' and 'reason' keys."
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides information about companies and industries."},
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response: {content}")

        # Remove markdown code block syntax if present
        content = content.replace('```python', '').replace('```', '').strip()

        # Safely evaluate the string as a Python expression
        similar_brands = eval(content)
        
        if not isinstance(similar_brands, list):
            raise ValueError("Response is not a list")
        
        # Ensure each item is a dictionary with 'company' and 'reason' keys
        validated_brands = []
        for brand in similar_brands:
            if isinstance(brand, dict) and 'company' in brand and 'reason' in brand:
                validated_brands.append(brand)
            else:
                logger.warning(f"Skipping invalid brand data: {brand}")
        
        logger.info(f"Processed similar brands: {validated_brands}")
        return validated_brands[:5]  # Ensure we only return up to 5 brands
    except Exception as e:
        logger.error(f"Error in get_similar_brands: {str(e)}", exc_info=True)
        return []  # Return an empty list if there's an error


def get_industry(brand_name):
    """
    Use OpenAI to determine the industry of a brand
    """
    prompt = f"What industry is {brand_name} primarily operating in? Provide a one-word answer."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides information about companies and industries."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in get_industry: {str(e)}", exc_info=True)
        return "Unknown"

def find_company_emails(domain):
    """
    Use Hunter.io API to find email addresses for a company
    """
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'data' in data and 'emails' in data['data']:
            return data['data']['emails']
        else:
            return []
    except Exception as e:
        logger.error(f"Error in find_company_emails: {str(e)}", exc_info=True)
        return []

def generate_tailored_email(user_company_info, recipient_company, outreach_goal, desired_cta):
    """
    Use OpenAI to generate a tailored email
    """
    prompt = f"""
    Create a professional outreach email with the following details:
    - Sender's company information: {user_company_info}
    - Recipient company: {recipient_company}
    - Outreach goal: {outreach_goal}
    - Desired Call to Action: {desired_cta}
    The email should be concise, friendly, and tailored to the recipient company.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional email writer, crafting personalized outreach emails for business collaborations."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in generate_tailored_email: {str(e)}", exc_info=True)
        return "Error generating email"

def research_brand(brand_name, user_company_info, outreach_goal, desired_cta):
    logger.info(f"Starting research for brand: {brand_name}")
    results = {}
    try:
        similar_brands = get_similar_brands(brand_name)
        logger.info(f"Similar brands found: {similar_brands}")
        industry = get_industry(brand_name)
        logger.info(f"Industry determined: {industry}")
        results[brand_name] = {
            'similar_brands': similar_brands,
            'industry': industry
        }
        for brand in similar_brands:
            company_name = brand['company']
            logger.info(f"Processing similar brand: {company_name}")
            domain = f"www.{company_name.lower().replace(' ', '')}.com"
            emails = find_company_emails(domain)
            tailored_email = generate_tailored_email(user_company_info, company_name, outreach_goal, desired_cta)
            results[company_name] = {
                'domain': domain,
                'emails': emails,
                'tailored_email': tailored_email,
                'reason': brand['reason']
            }
        logger.info("Research completed successfully")
        return results
    except Exception as e:
        logger.error(f"Error during research: {str(e)}", exc_info=True)
        raise