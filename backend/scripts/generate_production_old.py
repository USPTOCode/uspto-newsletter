import asyncio
import os
from datetime import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Debug print to verify
print(f"Using API Key: {os.getenv('OPENAI_API_KEY')[:6]}...")

from src.agent.newsletter_agent import NewsletterAgent
from src.integrator.newsletter_integrator import NewsletterIntegrator

async def main():
    try:
        print("Starting live newsletter generation...")
        
        # Initialize both agent and integrator
        print("Initializing components...")
        agent = NewsletterAgent()
        integrator = NewsletterIntegrator()
        
        # Use the agent to generate content
        print("Generating newsletter content using NewsletterAgent...")
        newsletter = await agent.compile_newsletter()
        
        # Save using the integrator
        print("Saving newsletter in multiple formats...")
        date_str = datetime.now().strftime('%Y_%m')
        html_path = integrator.save_newsletter_as(newsletter, 'html', f'newsletters/{date_str}.html')
        md_path = integrator.save_newsletter_as(newsletter, 'markdown', f'newsletters/{date_str}.md')
        
        print(f"\nNewsletter generated successfully!")
        print(f"HTML version: {html_path}")
        print(f"Markdown version: {md_path}")
        print("\nContent sources:")
        print(f"Papers: {newsletter['metadata']['source_counts']['papers']}")
        print(f"Blog posts: {newsletter['metadata']['source_counts']['blog_posts']}")
        print(f"GitHub projects: {newsletter['metadata']['source_counts']['github_projects']}")
        
    except Exception as e:
        print(f"Error generating newsletter: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())