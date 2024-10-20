# This is the main file that runs the entire process

from src.brand_research.brand_research import research_brand
from src.email_campaign.email_campaign import EmailCampaign

if __name__ == "__main__":
    # Ask the user for a brand to research
    brand_to_research = input("Enter a brand name to research: ")
    
    # Research the brand and similar brands
    results = research_brand(brand_to_research)
    
    print(f"\nResults for {brand_to_research}:")
    print(f"Industry: {results[brand_to_research]['industry']}")
    print("Similar brands:")
    
    # Initialize EmailCampaign
    # Note: Replace with your actual SMTP settings and credentials
    email_campaign = EmailCampaign('smtp.gmail.com', 587, 'your_email@gmail.com', 'your_password')
    
    # Create a campaign
    campaign_name = f"{brand_to_research} Outreach"
    email_campaign.create_campaign(campaign_name, [])
    
    # Process each similar brand
    for brand in results[brand_to_research]['similar_brands']:
        print(f"- {brand}")
        if brand in results:
            domain = results[brand]['domain']
            emails = results[brand]['emails']
            print(f"  Domain: {domain}")
            if any(emails.values()):
                print("  Emails found:")
                for category, email_data in emails.items():
                    if category != 'other' and email_data:
                        print(f"    {category.upper()}: {email_data['value']} ({email_data.get('position', 'Unknown position')})")
                        
                        # Generate email using OpenAI
                        sender_info = {
                            'name': 'Your Name',
                            'brand': brand_to_research,
                            'position': 'Marketing Director',
                            'expertise': 'Your Expertise'
                        }
                        recipient_info = {
                            'brand': brand,
                            'industry': results[brand_to_research]['industry']
                        }
                        email_content = email_campaign.generate_email(sender_info, recipient_info)
                        
                        if email_content:
                            print("\nGenerated Email:")
                            print(email_content)
                            
                            # Uncomment the following line to actually send emails (be careful!)
                            # email_campaign.send_email(campaign_name, email_data['value'], "Collaboration Opportunity", email_content)
                        
                if emails['other']:
                    print(f"    Other emails: {len(emails['other'])}")
            else:
                print("  No emails found")
        else:
            print("  No emails found")
        print()
    
    # Print campaign stats
    print("\nCampaign Stats:")
    print(email_campaign.get_campaign_stats(campaign_name))