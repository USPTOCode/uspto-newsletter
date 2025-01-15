import pytest
import asyncio
import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from src.agent.newsletter_agent import NewsletterAgent

@pytest.fixture
def agent():
    """Fixture to create and return a NewsletterAgent instance."""
    return NewsletterAgent()

@pytest.fixture
def sample_data():
    """Fixture with sample data for testing content generation."""
    return {
        'papers': [
            {
                'title': 'Test Paper',
                'summary': 'A test paper about data science',
                'authors': ['Test Author'],
                'link': 'http://example.com/paper',
                'published': '2025-01-13'
            }
        ],
        'blog_posts': [
            {
                'title': 'Test Blog Post',
                'summary': 'A test blog post about data analysis',
                'link': 'http://example.com/blog',
                'source': 'Test Blog',
                'published': 'Mon, 13 Jan 2025'
            }
        ],
        'github_projects': [
            {
                'name': 'test-project',
                'description': 'A test data science project',
                'url': 'http://github.com/test/project',
                'stars': 100,
                'language': 'Python'
            }
        ]
    }

@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test that the agent initializes correctly."""
    assert isinstance(agent, NewsletterAgent)
    assert agent.api_key is not None
    assert agent.client is not None

@pytest.mark.asyncio
async def test_arxiv_papers_fetch(agent):
    """Test fetching papers from arXiv."""
    papers = await agent.fetch_arxiv_papers()
    assert isinstance(papers, list)
    if papers:  # Only test structure if we got results
        paper = papers[0]
        assert isinstance(paper, dict)
        assert all(key in paper for key in ['title', 'summary', 'authors', 'link', 'published'])

@pytest.mark.asyncio
async def test_tech_blog_posts_fetch(agent):
    """Test fetching tech blog posts."""
    posts = await agent.fetch_tech_blog_posts()
    assert isinstance(posts, list)
    if posts:  # Only test structure if we got results
        post = posts[0]
        assert isinstance(post, dict)
        assert all(key in post for key in ['title', 'summary', 'link', 'source', 'published'])

@pytest.mark.asyncio
async def test_github_trends_fetch(agent):
    """Test fetching GitHub trends."""
    projects = await agent.fetch_github_trends()
    assert isinstance(projects, list)
    if projects:  # Only test structure if we got results
        project = projects[0]
        assert isinstance(project, dict)
        assert all(key in project for key in ['name', 'description', 'url', 'stars', 'language'])

@pytest.mark.asyncio
async def test_content_generation(agent, sample_data):
    """Test content generation using OpenAI."""
    content = agent.generate_section_content('emerging_trends', sample_data)
    assert isinstance(content, str)
    assert len(content) > 0

@pytest.mark.asyncio
async def test_newsletter_compilation(agent):
    """Test full newsletter compilation."""
    newsletter = await agent.compile_newsletter()
    assert newsletter is not None
    assert isinstance(newsletter, dict)
    assert all(key in newsletter for key in ['month', 'sections', 'metadata'])

@pytest.mark.asyncio
async def test_newsletter_save(agent, tmp_path):
    """Test saving newsletter to file."""
    newsletter = await agent.compile_newsletter()
    test_file = tmp_path / "test_newsletter.json"
    saved_file = agent.save_newsletter(newsletter, filename=str(test_file))
    assert saved_file is not None
    assert os.path.exists(test_file)

def test_environment_variables():
    """Test that required environment variables are set."""
    assert os.getenv('OPENAI_API_KEY') is not None, "OPENAI_API_KEY environment variable is not set"
    # GitHub token is optional but log if it's not set
    if not os.getenv('GITHUB_TOKEN'):
        print("Note: GITHUB_TOKEN is not set. GitHub API requests may be rate limited.")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])