import asyncio
import os
from datetime import datetime
from pathlib import Path
import sys

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)  # go up 1 parent from scripts to backend
sys.path.append(project_root)


from src.agent.newsletter_agent import NewsletterAgent
from src.integrator.newsletter_integrator import NewsletterIntegrator

async def main():
    try:
        # Initialize components
        print("Initializing newsletter generation...")
        integrator = NewsletterIntegrator()
        
        # Generate newsletter
        print("Generating newsletter content...")
        newsletter = await integrator.generate_newsletter()
        
        # Create filename with current date
        date_str = datetime.now().strftime('%Y_%m')
        
        # Save in multiple formats
        print("Saving newsletter in multiple formats...")
        html_path = integrator.save_newsletter_as(newsletter, 'html', f'newsletters/{date_str}.html')
        # md_path = integrator.save_newsletter_as(newsletter, 'markdown', f'newsletters/{date_str}.md')
        
        print(f"\nNewsletter generated successfully!")
        print(f"HTML version: {html_path}")
        # print(f"Markdown version: {md_path}")
        print("\nNext steps:")
        print("1. Review the generated files")
        print("2. Commit and push to GitHub:")
        print(f"   git add newsletters/{date_str}.*")
        print(f"   git commit -m \"Add {datetime.now().strftime('%B %Y')} newsletter\"")
        print("   git push origin main")
        print("3. Send to subscribers via MailOctopus")
        
    except Exception as e:
        print(f"Error generating newsletter: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())