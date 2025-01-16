import os
from datetime import datetime
import json
from pathlib import Path
import logging
from typing import Dict, Optional

from src.integrator.formatter import NewsletterFormatter, FormatType

class NewsletterIntegrator:
    def __init__(self, output_dir: str = None):
        """Initialize the integrator with optional custom output directory."""
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'data', 'generated')
        self._ensure_output_dir()
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the integrator."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='integrator.log'
        )
        self.logger = logging.getLogger('NewsletterIntegrator')

    def _ensure_output_dir(self):
        """Ensure the output directory exists."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    async def generate_newsletter(self) -> Dict:
        """Generate a new newsletter."""
        try:
            # In a real implementation, this would create the newsletter content
            # For now, return sample data
            return {
                'metadata': {
                    'month': datetime.now().strftime('%B %Y'),
                    'generatedAt': datetime.now().isoformat(),
                    'source_counts': {
                        'papers': 5,
                        'blog_posts': 3,
                        'github_projects': 4
                    }
                },
                'sections': {
                    'emerging_trends': {
                        'title': 'Emerging Trends',
                        'content': '# Sample content'
                    }
                }
            }
        except Exception as e:
            self.logger.error(f"Error generating newsletter: {e}")
            raise

    def save_newsletter_as(self, data: Dict, format_type: FormatType, filename: Optional[str] = None) -> str:
        """Save newsletter in specified format."""
        try:
            formatter = NewsletterFormatter()
            content = formatter.format_newsletter(data, format_type)
            
            if not filename:
                timestamp = datetime.now().strftime('%Y%m')
                filename = f"newsletter_{timestamp}.{format_type}"
            
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Saved {format_type} newsletter to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving newsletter as {format_type}: {e}")
            raise