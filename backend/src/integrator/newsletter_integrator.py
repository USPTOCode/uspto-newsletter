import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from .formatter import FormatType, NewsletterFormatter
from src.agent.newsletter_agent import NewsletterAgent

class NewsletterIntegrator:
    """Handles the integration between newsletter generation and frontend display."""
    
    def __init__(self, output_dir: str = None):
        """Initialize the integrator with optional custom output directory."""
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'data', 'generated')
        self.agent = NewsletterAgent()
        self.setup_logging()
        self._ensure_output_dir()

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
        """Generate a new newsletter and prepare it for frontend display."""
        try:
            # Generate raw newsletter content
            raw_newsletter = await self.agent.compile_newsletter()
            if not raw_newsletter:
                raise ValueError("Failed to generate newsletter content")

            # Transform for frontend
            frontend_data = self._transform_for_frontend(raw_newsletter)
            
            # Save both raw and transformed versions
            self._save_newsletter(raw_newsletter, 'raw')
            self._save_newsletter(frontend_data, 'frontend')

            return frontend_data

        except Exception as e:
            self.logger.error(f"Error generating newsletter: {e}")
            raise

    def _transform_for_frontend(self, raw_newsletter: Dict) -> Dict:
        """Transform raw newsletter data into frontend-friendly format."""
        try:
            return {
                'metadata': {
                    'month': raw_newsletter['month'],
                    'generatedAt': raw_newsletter['metadata']['generated_at'],
                    'sourceCounts': raw_newsletter['metadata']['source_counts']
                },
                'sections': {
                    'emergingTrends': {
                        'title': 'Emerging Trends in Data Science',
                        'content': raw_newsletter['sections']['emerging_trends'],
                        'icon': 'trending-up'
                    },
                    'toolsAndProjects': {
                        'title': 'Innovative Tools & Projects',
                        'content': raw_newsletter['sections']['tools_and_projects'],
                        'icon': 'tool'
                    },
                    'learningResources': {
                        'title': 'Learning & Development',
                        'content': raw_newsletter['sections']['learning_resources'],
                        'icon': 'book-open'
                    }
                },
                'display': {
                    'theme': 'light',
                    'layout': 'card',
                    'showMetadata': True
                }
            }
        except Exception as e:
            self.logger.error(f"Error transforming newsletter data: {e}")
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


    def _save_newsletter(self, data: Dict, version: str = 'raw') -> str:
        """Save newsletter data to file."""
        try:
            timestamp = datetime.now().strftime('%Y%m')
            filename = f"newsletter_{version}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved {version} newsletter to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error saving newsletter: {e}")
            raise
    

    def get_latest_newsletter(self, version: str = 'frontend') -> Optional[Dict]:
        """Retrieve the most recent newsletter data."""
        try:
            pattern = f"newsletter_{version}_*.json"
            newsletters = list(Path(self.output_dir).glob(pattern))
            
            if not newsletters:
                return None

            latest = max(newsletters, key=lambda x: x.stat().st_mtime)
            
            with open(latest, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error retrieving latest newsletter: {e}")
            return None

    def list_available_newsletters(self) -> Dict[str, list]:
        """List all available newsletter files."""
        try:
            raw_pattern = "newsletter_raw_*.json"
            frontend_pattern = "newsletter_frontend_*.json"
            
            raw_files = list(Path(self.output_dir).glob(raw_pattern))
            frontend_files = list(Path(self.output_dir).glob(frontend_pattern))

            return {
                'raw': [f.name for f in sorted(raw_files, key=lambda x: x.stat().st_mtime, reverse=True)],
                'frontend': [f.name for f in sorted(frontend_files, key=lambda x: x.stat().st_mtime, reverse=True)]
            }

        except Exception as e:
            self.logger.error(f"Error listing newsletters: {e}")
            return {'raw': [], 'frontend': []}

# Example usage
async def main():
    integrator = NewsletterIntegrator()
    
    # Generate new newsletter
    newsletter = await integrator.generate_newsletter()
    
    # List available newsletters
    available = integrator.list_available_newsletters()
    print(f"Available newsletters: {available}")
    
    # Get latest version
    latest = integrator.get_latest_newsletter()
    if latest:
        print(f"Latest newsletter is from: {latest['metadata']['month']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())