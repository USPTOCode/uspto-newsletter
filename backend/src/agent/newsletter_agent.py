import os
import logging
import requests
from datetime import datetime
import arxiv
from openai import OpenAI
import feedparser
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class NewsletterAgent:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"NewsletterAgent using API Key: {api_key[:6]}...")
        self.openai_client = OpenAI(api_key=api_key)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='agent.log'
        )
        self.logger = logging.getLogger('NewsletterAgent')

    async def compile_newsletter(self) -> Dict:
        """Generate complete newsletter content."""
        try:
            print("Fetching GitHub projects...")
            projects = await self.fetch_github_projects()
            print(f"Fetched {len(projects)} GitHub projects")

            print("Fetching learning resources...")
            learning_resources = self.get_learning_resources()
            print(f"Collected {len(learning_resources)} learning resources")

            print("Fetching arXiv papers...")
            papers = await self.fetch_arxiv_papers()
            print(f"Fetched {len(papers)} arXiv papers")

            print("Fetching blog posts...")
            blog_posts = await self.fetch_tech_blog_posts()
            print(f"Fetched {len(blog_posts)} blog posts")

            print("Generating emerging trends section...")
            emerging_trends = await self.generate_trends_section(papers)
            print("Trends section generated")

            return {
                'metadata': {
                    'month': datetime.now().strftime('%B %Y'),
                    'generatedAt': datetime.now().isoformat(),
                    'source_counts': {
                        'github_projects': len(projects),
                        'learning_resources': len(learning_resources),
                        'papers': len(papers),
                        'blog_posts': len(blog_posts)  # ✅ FIXED: Include blog posts count
                    }
                },
                'sections': {
                    'emerging_trends': {
                        'title': 'Emerging Trends in Data Science',
                        'content': emerging_trends
                    },
                    'tools_and_projects': {
                        'title': 'Innovative Tools & Projects',
                        'content': self.format_github_projects(projects)
                    },
                    'learning_resources': {
                        'title': 'Learning & Development',
                        'content': self.format_learning_resources(learning_resources)
                    },
                    'blog_posts': {  # ✅ Ensure blog posts section is included
                        'title': 'Recent Blog Posts',
                        'content': self.format_blog_posts(blog_posts)
                    }
                }
            }
        except Exception as e:
            print(f"Error in compile_newsletter: {str(e)}")
            self.logger.error(f"Error compiling newsletter: {e}")
            raise



    async def fetch_arxiv_papers(self) -> List[Dict]:
        """Fetch relevant papers from arXiv."""
        try:
            print("Creating arXiv client...")
            client = arxiv.Client()
            search = arxiv.Search(
                query="patent AND machine learning",
                max_results=5,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            print("Fetching results...")
            for result in client.results(search):
                papers.append({
                    'title': result.title,
                    'summary': result.summary,
                    'authors': [author.name for author in result.authors],
                    'link': result.pdf_url,
                    'published': result.published.strftime('%Y-%m-%d')
                })
                print(f"Found paper: {result.title}")
            
            self.logger.info(f"Successfully fetched {len(papers)} papers from arXiv")
            return papers
            
        except Exception as e:
            print(f"Error in fetch_arxiv_papers: {str(e)}")
            self.logger.error(f"Error fetching arXiv papers: {e}")
            return []

    async def fetch_tech_blog_posts(self) -> List[Dict]:
        """Fetch posts from relevant tech blogs."""
        try:
            print("Fetching blog posts...")
            feeds = [
                # Government Open Data
                'https://www.data.gov/meta/feed/',  
                'https://data.gov.uk/feed',  
                'https://ec.europa.eu/europeandataportal/en/news/rss',  
                'https://opendata.blog/feed/',  
                'https://opendatascience.com/feed/',  
                'https://blogs.worldbank.org/opendata/rss',  
                'https://opendatawatch.com/feed/',  

                # AI, Machine Learning, Data Science
                'https://www.kdnuggets.com/feed',  
                'https://www.datasciencecentral.com/main/feed',  
                'https://insidebigdata.com/feed/',  
                'https://towardsdatascience.com/feed',  
                'https://datafloq.com/feed/',  
                'https://www.datacamp.com/community/blog.rss',  
                'https://www.r-bloggers.com/feed/',  
                'https://simplystatistics.org/feed/',  
                'https://statmodeling.stat.columbia.edu/feed/',  

                # New Additions (AI, LLMs, MLOps)
                'https://huggingface.co/blog/feed',  
                'https://ai.googleblog.com/feeds/posts/default',  
                'https://lilianweng.github.io/rss.xml',  
                'https://sebastianraschka.com/blog/index.xml',  
                'https://www.fast.ai/feed.xml',  
                'https://www.mlops.community/rss',
                

                # Cloud, Open Source, Data Engineering
                'https://cloudblogs.microsoft.com/opensource/feed/',  
                'https://aws.amazon.com/blogs/opensource/feed/',  
                'https://openlogic.com/blog/feed',  
                'https://cncf.io/feed/',  
                'https://instaclustr.com/feed/',  
                'https://opensource.org/news/feed',  
                'https://www.rudderstack.com/blog/rss.xml',  
                'https://www.snowflake.com/blog/feed/',  
                'https://www.precisely.com/blog/feed',  
                'https://aws.amazon.com/blogs/big-data/feed/',  
                'https://engineering.fb.com/feed/',  
                'https://eng.uber.com/feed/',  
                'https://medium.com/feed/@Pinterest_Engineering',  
                'https://engineeringblog.yelp.com/feed.xml',  
                'https://medium.com/feed/@AirbyteHQ',  
                'https://engineering.atspotify.com/feed/',  
                'https://www.infoq.com/data-eng/news.atom',  
                'https://www.datacamp.com/blog/category/data-engineering/rss',  
            ]

            posts = []
            for feed_url in feeds:
                try:
                    print(f"Checking feed: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    if not feed.entries:
                        print(f"Warning: No entries found for {feed_url}")
                        continue
                    for entry in feed.entries[:2]:  # Get 2 most recent from each
                        posts.append({
                            'title': entry.title,
                            'summary': entry.get('summary', ''),
                            'link': entry.link,
                            'source': feed.feed.title if 'title' in feed.feed else 'Unknown Source',
                            'published': entry.get('published', '')
                        })
                        print(f"Found post: {entry.title}")
                except Exception as e:
                    print(f"Error with feed {feed_url}: {str(e)}")
                    continue

            print(f"Found {len(posts)} total posts")
            return posts

        except Exception as e:
            print(f"Error fetching blog posts: {str(e)}")
            self.logger.error(f"Error fetching blog posts: {e}")
            return []


    async def generate_trends_section(self, papers: List[Dict]) -> str:
        """Generate an accessible, engaging trends section with real-world applications."""
        try:
            if not papers:
                print("No papers found to analyze")
                return "# Data Trends This Month\n\nWe're taking a short break this month while we gather more exciting data stories for you."

            print("Creating GPT prompt...")
            prompt = f"""Create an engaging, conversational section on data trends for a newsletter aimed at 
            a club of data enthusiasts with varying technical backgrounds.

            Recent Papers:
            {self._format_papers_for_prompt(papers)}

            Transform these technical papers into 2-3 accessible stories about how data is changing the world.
            For each story:
            1. Start with a compelling hook or real-world problem
            2. Explain how data science/AI is being used to address it
            3. Include 1-2 practical takeaways club members might find interesting
            4. Reference the relevant papers but in a casual way (like "researchers at X University found...")

            Use a friendly, conversational tone as if you're explaining to a curious friend.
            Avoid jargon when possible, and when you must use technical terms, briefly explain them.
            Add examples and analogies that make complex concepts relatable.
            
            Format the content in markdown with:
            - Engaging subheadings
            - Short paragraphs
            - Occasional bullet points for key takeaways
            - A brief "Why This Matters" section at the end of each story
            """

            print("Sending request to OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a talented science communicator who makes complex data topics engaging and accessible to general audiences while maintaining accuracy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            content = response.choices[0].message.content
            print("Successfully received GPT response")
            self.logger.info("Successfully generated engaging trends section")
            return content

        except Exception as e:
            print(f"Error in generate_trends_section: {str(e)}")
            self.logger.error(f"Error generating trends section: {e}")
            return "# Data Stories This Month\n\nWe're experiencing some technical difficulties with our trend analysis. We'll be back next month with more exciting data stories!"

    

    async def fetch_github_projects(self) -> List[Dict]:
        """Fetch trending GitHub repositories related to AI, ML, and patent analysis that are less than 6 months old and have at least 10 stars."""
        try:
            print("Fetching GitHub repositories...")

            # Add date filter for repositories created or updated in the last 6 months
            from datetime import datetime, timedelta
            six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            
            # Search for repositories created or pushed after the cutoff date and with at least 10 stars
            url = f"https://api.github.com/search/repositories?q=machine+learning+patent+created:>{six_months_ago}+stars:>=10&sort=stars&order=desc"
            headers = {"Accept": "application/vnd.github.v3+json"}

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"GitHub API error: {response.status_code}")
                return []

            data = response.json()
            projects = []

            for repo in data.get('items', [])[:10]:  # Get top 10, filter to best 5
                name = repo['name']
                url = repo['html_url']
                description = repo.get('description', '').strip() or "No description available"
                stars = repo['stargazers_count']
                created_at = repo.get('created_at', '')
                pushed_at = repo.get('pushed_at', '')
                
                # Skip repositories with empty descriptions
                if "no description" in description.lower():
                    continue

                # Ensure the repository has at least 10 stars (double-check)
                if stars < 10:
                    continue

                # Limit description length to 300 characters
                if len(description) > 300:
                    description = description[:300] + "..."

                projects.append({
                    'name': name,
                    'url': url,
                    'description': description,
                    'stars': stars,
                    'created_at': created_at,
                    'pushed_at': pushed_at
                })

                # Stop at first 5 valid projects
                if len(projects) >= 5:
                    break

            # If filtering was too strict, try again with relaxed criteria but still keep the minimum stars requirement
            if len(projects) < 3:
                print("Too few projects found, relaxing date filtering but keeping stars requirement...")
                # Try with a 1-year date range instead
                one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                url = f"https://api.github.com/search/repositories?q=machine+learning+patent+created:>{one_year_ago}+stars:>=10&sort=stars&order=desc"
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    additional_data = response.json()
                    
                    # Process additional data
                    for repo in additional_data.get('items', [])[:10]:
                        # Skip repos we already have
                        if any(p['url'] == repo['html_url'] for p in projects):
                            continue
                            
                        name = repo['name']
                        url = repo['html_url']
                        description = repo.get('description', '').strip() or "No description available"
                        stars = repo['stargazers_count']
                        
                        # Only add repos with at least 10 stars
                        if stars >= 10:
                            projects.append({
                                'name': name,
                                'url': url,
                                'description': description[:300] + "..." if len(description) > 300 else description,
                                'stars': stars,
                                'created_at': repo.get('created_at', ''),
                                'pushed_at': repo.get('pushed_at', '')
                            })
                        
                        if len(projects) >= 5:
                            break

            return projects

        except Exception as e:
            print(f"Error fetching GitHub projects: {str(e)}")
            return []



    def format_github_projects(self, projects: List[Dict]) -> str:
        """Format GitHub projects into accessible, practical descriptions."""
        if not projects:
            return "No GitHub projects found this month."

        content = "## Cool Tools & Projects You Might Want to Try\n\n"
        for project in projects:
            # Extract a more human-friendly name
            friendly_name = project['name'].replace('-', ' ').replace('_', ' ').title()
            
            # Create a more engaging description
            description = project['description'] if project['description'] else "A new open data project"
            
            # Add a use case suggestion if the description is short
            if len(description) < 100:
                description += f" This could be useful for your next data exploration project!"
                
            content += f"- **[{friendly_name}]({project['url']})** ⭐ {project['stars']} stars\n  {description}\n\n"
        
        # Add a community engagement prompt at the end
        content += "\n> **Have you tried any of these tools?** Share your experience at our next meetup!\n"
        return content

    def get_learning_resources(self) -> List[Dict]:
        """Fetch real learning resources instead of hardcoded ones."""
        try:
            print("Fetching learning resources...")
            resources = []

            # ✅ 1. Get latest NLP & AI review papers from arXiv
            arxiv_url = "http://export.arxiv.org/api/query?search_query=cat:cs.LG&start=0&max_results=3"
            response = requests.get(arxiv_url, timeout=10)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:3]:
                    title = entry.find("{http://www.w3.org/2005/Atom}title").text
                    link = entry.find("{http://www.w3.org/2005/Atom}id").text
                    resources.append({
                        "title": title,
                        "url": link,
                        "description": "Latest AI/ML research paper on arXiv."
                    })

            # # ✅ 2. Get top 3 trending courses from Coursera
            # coursera_url = "https://api.coursera.org/api/courses.v1?fields=name,description&limit=3"
            # response = requests.get(coursera_url, timeout=10)
            # if response.status_code == 200:
            #     data = response.json()
            #     for course in data.get('elements', [])[:3]:
            #         title = course.get('name', 'Unknown Course')
            #         description = course.get('description', 'No description available')
            #         resources.append({
            #             "title": title,
            #             "url": f"https://www.coursera.org/courses/{course['id']}",
            #             "description": description
            #         })

            return resources

        except Exception as e:
            print(f"Error fetching learning resources: {str(e)}")
            return []


    def format_learning_resources(self, resources: List[Dict]) -> str:
        """Format learning resources with difficulty levels and time commitments."""
        content = "## Learn Something New Today\n\n"
        
        # Add an engaging intro
        content += "_Looking to expand your data skills? Here are some resources our members are finding valuable:_\n\n"
        
        for resource in resources:
            # Add estimated time and difficulty based on the resource type
            if "course" in resource['title'].lower() or "introduction" in resource['title'].lower():
                difficulty = "Beginner-Friendly" 
                time_est = "4-6 hours"
            elif "deep dive" in resource['description'].lower() or "advanced" in resource['title'].lower():
                difficulty = "Advanced"
                time_est = "10+ hours"
            else:
                difficulty = "Intermediate"
                time_est = "2-3 hours"
                
            content += f"- **[{resource['title']}]({resource['url']})**\n  {resource['description']}\n"
            content += f"  _{difficulty} · Approx. {time_est}_\n\n"
        
        # Add a suggestion for members to contribute
        content += "\n> **Know a great resource?** Email us your suggestions for next month's newsletter!\n"
        return content
    
    def format_blog_posts(self, blog_posts: List[Dict]) -> str:
        """Format blog posts with quick-read indicators and key takeaways."""
        if not blog_posts:
            return "No recent blog posts available."

        content = "## Quick Reads for Data Enthusiasts\n\n"
        content += "_Stay up-to-date with these thought-provoking articles:_\n\n"
        
        for i, post in enumerate(blog_posts[:5]):
            # Clean up and shorten the summary
            summary = post['summary'].replace('\n', ' ').strip()
            if len(summary) > 120:
                summary = summary[:117] + "..."
                
            # Estimate read time (rough calculation)
            words = len(summary.split())
            read_time = max(1, words // 200)
            
            content += f"- **[{post['title']}]({post['link']})**\n"
            content += f"  {summary}\n"
            content += f"  _📚 {read_time}-minute read · From {post.get('source', 'The Web')}_\n\n"
            
            # Add a divider except after the last item
            if i < len(blog_posts[:5]) - 1:
                content += "---\n\n"
        
        return content
