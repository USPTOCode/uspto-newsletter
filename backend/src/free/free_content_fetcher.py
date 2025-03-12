import os
import logging
from typing import List, Dict, Any
import feedparser
import json
import random
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import time

class FreeContentFetcher:
    """Fetches content from various sources without requiring paid API keys."""
    
    def __init__(self):
        """Initialize the content fetcher."""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='content_fetcher.log'
        )
        self.logger = logging.getLogger('FreeContentFetcher')
        
        # Ensure cache directory exists
        self.cache_dir = os.path.join(os.getcwd(), 'data', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    async def fetch_youtube_content(self, channels: List[str], max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch recent YouTube videos using RSS feeds instead of the API.
        
        Args:
            channels: List of channel IDs or usernames
            max_results: Maximum number of results per channel
            
        Returns:
            List of video items
        """
        videos = []
        
        try:
            for channel in channels:
                # Try both formats (channel ID and username) since we don't know which one we have
                feed_urls = [
                    f"https://www.youtube.com/feeds/videos.xml?channel_id={channel}",
                    f"https://www.youtube.com/feeds/videos.xml?user={channel}"
                ]
                
                for feed_url in feed_urls:
                    try:
                        feed = feedparser.parse(feed_url)
                        
                        if feed.entries:
                            # Found a working feed
                            channel_title = feed.feed.title if hasattr(feed.feed, 'title') else channel
                            
                            for entry in feed.entries[:max_results]:
                                video_id = entry.yt_videoid if hasattr(entry, 'yt_videoid') else entry.id.split(':')[-1]
                                videos.append({
                                    'title': entry.title,
                                    'description': entry.summary if hasattr(entry, 'summary') else '',
                                    'link': f"https://www.youtube.com/watch?v={video_id}",
                                    'published': entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                                    'source': f"YouTube - {channel_title}",
                                    'type': 'youtube'
                                })
                            
                            # If we found entries, no need to try the other format
                            break
                    except Exception as e:
                        self.logger.warning(f"Error fetching YouTube feed {feed_url}: {e}")
                        continue
                        
            self.logger.info(f"Fetched {len(videos)} YouTube videos using RSS")
            return videos
            
        except Exception as e:
            self.logger.error(f"Error fetching YouTube content: {e}")
            return []
            
    async def fetch_twitter_content(self, usernames: List[str], max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch Twitter/X content without using the official API.
        
        This uses a public timeline page approach, which is not reliable for production use
        but can work for demo purposes. For production, consider Nitter RSS feeds or services
        like ScrapingBee.
        
        Args:
            usernames: List of Twitter usernames
            max_results: Maximum number of results per user
            
        Returns:
            List of tweet items
        """
        tweets = []
        
        try:
            # For demo purposes, use some sample tweets
            # In a real implementation, you could use Nitter RSS feeds
            sample_tweets = [
                {
                    'username': 'kaggle',
                    'text': 'Announcing our latest competition: Predicting renewable energy output based on weather patterns. $50,000 in prizes!',
                    'date': '2025-02-28T15:30:00'
                },
                {
                    'username': 'kaggle',
                    'text': 'New dataset available: Global Climate Data 2010-2025. Perfect for time series analysis and forecasting projects.',
                    'date': '2025-03-05T12:15:00'
                },
                {
                    'username': 'DataScienceCtrl',
                    'text': '10 Python libraries for data visualization you probably haven\'t heard of. Number 7 will surprise you! https://example.com/viz-libs',
                    'date': '2025-03-01T09:45:00'
                },
                {
                    'username': 'DataScienceCtrl',
                    'text': 'What\'s the difference between a data scientist, data analyst, and data engineer? A thread on roles and responsibilities in data careers.',
                    'date': '2025-03-07T14:20:00'
                },
                {
                    'username': 'OpenAI',
                    'text': 'Introducing our latest research on multimodal learning. New techniques for combining text, image, and audio understanding in a single model.',
                    'date': '2025-03-02T16:10:00'
                },
                {
                    'username': 'OpenAI',
                    'text': 'We\'re hiring! Looking for researchers and engineers interested in responsible AI development and evaluation.',
                    'date': '2025-03-06T11:30:00'
                }
            ]
            
            # Filter to the requested usernames
            for username in usernames:
                user_tweets = [t for t in sample_tweets if t['username'].lower() == username.lower()]
                for tweet in user_tweets[:max_results]:
                    tweets.append({
                        'title': f"Tweet from {tweet['username']}",
                        'description': tweet['text'],
                        'link': f"https://twitter.com/{tweet['username']}",
                        'published': tweet['date'],
                        'source': f"Twitter/X - {tweet['username']}",
                        'type': 'twitter'
                    })
                    
            # For production, replace the above with Nitter RSS feed parsing
            # Example code for Nitter RSS (when available):
            #for username in usernames:
            #    feed_url = f"https://nitter.net/{username}/rss"
            #    feed = feedparser.parse(feed_url)
            #    for entry in feed.entries[:max_results]:
            #        tweets.append({
            #            'title': f"Tweet from {username}",
            #            'description': entry.title,
            #            'link': entry.link,
            #            'published': entry.published,
            #            'source': f"Twitter/X - {username}",
            #            'type': 'twitter'
            #        })
            
            self.logger.info(f"Fetched {len(tweets)} tweets (sample data)")
            return tweets
            
        except Exception as e:
            self.logger.error(f"Error fetching Twitter content: {e}")
            return []
            
    async def fetch_tech_blog_posts(self, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch technology blog posts from various RSS feeds.
        
        Args:
            categories: Optional list of categories to filter by
            
        Returns:
            List of blog post items
        """
        if categories is None:
            categories = ['data', 'ai', 'ml', 'analytics', 'visualization']
            
        try:
            # These are RSS feeds that are freely available
            feeds = [
                # Data science and AI feeds
                'https://www.kdnuggets.com/feed',
                'https://www.datasciencecentral.com/feed',  
                'https://towardsdatascience.com/feed',
                'https://www.r-bloggers.com/feed/',
                'https://feeds.feedburner.com/kdnuggets-data-science-machine-learning-analytics-big-data',
                'https://www.datacamp.com/community/blog.rss',
                
                # Open source and open data feeds
                'https://opensource.com/feed',
                'https://www.data.gov/feed/',
                'https://aws.amazon.com/blogs/opensource/feed/',
                'https://blog.opencorporates.com/feed/',
                'https://opendatawatch.com/feed/',
                'https://blogs.worldbank.org/opendata/rss',
                
                # Technology news that often covers data topics
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://www.technologyreview.com/feed/',
                'https://www.zdnet.com/topic/big-data/rss.xml',
                'https://www.infoq.com/feed/data-eng/'
            ]
            
            posts = []
            for feed_url in feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    if not feed.entries:
                        self.logger.warning(f"No entries found for {feed_url}")
                        continue
                        
                    feed_title = feed.feed.title if hasattr(feed.feed, 'title') else "Tech Blog"
                    
                    for entry in feed.entries[:3]:  # Get 3 most recent from each feed
                        # Extract the content
                        title = entry.title if hasattr(entry, 'title') else "Blog Post"
                        link = entry.link if hasattr(entry, 'link') else "#"
                        published = entry.published if hasattr(entry, 'published') else datetime.now().isoformat()
                        
                        # Try to get summary from various possible attributes
                        summary = ""
                        if hasattr(entry, 'summary'):
                            summary = entry.summary
                        elif hasattr(entry, 'description'):
                            summary = entry.description
                        elif hasattr(entry, 'content'):
                            summary = entry.content[0].value if entry.content else ""
                            
                        # Clean up summary (remove HTML tags)
                        summary = re.sub(r'<[^>]+>', '', summary)
                        
                        # Check if the post is relevant to the categories
                        if not categories or any(cat.lower() in (title + " " + summary).lower() for cat in categories):
                            posts.append({
                                'title': title,
                                'summary': summary,
                                'link': link,
                                'published': published,
                                'source': feed_title,
                                'type': 'blog'
                            })
                except Exception as feed_error:
                    self.logger.warning(f"Error processing feed {feed_url}: {feed_error}")
                    continue
                    
                # Be nice to the servers
                time.sleep(0.5)
                
            # Sort by most recent
            posts = sorted(posts, key=lambda x: x.get('published', ''), reverse=True)
            self.logger.info(f"Fetched {len(posts)} relevant blog posts")
            return posts
            
        except Exception as e:
            self.logger.error(f"Error fetching blog posts: {e}")
            return []

    def format_social_content_html(self, items: List[Dict[str, Any]]) -> str:
        """Format social media and blog content into HTML."""
        if not items:
            return ""

        html = "<h2>From Around the Web</h2>\n"
        html += "<p><em>Stay updated with the latest content from data experts:</em></p>\n"
        
        # Group by type
        by_type = {}
        for item in items:
            item_type = item.get('type', 'other')
            if item_type not in by_type:
                by_type[item_type] = []
            by_type[item_type].append(item)
        
        # Format YouTube videos
        if 'youtube' in by_type and by_type['youtube']:
            html += "<h3>Latest Videos</h3>\n<ul>\n"
            for item in by_type['youtube'][:3]:
                html += f'<li><strong><a href="{item.get("link", "#")}">{item.get("title", "YouTube Video")}</a></strong><br>\n'
                html += f"<p>{item.get('description', '')}</p>\n"
                html += f'<p><em>From {item.get("source", "YouTube")}</em></p></li>\n'
            html += "</ul>\n"
        
        # Format Twitter posts
        if 'twitter' in by_type and by_type['twitter']:
            html += "<h3>Twitter/X Highlights</h3>\n<ul>\n"
            for item in by_type['twitter'][:3]:
                html += f'<li><strong><a href="{item.get("link", "#")}">{item.get("title", "Tweet")}</a></strong><br>\n'
                html += f"<p>{item.get('description', '')}</p>\n"
                html += f'<p><em>From {item.get("source", "Twitter/X")}</em></p></li>\n'
            html += "</ul>\n"
        
        # Format Blog posts if they're not already included elsewhere
        if 'blog' in by_type and by_type['blog']:
            html += "<h3>Data Science Blogs</h3>\n<ul>\n"
            for item in by_type['blog'][:3]:
                description = item.get('summary', '') or item.get('description', '')
                if len(description) > 150:
                    description = description[:147] + "..."
                    
                html += f'<li><strong><a href="{item.get("link", "#")}">{item.get("title", "Blog Post")}</a></strong><br>\n'
                html += f"<p>{description}</p>\n"
                html += f'<p><em>From {item.get("source", "Blog")}</em></p></li>\n'
            html += "</ul>\n"
                
        return html


# Example usage:
"""
async def main():
    fetcher = FreeContentFetcher()
    
    # YouTube channel usernames or IDs
    youtube_channels = [
        "GoogleDevelopers",
        "kaggle",
        "MIT"
    ]
    
    # Twitter/X usernames
    twitter_accounts = [
        "kaggle",
        "DataScienceCtrl",
        "OpenAI"
    ]
    
    # Fetch content
    youtube_content = await fetcher.fetch_youtube_content(youtube_channels)
    twitter_content = await fetcher.fetch_twitter_content(twitter_accounts)
    blog_content = await fetcher.fetch_tech_blog_posts(categories=['data science', 'open data'])
    
    # Combine all content
    all_content = youtube_content + twitter_content + blog_content
    
    # Format as HTML
    html_content = fetcher.format_social_content_html(all_content)
    print(html_content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
"""