from typing import Dict, Literal
import json
import logging
import markdown
from markdown.extensions import fenced_code, extra
from jinja2 import Environment, PackageLoader, select_autoescape

FormatType = Literal['json', 'html', 'markdown', 'email']

class NewsletterFormatter:
    """Handles conversion of newsletter content into various formats."""
    
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('src.integrator', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.env.filters['markdown'] = self._markdown_filter
        self.logger = logging.getLogger('NewsletterFormatter')

    def _markdown_filter(self, text):
        """Convert markdown to HTML."""
        if text is None:
            return ""
        
        # Use markdown extensions
        extensions = [
            'fenced_code',
            'tables',
            'extra'
        ]
        
        return markdown.markdown(text, extensions=extensions)

    def format_newsletter(self, data: Dict, format_type: FormatType) -> str:
        """Convert newsletter data to specified format."""
        format_methods = {
            'json': self._format_json,
            'html': self._format_html,
            'markdown': self._format_markdown,
            'email': self._format_email
        }
        
        if format_type not in format_methods:
            raise ValueError(f"Unsupported format: {format_type}")
            
        return format_methods[format_type](data)

    def _format_html(self, data: Dict) -> str:
        """Format newsletter as HTML."""
        try:
            template = self.env.get_template('newsletter.html')
            # Add detailed sources to metadata
            if 'sources' not in data['metadata']:
                data['metadata']['sources'] = {
                    'papers': data.get('papers', []),
                    'blog_posts': data.get('blog_posts', []),
                    'github_projects': data.get('github_projects', [])
                }
            return template.render(
                title=f"{data['metadata']['month']} Newsletter",
                sections={
                    'emerging_trends': {
                        'title': 'Emerging Trends in Data Science',
                        'content': data['sections']['emerging_trends']['content']
                    },
                    'tools_and_projects': {
                        'title': 'Innovative Tools & Projects',
                        'content': data['sections']['tools_and_projects']['content']
                    },
                    'learning_resources': {
                        'title': 'Learning & Development',
                        'content': data['sections']['learning_resources']['content']
                    }
                },
                metadata=data['metadata']
            )
        except Exception as e:
            self.logger.error(f"Error formatting HTML: {e}")
            raise

    def _format_json(self, data: Dict) -> str:
        """Format newsletter as JSON."""
        return json.dumps(data, indent=2)

    def _format_markdown(self, data: Dict) -> str:
        """Format newsletter as Markdown."""
        md_content = f"# {data['metadata']['month']} Newsletter\n\n"
        
        for section_name, section in data['sections'].items():
            title = section_name.replace('_', ' ').title()
            md_content += f"## {title}\n\n"
            content = section.get('content', '')
            md_content += f"{content}\n\n"
        
        md_content += "---\n"
        md_content += f"Generated: {data['metadata']['generatedAt']}\n"
        md_content += "USPTO Open Data Enthusiasts Club\n"
        
        return md_content

    def _format_email(self, data: Dict) -> str:
        """Format newsletter as plain text email."""
        email_content = f"USPTO Open Data Enthusiasts Newsletter - {data['metadata']['month']}\n"
        email_content += "=" * 80 + "\n\n"
        
        for section_name, section in data['sections'].items():
            title = section_name.replace('_', ' ').title()
            email_content += f"{title}\n"
            email_content += "-" * len(title) + "\n\n"
            content = section.get('content', '')
            plain_content = self._markdown_to_plain(content)
            email_content += f"{plain_content}\n\n"
        
        email_content += "-" * 80 + "\n"
        email_content += "USPTO Open Data Enthusiasts Club\n"
        email_content += f"Generated: {data['metadata']['generatedAt']}\n"
        
        return email_content

    def _markdown_to_plain(self, text: str) -> str:
        """Convert markdown to plain text."""
        if not text:
            return ""
        
        lines = []
        in_code_block = False
        
        for line in text.split('\n'):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if not in_code_block:
                # Remove markdown syntax
                line = (line.replace('**', '')
                          .replace('*', '')
                          .replace('###', '')
                          .replace('##', '')
                          .replace('#', '')
                          .replace('`', ''))
                if line.strip():
                    lines.append(line)
        
        return '\n'.join(lines)