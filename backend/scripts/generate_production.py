import asyncio
import os
import re
from datetime import datetime
from pathlib import Path
import sys
import markdown
from dotenv import load_dotenv
from jinja2 import Template

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Debug print to verify
print(f"Using API Key: {os.getenv('OPENAI_API_KEY')[:6]}...")

# Import our components
from src.agent.newsletter_agent import NewsletterAgent
from src.integrator.newsletter_integrator import NewsletterIntegrator
from src.curator.content_curator import ContentCurator
from src.templates.newsletter_template_manager import NewsletterTemplateManager
from src.free.free_content_fetcher import FreeContentFetcher
from src.custom.custom_article_integrator import CustomArticleIntegrator

def clean_project_name(name):
    """Clean up project names to be more readable."""
    # Special case for short project names
    if len(name) <= 3:
        return name
        
    # Replace hyphens and underscores with spaces
    cleaned = name.replace('-', ' ').replace('_', ' ')
    
    # Handle special cases with brackets
    cleaned = cleaned.replace('[', '').replace(']', '')
    
    # Capitalize first letter of each word
    cleaned = ' '.join(word.capitalize() for word in cleaned.split())
    
    return cleaned

def format_blog_posts_html(blog_posts):
    """Format blog posts with proper HTML structure."""
    if not blog_posts or len(blog_posts) == 0:
        return "<h2>Recent Articles</h2><p>We're gathering fresh content for our next issue.</p>"

    html = "<h2>Quick Reads for Data Enthusiasts</h2>\n"
    html += "<p><em>Stay up-to-date with these thought-provoking articles:</em></p>\n<ul>\n"
    
    for i, post in enumerate(blog_posts[:5]):
        # Clean up and shorten the summary
        summary = post.get('summary', '').replace('\n', ' ').strip()
        if not summary:
            summary = "An interesting read from the data community."
            
        if len(summary) > 120:
            summary = summary[:117] + "..."
            
        # Estimate read time (rough calculation)
        words = len(summary.split())
        read_time = max(1, words // 200)
        
        html += f'<li><strong><a href="{post.get("link", "#")}">{post.get("title", "Interesting Article")}</a></strong><br>\n'
        html += f"<p>{summary}</p>\n"
        html += f'<p><em>📚 {read_time}-minute read · From {post.get("source", "The Web")}</em></p>\n'
        
        # Add a divider except after the last item
        if i < len(blog_posts[:5]) - 1:
            html += "<hr>\n"
        
        html += "</li>\n"
    
    html += "</ul>"
    return html

def generate_trends_content():
    """Generate fallback trends content."""
    return """
<h1>Featured Data Stories</h1>

<h2>Making Sense of Patent Documents with AI</h2>

<p>Have you ever tried to read a patent? They're often filled with technical jargon and complex diagrams that can be difficult to understand. Researchers are now using machine learning to make these documents more accessible.</p>

<p>By applying natural language processing and computer vision techniques, AI systems can now classify patents, extract key information, and even predict how long a patent might remain valuable. This is especially helpful for researchers, inventors, and companies who need to navigate the vast landscape of intellectual property.</p>

<p><strong>Why This Matters:</strong> Better patent analysis tools mean more innovation can build on existing ideas, potentially accelerating technological progress in areas like healthcare, climate solutions, and more.</p>

<h2>Open Data in Patent Analysis</h2>

<p>The open data movement is making waves in patent research. Several projects in our GitHub section this month focus on creating openly available tools that analyze patent documents, classify them automatically, and extract useful insights.</p>

<p>These open source approaches are democratizing access to patent information that was previously only available through expensive proprietary platforms. Now, smaller organizations and individual inventors can gain insights that were once only accessible to large corporations.</p>

<p><strong>Why This Matters:</strong> When patent data becomes more accessible, innovation becomes more inclusive, potentially leading to more diverse and creative solutions to our biggest challenges.</p>
"""

async def main():
    try:
        print("Starting newsletter generation for Club for Open Data Enthusiasts...")
        
        # Initialize components
        print("Initializing components...")
        agent = NewsletterAgent()
        integrator = NewsletterIntegrator()
        curator = ContentCurator()
        content_fetcher = FreeContentFetcher()
        custom_article_integrator = CustomArticleIntegrator()
        
        # Create templates directory if it doesn't exist
        templates_dir = Path(backend_dir) / 'src' / 'templates' / 'templates'
        templates_dir.mkdir(parents=True, exist_ok=True)
        template_mgr = NewsletterTemplateManager(str(templates_dir))
        
        # Fetch raw content
        print("Gathering content...")
        blog_posts = await agent.fetch_tech_blog_posts()
        github_projects = await agent.fetch_github_projects()
        papers = await agent.fetch_arxiv_papers()
        learning_resources = agent.get_learning_resources()
        
        # Fetch free social media content
        print("Fetching social media and additional content...")
        # YouTube channel usernames or IDs
        youtube_channels = [
            "GoogleDevelopers",  # Google Developers
            "stanfordonline",    # Stanford
            "mitocw"             # MIT OpenCourseWare
        ]
        
        # Twitter/X usernames
        twitter_accounts = [
            "kaggle",
            "DataScienceCtrl",
            "OpenAI"
        ]
        
        # Fetch content using free methods
        youtube_content = await content_fetcher.fetch_youtube_content(youtube_channels)
        twitter_content = await content_fetcher.fetch_twitter_content(twitter_accounts)
        additional_blog_content = await content_fetcher.fetch_tech_blog_posts(
            categories=['open data', 'data visualization', 'ai ethics']
        )
        
        # Combine social media content
        all_social_content = youtube_content + twitter_content + additional_blog_content[:3]
        
        # Process custom articles
        print("Processing custom articles...")
        custom_articles = await custom_article_integrator.process_custom_articles()
        
        # Curate content
        print("Curating the most relevant and engaging content...")
        curated_posts = curator.curate_blog_posts(blog_posts)
        curated_projects = curator.curate_github_projects(github_projects)
        
        # Special handling for project names
        for project in curated_projects:
            project['display_name'] = clean_project_name(project['name'])
            # Special case for "-L-" project
            if project['name'] == "-L-":
                project['display_name'] = "W3C Strategic Highlights"
        
        # Use a static theme or derive from content
        newsletter_theme = "Patent Analysis & Open Data"
        print(f"Using newsletter theme: {newsletter_theme}")
        
        # Generate trends content (use fallback to ensure consistency)
        trends_content = generate_trends_content()
        
        # Format content sections with proper HTML
        tools_html = """
<h2>Cool Tools &amp; Projects You Might Want to Try</h2>
<ul>
"""
        for project in curated_projects:
            tools_html += f'<li><p><strong><a href="{project["url"]}">{project["display_name"]}</a></strong> ⭐ {project["stars"]} stars<br />\n'
            tools_html += f'  {project["description"]}</p></li>\n'
        
        tools_html += """
</ul>
<blockquote>
<p><strong>Have you tried any of these tools?</strong> Share your experience at our next meetup!</p>
</blockquote>
"""

        # Render learning resources as HTML directly
        learning_html = """
<h2>Learn Something New Today</h2>
<p><em>Looking to expand your data skills? Here are some resources our members are finding valuable:</em></p>
<ul>
"""
        for resource in learning_resources:
            # Add estimated time and difficulty based on the resource type
            if "course" in resource.get('title', '').lower() or "introduction" in resource.get('title', '').lower():
                difficulty = "Beginner-Friendly" 
                time_est = "4-6 hours"
            elif "deep dive" in resource.get('description', '').lower() or "advanced" in resource.get('title', '').lower():
                difficulty = "Advanced"
                time_est = "10+ hours"
            else:
                difficulty = "Intermediate"
                time_est = "2-3 hours"
                
            learning_html += f'<li><p><strong><a href="{resource["url"]}">{resource["title"]}</a></strong><br />\n'
            learning_html += f'  {resource["description"]}<br />\n'
            learning_html += f'<em>{difficulty} · Approx. {time_est}</em></p></li>\n'
        
        learning_html += """
</ul>
<blockquote>
<p><strong>Know a great resource?</strong> Email us your suggestions for next month's newsletter!</p>
</blockquote>
"""

        # Format blog posts
        blog_html = format_blog_posts_html(curated_posts)
        
        # Format social media content
        social_html = content_fetcher.format_social_content_html(all_social_content)
        
        # Format custom articles
        custom_articles_html = custom_article_integrator.format_custom_articles_html(custom_articles)
        
        # Assemble newsletter data with HTML content directly
        newsletter = {
            'metadata': {
                'month': datetime.now().strftime('%B %Y'),
                'generatedAt': datetime.now().isoformat(),
                'theme': newsletter_theme,
                'source_counts': {
                    'papers': len(papers),
                    'blog_posts': len(curated_posts),
                    'github_projects': len(curated_projects),
                    'learning_resources': len(learning_resources),
                    'social_media': len(all_social_content),
                    'custom_articles': len(custom_articles)
                }
            },
            'sections': {
                'emerging_trends': {
                    'title': 'Data Stories & Trends',
                    'content': '',  # Not used
                    'html_content': trends_content
                },
                'custom_articles': {
                    'title': 'Editor\'s Picks',
                    'content': '',  # Not used
                    'html_content': custom_articles_html
                },
                'tools_and_projects': {
                    'title': 'Cool Tools & Projects',
                    'content': '',  # Not used
                    'html_content': tools_html
                },
                'learning_resources': {
                    'title': 'Learn Something New',
                    'content': '',  # Not used
                    'html_content': learning_html
                },
                'blog_posts': {
                    'title': 'Quick Reads for Data Enthusiasts',
                    'content': '',  # Not used
                    'html_content': blog_html
                },
                'social_media': {
                    'title': 'From Around the Web',
                    'content': '',  # Not used
                    'html_content': social_html
                }
            }
        }
        
        # Create a simple HTML template
        html_template = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ metadata.month }} Newsletter - Club for Open Data Enthusiasts</title>
    <style>
        /* Theme Variables */
        html[data-theme="light"] {
            --bg-primary: #FFFFFF;
            --bg-secondary: #F7F9FC;
            --bg-highlight: #ECF4FF;
            --text-primary: #1B1B1B;
            --text-secondary: #454545;
            --accent-primary: #0076D6;
            --accent-secondary: #205493;
            --border-color: #DFE1E6;
        }

        html[data-theme="dark"] {
            --bg-primary: #18181B;
            --bg-secondary: #27272A;
            --bg-highlight: #1F2937;
            --text-primary: #E4E4E7;
            --text-secondary: #A1A1AA;
            --accent-primary: #60A5FA;
            --accent-secondary: #93C5FD;
            --border-color: #3F3F46;
        }

        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            color: var(--text-primary);
            background-color: var(--bg-primary);
        }

        /* Header and branding */
        .newsletter-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .newsletter-title {
            font-size: 2.2rem;
            color: var(--accent-secondary);
            margin-bottom: 0.5rem;
        }
        
        .newsletter-subtitle {
            font-size: 1.2rem;
            color: var(--text-secondary);
            font-weight: normal;
        }
        
        /* Section styling */
        .section {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 2rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        .section-header {
            font-size: 1.6rem;
            color: var(--accent-primary);
            margin-bottom: 1.2rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.5rem;
        }
        
        /* Content styling */
        h2 {
            color: var(--accent-secondary);
            font-size: 1.4rem;
            margin-top: 1.5rem;
        }
        
        h3 {
            color: var(--text-secondary);
            font-size: 1.2rem;
            font-weight: 600;
        }
        
        p {
            margin: 1rem 0;
        }
        
        a {
            color: var(--accent-primary);
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        ul, ol {
            padding-left: 1.5rem;
        }
        
        li {
            margin: 0.5rem 0;
        }
        
        blockquote {
            background: var(--bg-highlight);
            border-left: 4px solid var(--accent-primary);
            margin: 1.5rem 0;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            font-style: italic;
        }
        
        /* Highlight boxes */
        .highlight-box {
            background: var(--bg-highlight);
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
            border: 1px solid var(--border-color);
        }
        
        .highlight-box h4 {
            margin-top: 0;
            color: var(--accent-secondary);
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        /* Responsive styles */
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .newsletter-title {
                font-size: 1.8rem;
            }
        }
        
        /* Theme toggle button */
        #theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 0.5rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        /* Separator styling */
        hr {
            border: 0;
            height: 1px;
            background: var(--border-color);
            margin: 1.5rem 0;
        }
    </style>
</head>
<body>
    <button id="theme-toggle" aria-label="Toggle dark/light mode">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
    </button>

    <div class="newsletter-header">
        <h1 class="newsletter-title">{{ metadata.month }} Data Explorer</h1>
        <h2 class="newsletter-subtitle">Club for Open Data Enthusiasts</h2>
    </div>
    
    <div class="section">
        <div class="section-header">{{ sections.emerging_trends.title }}</div>
        {{ sections.emerging_trends.html_content|safe }}
    </div>
    
    {% if sections.custom_articles.html_content %}
    <div class="section">
        <div class="section-header">{{ sections.custom_articles.title }}</div>
        {{ sections.custom_articles.html_content|safe }}
    </div>
    {% endif %}
    
    <div class="section">
        <div class="section-header">{{ sections.tools_and_projects.title }}</div>
        {{ sections.tools_and_projects.html_content|safe }}
    </div>
    
    <div class="section">
        <div class="section-header">{{ sections.learning_resources.title }}</div>
        {{ sections.learning_resources.html_content|safe }}
    </div>
    
    <div class="section">
        <div class="section-header">{{ sections.blog_posts.title }}</div>
        {{ sections.blog_posts.html_content|safe }}
    </div>
    
    {% if sections.social_media.html_content %}
    <div class="section">
        <div class="section-header">{{ sections.social_media.title }}</div>
        {{ sections.social_media.html_content|safe }}
    </div>
    {% endif %}
    
    <div class="highlight-box">
        <h4>Share Your Data Stories!</h4>
        <p>Have you used data in an interesting way recently? We'd love to feature your story in our next newsletter!</p>
        <p>Drop us an email at <a href="mailto:newsletter@club.org">newsletter@club.org</a> with your project details.</p>
    </div>
    
    <div class="footer">
        <p>Generated: {{ metadata.generatedAt }}</p>
        <p>USPTO <a href="https://github.com/USPTOCode/" title="Club for Open Data Enthusiasts">C.O.D.E.</a></p>
        <p>
            Content sourced from {{ metadata.source_counts.papers }} research papers, 
            {{ metadata.source_counts.blog_posts }} blog posts, 
            {{ metadata.source_counts.github_projects }} GitHub projects
            {% if metadata.source_counts.social_media > 0 %}, {{ metadata.source_counts.social_media }} social media posts{% endif %}
            {% if metadata.source_counts.custom_articles > 0 %}, and {{ metadata.source_counts.custom_articles }} editor's picks{% endif %}
        </p>
    </div>

    <script>
        // Theme toggle functionality
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        
        // Check for saved theme preference or system preference
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme) {
            html.setAttribute('data-theme', savedTheme);
        } else if (prefersDark) {
            html.setAttribute('data-theme', 'dark');
        }
        
        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    </script>
</body>
</html>"""
        
        # Generate the newsletter
        print("Generating final newsletter HTML...")
        date_str = datetime.now().strftime('%Y_%m')
        newsletters_dir = Path(integrator.output_dir) / 'newsletters'
        newsletters_dir.mkdir(parents=True, exist_ok=True)
        
        # Use Jinja2 directly
        template = Template(html_template)
        html_content = template.render(**newsletter)
        
        html_path = newsletters_dir / f"{date_str}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # Mark custom articles as included in the newsletter
        if custom_articles:
            included_urls = [article['url'] for article in custom_articles]
            custom_article_integrator.mark_as_included(included_urls)
            
        print(f"\nNewsletter generated successfully!")
        print(f"HTML version: {html_path}")
        print("\nContent sources:")
        print(f"Papers: {newsletter['metadata']['source_counts']['papers']}")
        print(f"Blog posts: {newsletter['metadata']['source_counts']['blog_posts']}")
        print(f"GitHub projects: {newsletter['metadata']['source_counts']['github_projects']}")
        print(f"Learning resources: {newsletter['metadata']['source_counts']['learning_resources']}")
        if newsletter['metadata']['source_counts']['social_media'] > 0:
            print(f"Social media posts: {newsletter['metadata']['source_counts']['social_media']}")
        if newsletter['metadata']['source_counts']['custom_articles'] > 0:
            print(f"Editor's picks: {newsletter['metadata']['source_counts']['custom_articles']}")
        
    except Exception as e:
        print(f"Error generating newsletter: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())