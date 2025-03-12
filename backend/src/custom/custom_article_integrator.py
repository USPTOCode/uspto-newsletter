import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml
from pathlib import Path
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CustomArticleIntegrator:
    """
    Manages custom articles for the newsletter, including fetching metadata,
    generating descriptions, and prioritizing them in the newsletter.
    """
    
    def __init__(self, custom_articles_file: str = None):
        """Initialize with an optional path to a custom articles file."""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='article_integrator.log'
        )
        self.logger = logging.getLogger('CustomArticleIntegrator')
        
        # Set up file path for custom articles
        self.custom_articles_file = custom_articles_file or os.path.join(
            os.getcwd(), 'data', 'custom_articles.yaml')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.custom_articles_file), exist_ok=True)
        
        # Initialize OpenAI client for generating descriptions
        api_key = os.getenv('OPENAI_API_KEY')
        self.openai_client = OpenAI(api_key=api_key) if api_key else None
        if not self.openai_client:
            self.logger.warning("OpenAI API key not found, description generation will be unavailable")
            
    def load_custom_articles(self) -> List[Dict[str, Any]]:
        """Load custom articles from the YAML file."""
        try:
            if not os.path.exists(self.custom_articles_file):
                self.logger.info(f"Custom articles file not found at {self.custom_articles_file}")
                return []
                
            with open(self.custom_articles_file, 'r') as file:
                data = yaml.safe_load(file)
                
            if not data or not isinstance(data, list):
                self.logger.warning("Invalid or empty custom articles file")
                return []
                
            self.logger.info(f"Loaded {len(data)} custom articles")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading custom articles: {e}")
            return []
            
    def save_custom_articles(self, articles: List[Dict[str, Any]]) -> bool:
        """Save custom articles to the YAML file."""
        try:
            with open(self.custom_articles_file, 'w') as file:
                yaml.dump(articles, file, default_flow_style=False)
                
            self.logger.info(f"Saved {len(articles)} custom articles to {self.custom_articles_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving custom articles: {e}")
            return False
            
    def add_custom_article(self, url: str, title: str = None, 
                          description: str = None, priority: int = 1) -> bool:
        """
        Add a custom article to the list.
        
        Args:
            url: The URL of the article
            title: Optional title (if not provided, will be fetched or generated)
            description: Optional description (if not provided, will be generated)
            priority: Priority level (1-5, with 1 being highest)
            
        Returns:
            bool: Success status
        """
        try:
            # Load existing articles
            articles = self.load_custom_articles()
            
            # Check if URL already exists
            for article in articles:
                if article.get('url') == url:
                    self.logger.warning(f"Article with URL {url} already exists")
                    return False
                    
            # Add new article
            new_article = {
                'url': url,
                'title': title or "",
                'description': description or "",
                'priority': min(max(1, priority), 5),
                'added_date': datetime.now().isoformat(),
                'included_in_newsletter': False
            }
            
            articles.append(new_article)
            
            # Save updated list
            return self.save_custom_articles(articles)
            
        except Exception as e:
            self.logger.error(f"Error adding custom article: {e}")
            return False
            
    async def fetch_article_metadata(self, url: str) -> Dict[str, Any]:
        """Fetch metadata (title, description) from an article URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        self.logger.warning(f"Failed to fetch URL {url}: {response.status}")
                        return {'title': '', 'description': ''}
                        
                    html = await response.text()
                    
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = ''
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
                
            # Extract description
            description = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and 'content' in meta_desc.attrs:
                description = meta_desc['content'].strip()
                
            # If no description found, use the first paragraph
            if not description:
                first_p = soup.find('p')
                if first_p:
                    description = first_p.text.strip()
                    
            # Limit description length
            if description and len(description) > 200:
                description = description[:197] + '...'
                
            return {
                'title': title,
                'description': description
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching metadata for {url}: {e}")
            return {'title': '', 'description': ''}
            
    async def generate_description(self, url: str, title: str, existing_desc: str = '') -> str:
        """
        Generate an engaging description for an article using OpenAI.
        Falls back to the existing description if generation fails.
        """
        if not self.openai_client:
            self.logger.warning("OpenAI client not available, cannot generate description")
            return existing_desc
            
        try:
            # Create a prompt for description generation
            prompt = f"""Write a brief, engaging description (2-3 sentences) for the following article 
            that would appeal to data enthusiasts:
            
            Title: {title}
            URL: {url}
            """
            
            if existing_desc:
                prompt += f"\nExisting description: {existing_desc}"
                
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a skilled editor writing concise, engaging article descriptions for a data science newsletter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            # Extract and clean up the generated description
            generated_desc = response.choices[0].message.content.strip()
            
            # Remove quotes if present
            if generated_desc.startswith('"') and generated_desc.endswith('"'):
                generated_desc = generated_desc[1:-1]
                
            self.logger.info(f"Generated description for article: {title}")
            return generated_desc
            
        except Exception as e:
            self.logger.error(f"Error generating description: {e}")
            return existing_desc or "An interesting article for data enthusiasts."
            
    async def process_custom_articles(self) -> List[Dict[str, Any]]:
        """
        Process all custom articles:
        1. Fetch missing metadata
        2. Generate descriptions if needed
        3. Mark as processed
        """
        try:
            # Load articles
            articles = self.load_custom_articles()
            if not articles:
                return []
                
            updated_articles = []
            for article in articles:
                url = article.get('url', '')
                if not url:
                    continue
                    
                # Skip articles that have been included in a newsletter
                if article.get('included_in_newsletter', False):
                    updated_articles.append(article)
                    continue
                    
                # Fetch metadata if title is missing
                if not article.get('title'):
                    metadata = await self.fetch_article_metadata(url)
                    article['title'] = metadata['title']
                    # Only update description if none exists
                    if not article.get('description'):
                        article['description'] = metadata['description']
                        
                # Generate description if needed
                if not article.get('description') or len(article.get('description', '')) < 10:
                    article['description'] = await self.generate_description(
                        url, article.get('title', 'Untitled Article'), article.get('description', '')
                    )
                    
                updated_articles.append(article)
                
            # Save updated articles
            self.save_custom_articles(updated_articles)
            
            # Return articles sorted by priority
            return sorted(
                [a for a in updated_articles if not a.get('included_in_newsletter', False)],
                key=lambda x: x.get('priority', 5)
            )
            
        except Exception as e:
            self.logger.error(f"Error processing custom articles: {e}")
            return []
            
    def mark_as_included(self, urls: List[str]) -> None:
        """Mark articles as included in the newsletter."""
        try:
            articles = self.load_custom_articles()
            for article in articles:
                if article.get('url') in urls:
                    article['included_in_newsletter'] = True
                    article['newsletter_date'] = datetime.now().isoformat()
                    
            self.save_custom_articles(articles)
            self.logger.info(f"Marked {len(urls)} articles as included in newsletter")
            
        except Exception as e:
            self.logger.error(f"Error marking articles as included: {e}")
            
    def format_custom_articles(self, articles: List[Dict[str, Any]]) -> str:
        """Format custom articles for the newsletter."""
        if not articles:
            return ""
            
        content = "## Editor's Picks\n\n"
        content += "_Handpicked articles our team found valuable:_\n\n"
        
        for article in articles:
            title = article.get('title', 'Interesting Article')
            url = article.get('url', '#')
            description = article.get('description', 'An article selected by our editorial team.')
            
            content += f"- **[{title}]({url})**\n"
            content += f"  {description}\n\n"
            
        return content

    def format_custom_articles_html(self, articles: List[Dict[str, Any]]) -> str:
        """Format custom articles as HTML for the newsletter."""
        if not articles:
            return ""
            
        html = "<h2>Editor's Picks</h2>\n"
        html += "<p><em>Handpicked articles our team found valuable:</em></p>\n<ul>\n"
        
        for article in articles:
            title = article.get('title', 'Interesting Article')
            url = article.get('url', '#')
            description = article.get('description', 'An article selected by our editorial team.')
            
            html += f'<li><strong><a href="{url}">{title}</a></strong><br>\n'
            html += f"<p>{description}</p></li>\n"
            
        html += "</ul>\n"
        return html


# Example custom_articles.yaml format:
"""
- url: https://example.com/article1
  title: Example Article 1
  description: This is a custom article about data science
  priority: 1
  added_date: '2025-03-01T12:00:00'
  included_in_newsletter: false

- url: https://example.com/article2
  title: Example Article 2
  priority: 2
  added_date: '2025-03-02T14:30:00'
  included_in_newsletter: false
"""

# Example usage
"""
async def main():
    integrator = CustomArticleIntegrator()
    
    # Add a custom article
    integrator.add_custom_article(
        url="https://example.com/new-article",
        title="Amazing New Data Tool",
        priority=1
    )
    
    # Process articles
    processed_articles = await integrator.process_custom_articles()
    
    # Format for newsletter
    formatted_content = integrator.format_custom_articles(processed_articles)
    
    # After including in newsletter, mark as processed
    included_urls = [article['url'] for article in processed_articles[:2]]
    integrator.mark_as_included(included_urls)

if __name__ == "__main__":
    asyncio.run(main())
"""