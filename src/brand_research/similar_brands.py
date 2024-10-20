# src/brand_research/similar_brands.py

import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

def search_similar_brands(brand_name):
    """
    Search for brands similar to the given brand name.
    """
    # Use SerpAPI to search for similar brands
    url = f"https://serpapi.com/search.json?q=brands+similar+to+{brand_name}&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    data = response.json()
    
    # Extract organic results
    similar_brands = [result['title'] for result in data.get('organic_results', [])[:5]]
    return similar_brands

def find_company_website(brand_name):
    """
    Find the official website for a given brand name.
    """
    # Use SerpAPI to search for the brand's website
    url = f"https://serpapi.com/search.json?q={brand_name}+official+website&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    data = response.json()
    
    # Extract the first organic result as the official website
    if data.get('organic_results'):
        return data['organic_results'][0]['link']
    return None

def scrape_emails(url):
    """
    Scrape email addresses from a given URL.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all email addresses on the page
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_regex, soup.text)
        
        return emails
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return []

def categorize_emails(emails):
    """
    Attempt to categorize emails based on common patterns.
    """
    categorized = {
        'ceo': None,
        'cmo': None,
        'cfo': None,
        'marketing': None,
        'general': []
    }
    
    for email in emails:
        lower_email = email.lower()
        if 'ceo' in lower_email:
            categorized['ceo'] = email
        elif 'cmo' in lower_email or 'marketing' in lower_email:
            categorized['cmo'] = email
        elif 'cfo' in lower_email or 'finance' in lower_email:
            categorized['cfo'] = email
        elif 'marketing' in lower_email:
            categorized['marketing'] = email
        else:
            categorized['general'].append(email)
    
    return categorized

def research_brand(brand_name):
    """
    Main function to research a brand, find similar brands, and their email addresses.
    """
    results = {}
    
    # Find similar brands
    similar_brands = search_similar_brands(brand_name)
    results[brand_name] = {'similar_brands': similar_brands}
    
    # Research each similar brand
    for brand in similar_brands:
        website = find_company_website(brand)
        if website:
            emails = scrape_emails(website)
            categorized_emails = categorize_emails(emails)
            results[brand] = {
                'website': website,
                'emails': categorized_emails
            }
    
    return results

# Example usage
if __name__ == "__main__":
    brand_to_research = input("Enter a brand name to research: ")
    results = research_brand(brand_to_research)
    print(results)