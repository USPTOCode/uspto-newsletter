import os
import logging
from datetime import datetime, timedelta
import requests
import feedparser
import arxiv
from bs4 import BeautifulSoup
from openai import OpenAI
from typing import Dict, List, Optional
import json

class NewsletterAgent:
    """Agent for gathering and generating newsletter content from external sources."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the newsletter agent with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the agent."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='agent.log'
        )
        self.logger = logging.getLogger('NewsletterAgent')

    async def fetch_arxiv_papers(self) -> List[Dict]:
        """Fetch relevant papers from arXiv."""
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query="data mining OR machine learning OR open data",
                max_results=5,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            results = client.results(search)  # Get results iterator
            for result in results:  # Use standard for loop
                papers.append({
                    'title': result.title,
                    'summary': result.summary,
                    'authors': [author.name for author in result.authors],
                    'link': result.pdf_url,
                    'published': result.published.strftime('%Y-%m-%d')
                })
            
            self.logger.info(f"Successfully fetched {len(papers)} papers from arXiv")
            return papers
            
        except Exception as e:
            self.logger.error(f"Error fetching arXiv papers: {e}")
            return []

    async def fetch_tech_blog_posts(self) -> List[Dict]:
        """Fetch posts from relevant tech blogs."""
        try:
            feeds = [
                'https://towardsdatascience.com/feed',
                'https://blogs.opendata.ch/feed/',
                'https://databricks.com/feed'
            ]
            
            posts = []
            for feed_url in feeds:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:2]:  # Get 2 most recent from each
                    posts.append({
                        'title': entry.title,
                        'summary': entry.summary,
                        'link': entry.link,
                        'source': feed.feed.title,
                        'published': entry.published
                    })
            
            self.logger.info(f"Successfully fetched {len(posts)} blog posts")
            return posts
            
        except Exception as e:
            self.logger.error(f"Error fetching blog posts: {e}")
            return []

    async def fetch_github_trends(self) -> List[Dict]:
        """Fetch trending open data and analysis projects from GitHub."""
        try:
            headers = {'Accept': 'application/vnd.github.v3+json'}
            if github_token := os.getenv('GITHUB_TOKEN'):
                headers['Authorization'] = f'token {github_token}'
            
            queries = [
                'open+data+tools',
                'data+analysis+framework',
                'machine+learning+pipeline'
            ]
            
            projects = []
            for query in queries:
                url = f"https://api.github.com/search/repositories"
                params = {
                    'q': f"{query}+language:python+created:>{datetime.now() - timedelta(days=30)}",
                    'sort': 'stars',
                    'order': 'desc'
                }
                
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    for repo in response.json()['items'][:3]:
                        projects.append({
                            'name': repo['name'],
                            'description': repo['description'],
                            'url': repo['html_url'],
                            'stars': repo['stargazers_count'],
                            'language': repo['language']
                        })
            
            self.logger.info(f"Successfully fetched {len(projects)} GitHub projects")
            return projects
            
        except Exception as e:
            self.logger.error(f"Error fetching GitHub trends: {e}")
            return []

    def generate_section_content(self, section_name: str, data: Dict) -> str:
        """Generate newsletter content for a section using OpenAI."""
        try:
            prompt = self._create_section_prompt(section_name, data)
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": """You are an expert data analyst creating content 
                    for the USPTO Open Data Enthusiasts newsletter. Focus on insights that would be 
                    valuable and novel for USPTO employees. Write in a professional but engaging tone."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating section content: {e}")
            return ""

    def _create_section_prompt(self, section_name: str, data: Dict) -> str:
        """Create specific prompts for different newsletter sections."""
        prompts = {
            'emerging_trends': f"""
            Create a section analyzing emerging trends in data science and analytics.
            Focus on these recent developments:
            
            Academic Papers:
            {json.dumps(data['papers'], indent=2)}
            
            Tech Blog Discussions:
            {json.dumps(data['blog_posts'], indent=2)}
            
            Write a cohesive analysis that:
            1. Identifies key trends and patterns
            2. Explains relevance to USPTO work
            3. Suggests potential applications
            4. Includes specific examples
            
            Format with clear subheadings and concise paragraphs.
            """,
            
            'tools_and_projects': f"""
            Create a section highlighting innovative data tools and projects.
            Based on these trending repositories:
            
            {json.dumps(data['github_projects'], indent=2)}
            
            Write a detailed analysis that:
            1. Describes each tool's key features
            2. Explains potential benefits for USPTO work
            3. Provides specific use cases
            4. Includes any setup or usage tips
            
            Format with clear subheadings and concise paragraphs.
            """,
            
            'learning_resources': f"""
            Create a section on learning opportunities and resources.
            Based on these materials:
            
            Blog Posts:
            {json.dumps(data['blog_posts'], indent=2)}
            
            Academic Papers:
            {json.dumps(data['papers'], indent=2)}
            
            Write a comprehensive guide that:
            1. Highlights key learning resources
            2. Suggests learning paths
            3. Provides practical next steps
            4. Includes specific skill development tips
            
            Format with clear subheadings and concise paragraphs.
            """
        }
        
        return prompts.get(section_name, "Generate relevant content for the newsletter section.")

    async def compile_newsletter(self) -> Dict:
        """Compile complete newsletter with all sections."""
        try:
            # Gather content from all sources
            papers = await self.fetch_arxiv_papers()
            blog_posts = await self.fetch_tech_blog_posts()
            github_projects = await self.fetch_github_trends()
            
            # Prepare data for content generation
            data = {
                'papers': papers,
                'blog_posts': blog_posts,
                'github_projects': github_projects
            }
            
            # Generate each section
            newsletter = {
                'month': datetime.now().strftime('%B %Y'),
                'sections': {
                    'emerging_trends': self.generate_section_content('emerging_trends', data),
                    'tools_and_projects': self.generate_section_content('tools_and_projects', data),
                    'learning_resources': self.generate_section_content('learning_resources', data)
                },
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'source_counts': {
                        'papers': len(papers),
                        'blog_posts': len(blog_posts),
                        'github_projects': len(github_projects)
                    }
                }
            }
            
            self.logger.info("Successfully compiled newsletter")
            return newsletter
            
        except Exception as e:
            self.logger.error(f"Error compiling newsletter: {e}")
            return None

    def save_newsletter(self, newsletter: Dict, filename: Optional[str] = None) -> str:
        """Save the newsletter to a JSON file."""
        try:
            if not filename:
                filename = f"newsletter_{datetime.now().strftime('%Y%m')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(newsletter, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Successfully saved newsletter to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving newsletter: {e}")
            return None

# Example usage
async def main():
    api_key = os.getenv('OPENAI_API_KEY')
    agent = NewsletterAgent(api_key)
    
    newsletter = await agent.compile_newsletter()
    if newsletter:
        agent.save_newsletter(newsletter)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())