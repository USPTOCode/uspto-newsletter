import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json
from pathlib import Path

from src.agent.newsletter_agent import NewsletterAgent
from src.integrator.newsletter_integrator import NewsletterIntegrator
from src.integrator.subscriber_manager import SubscriberManager

class NewsletterScheduler:
    """Handles periodic scanning of articles and newsletter generation."""
    
    def __init__(self, scan_interval_hours: int = 24):
        self.scan_interval = scan_interval_hours
        self.agent = NewsletterAgent()
        self.integrator = NewsletterIntegrator()
        self.subscriber_manager = SubscriberManager()
        self.setup_logging()
        
        # Directory to store daily scans
        self.scans_dir = Path('data/daily_scans')
        self.scans_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_logging(self):
        """Configure logging for the scheduler."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='scheduler.log'
        )
        self.logger = logging.getLogger('NewsletterScheduler')
        
    async def perform_daily_scan(self):
        """Perform a daily scan for new articles."""
        try:
            self.logger.info("Starting daily article scan...")
            
            # Fetch new articles
            papers = await self.agent.fetch_arxiv_papers()
            blog_posts = await self.agent.fetch_tech_blog_posts()
            
            # Create scan data
            scan_data = {
                'date': datetime.now().isoformat(),
                'papers': papers,
                'blog_posts': blog_posts
            }
            
            # Save scan data
            date_str = datetime.now().strftime('%Y_%m_%d')
            scan_file = self.scans_dir / f'scan_{date_str}.json'
            
            with open(scan_file, 'w', encoding='utf-8') as f:
                json.dump(scan_data, f, indent=2)
                
            self.logger.info(f"Daily scan completed and saved to {scan_file}")
            return scan_data
            
        except Exception as e:
            self.logger.error(f"Error performing daily scan: {e}")
            raise
            
    async def compile_monthly_newsletter(self):
        """Compile monthly newsletter from daily scans."""
        try:
            current_month = datetime.now().strftime('%Y_%m')
            scan_files = list(self.scans_dir.glob(f'scan_{current_month}*.json'))
            
            if not scan_files:
                self.logger.warning(f"No scan files found for month {current_month}")
                return None
                
            # Combine all scans
            all_papers = []
            all_blog_posts = []
            
            for scan_file in scan_files:
                with open(scan_file, 'r', encoding='utf-8') as f:
                    scan_data = json.load(f)
                    all_papers.extend(scan_data['papers'])
                    all_blog_posts.extend(scan_data['blog_posts'])
            
            # Generate newsletter content
            newsletter = await self.agent.compile_newsletter()
            
            # Save newsletter
            date_str = datetime.now().strftime('%Y_%m')
            html_path = self.integrator.save_newsletter_as(
                newsletter, 
                'html', 
                f'newsletters/{date_str}.html'
            )
            
            self.logger.info(f"Monthly newsletter generated and saved to {html_path}")
            return html_path
            
        except Exception as e:
            self.logger.error(f"Error compiling monthly newsletter: {e}")
            raise
            
    async def run(self):
        """Main scheduler loop."""
        while True:
            try:
                # Perform daily scan
                await self.perform_daily_scan()
                
                # Check if it's the end of the month
                now = datetime.now()
                if now.month != (now + timedelta(days=1)).month:
                    self.logger.info("End of month detected, generating newsletter...")
                    await self.compile_monthly_newsletter()
                    
                    # Send to subscribers
                    subscribers = self.subscriber_manager.get_active_subscribers()
                    if subscribers:
                        # TODO: Implement email sending
                        self.logger.info(f"Newsletter sent to {len(subscribers)} subscribers")
                
                # Wait for next scan interval
                await asyncio.sleep(self.scan_interval * 3600)  # Convert hours to seconds
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(300)  # 5 minutes 