import os
from datetime import datetime
import markdown
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any

class NewsletterTemplateManager:
    """Manages templates for newsletter generation with customizable themes and layouts."""
    
    def __init__(self, templates_dir: str = None):
        """Initialize the template manager with optional custom templates directory."""
        self.templates_dir = templates_dir or os.path.join(os.getcwd(), 'templates')
        # Ensure directory exists
        os.makedirs(self.templates_dir, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        self._prepare_default_templates()
    
    def _prepare_default_templates(self):
        """Create default templates if they don't exist."""
        # Create a modern, engaging HTML template
        html_template_path = os.path.join(self.templates_dir, 'newsletter_template.html')
        if not os.path.exists(html_template_path):
            with open(html_template_path, 'w', encoding='utf-8') as f:
                f.write(self._get_default_html_template())
    
    def _get_default_html_template(self) -> str:
        """Return a default HTML template with a clean, modern design."""
        return '''<!DOCTYPE html>
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
    
    <div class="section">
        <div class="section-header">{{ sections.tools_and_projects.title }}</div>
        {{ sections.tools_and_projects.html_content|safe }}
    </div>
    
    <div class="section">
        <div class="section-header">{{ sections.learning_resources.title }}</div>
        {{ sections.learning_resources.html_content|safe }}
    </div>
    
    {% if sections.blog_posts %}
    <div class="section">
        <div class="section-header">{{ sections.blog_posts.title }}</div>
        {{ sections.blog_posts.html_content|safe }}
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
            {{ metadata.source_counts.blog_posts }} blog posts, and 
            {{ metadata.source_counts.github_projects }} GitHub projects
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
</html>'''
    
    def convert_markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown content to HTML."""
        # Use the Python Markdown library
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'nl2br', 'sane_lists']
        )
        return html_content
    
    def prepare_section_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare section data by converting markdown to HTML."""
        prepared_data = {
            'metadata': data['metadata'],
            'sections': {}
        }
        
        # Convert each section's content from markdown to HTML
        for section_key, section_data in data['sections'].items():
            prepared_data['sections'][section_key] = {
                'title': section_data['title'],
                'content': section_data['content'],  # Keep the original markdown
                'html_content': self.convert_markdown_to_html(section_data['content'])  # Add HTML version
            }
        
        return prepared_data
    
    def render_newsletter(self, data: Dict[str, Any], template_name: str = 'newsletter_template.html') -> str:
        """Render the newsletter data with the specified template."""
        # Prepare data by converting markdown to HTML
        prepared_data = self.prepare_section_data(data)
        
        # Load template
        template = self.env.get_template(template_name)
        
        # Render with prepared data
        return template.render(**prepared_data)