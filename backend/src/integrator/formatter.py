from typing import Dict, Literal
import markdown
import json
from datetime import datetime
from pathlib import Path
import logging
from jinja2 import Environment, PackageLoader, select_autoescape

FormatType = Literal['json', 'markdown', 'html', 'email']

class NewsletterFormatter:
    """Handles conversion of newsletter content into various formats."""
    
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('src.integrator', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.logger = logging.getLogger('NewsletterFormatter')

    def format_newsletter(self, data: Dict, format_type: FormatType) -> str:
        """Convert newsletter data to specified format."""
        format_methods = {
            'json': self._format_json,
            'markdown': self._format_markdown,
            'html': self._format_html,
            'email': self._format_email
        }
        
        if format_type not in format_methods:
            raise ValueError(f"Unsupported format: {format_type}")
            
        return format_methods[format_type](data)

    def _format_json(self, data: Dict) -> str:
        """Format newsletter as JSON."""
        return json.dumps(data, indent=2)

    def _format_markdown(self, data: Dict) -> str:
        """Format newsletter as Markdown."""
        md_content = f"# {data['metadata']['month']} Newsletter\n\n"
        
        for section_name, section in data['sections'].items():
            md_content += f"## {section['title']}\n\n"
            md_content += f"{section['content']}\n\n"
        
        # Add metadata footer
        md_content += "---\n"
        md_content += f"Generated: {data['metadata']['generatedAt']}\n"
        md_content += "USPTO Open Data Enthusiasts Club\n"
        
        return md_content

    def _format_html(self, data: Dict) -> str:
        """Format newsletter as HTML."""
        template = self.env.get_template('newsletter.html')
        return template.render(
            title=f"{data['metadata']['month']} Newsletter",
            sections=data['sections'],
            metadata=data['metadata']
        )

    def _format_email(self, data: Dict) -> str:
        """Format newsletter as plain text email."""
        email_content = f"USPTO Open Data Enthusiasts Newsletter - {data['metadata']['month']}\n"
        email_content += "=" * 80 + "\n\n"
        
        for section_name, section in data['sections'].items():
            email_content += f"{section['title'].upper()}\n"
            email_content += "-" * len(section['title']) + "\n\n"
            # Convert any markdown to plain text
            content = section['content'].replace('#', '').replace('*', '')
            email_content += f"{content}\n\n"
        
        email_content += "-" * 80 + "\n"
        email_content += "USPTO Open Data Enthusiasts Club\n"
        email_content += f"Generated: {data['metadata']['generatedAt']}\n"
        
        return email_content