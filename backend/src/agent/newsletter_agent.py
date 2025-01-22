import os
import logging
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
            print("Fetching arXiv papers...")
            papers = await self.fetch_arxiv_papers()
            print(f"Fetched {len(papers)} papers")
            
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
                        'papers': len(papers),
                        'blog_posts': len(blog_posts),
                        'github_projects': 0
                    }
                },
                'sections': {
                    'emerging_trends': {
                        'title': 'Emerging Trends in Data Science',
                        'content': emerging_trends
                    },
                    'tools_and_projects': {
                        'title': 'Tools and Projects',
                        'content': '# Coming Soon\n\nTools and projects section will be implemented next.'
                    },
                    'learning_resources': {
                        'title': 'Learning Resources',
                        'content': '# Coming Soon\n\nLearning resources section will be implemented next.'
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
            feeds = feeds = [
    'https://www.data.gov/meta/feed/',  # Data.gov: U.S. government's open data portal
    'https://data.gov.uk/feed',  # Data.gov.uk: UK government's open data portal
    'https://ec.europa.eu/europeandataportal/en/news/rss',  # European Data Portal: EU's open data portal
    'https://opendata.blog/feed/',  # Open Data Blog: Articles on open data and technology trends
    'https://opendatascience.com/feed/',  # Open Data Science: News on data science and AI
    'https://blogs.worldbank.org/opendata/rss',  # World Bank Data Blog: Global development data stories
    'https://opendatawatch.com/feed/',  # Open Data Watch Blog: Open data policies and practices
    'https://www.odi.org/feed',  # Open Data Institute (ODI): Resources on open data
    'https://blog.okfn.org/feed/',  # Open Knowledge Foundation Blog: Promoting openness in various fields
    'https://www.kdnuggets.com/feed',  # KDnuggets: Data science and machine learning articles
    'https://www.datasciencecentral.com/main/feed',  # Data Science Central: Resources for data science practitioners
    'https://fivethirtyeight.com/all/feed',  # FiveThirtyEight: Data-driven journalism
    'https://insidebigdata.com/feed/',  # InsideBIGDATA: News on big data and AI
    'https://www.smartdatacollective.com/feed/',  # SmartData Collective: Expert opinions on data management
    'https://towardsdatascience.com/feed',  # Towards Data Science: Articles on data science concepts
    'https://datafloq.com/feed/',  # Datafloq: Information on big data and AI
    'https://opendatainception.io/feed/',  # Open Data Inception: List of open data portals
    'https://opendatacharter.net/feed/',  # Open Data Charter: Principles for open data policies
    'https://blog.datawrapper.de/feed/',  # Datawrapper Blog: Tutorials on data visualization
    'https://flowingdata.com/feed/',  # FlowingData: Exploring data through visualization
    'https://informationisbeautiful.net/feed/',  # Information is Beautiful: Data visualizations
    'https://www.datacamp.com/community/blog.rss',  # DataCamp Community: Tutorials on data science
    'https://www.r-bloggers.com/feed/',  # R-Bloggers: Content related to R programming
    'https://simplystatistics.org/feed/',  # Simply Statistics: Discussions on statistics and data science
    'https://statmodeling.stat.columbia.edu/feed/',  # Statistical Modeling, Causal Inference, and Social Science
    'https://dataelixir.com/feed',  # Data Elixir: Weekly newsletter of curated data science news
    'https://dataskeptic.com/feed',  # Data Skeptic: Podcasts and articles on data science topics
    'https://pudding.cool/feed.xml',  # The Pudding: Visual essays explaining ideas with data
    'https://ourworldindata.org/atom.xml',  # Our World in Data: Research and data visualizations on global issues
    'https://opensource.googleblog.com/feeds/posts/default',  # Google Open Source Blog: Updates on open source projects
    'https://cloudblogs.microsoft.com/opensource/feed/',  # Microsoft Open Source Blog: Insights on open source practices
    'https://aws.amazon.com/blogs/opensource/feed/',  # AWS Open Source Blog: Articles on open source technologies
    'https://openlogic.com/blog/feed',  # OpenLogic Blog: Guidance on open source software
    'https://cncf.io/feed/',  # Cloud Native Computing Foundation Blog: Updates on open source cloud technologies
    'https://instaclustr.com/feed/',  # Instaclustr Blog: Developments in open source technologies
    'https://fosspost.org/feed/',  # FOSS Post: Articles on Linux and open source software
    'https://blog.fossasia.org/feed/',  # FOSSASIA Blog: Open source development in Asia
    'https://opensource.org/news/feed',  # Open Source Initiative: News on open source software
    'https://blog.rasa.com/rss/',  # Rasa Blog: Insights on conversational AI and open source
    'https://swagger.io/blog/feed/',  # Swagger Blog: API design and development
    'https://developers.facebook.com/blog/opensource/rss',  # Facebook Open Source: Updates on open source projects
    'https://blog.twitter.com/engineering/en_us/topics/opensource.rss',  # Twitter Engineering: Open source contributions
    'https://developer.ibm.com/blogs/category/open-source/feed/',  # IBM Developer: Open source development
    'https://blogs.vmware.com/opensource/feed/',  # VMware Open Source Blog: Project news and updates
    'https://www.zdnet.com/topic/open-source/rss.xml',  # ZDNet Open Source: News and analysis on open source
    'https://about.gitlab.com/blog/rss/',  # GitLab Blog: Updates on open source development
    'https://www.percona.com/blog/feed/',  # Percona Community Blog: Open source database insights
    'https://www.rudderstack.com/blog/rss.xml',  # RudderStack Blog: Customer data infrastructure and analytics
    'https://engineering.fb.com/feed/',  # Meta Engineering: Open source project releases
    'https://www.snowflake.com/blog/feed/',  # Snowflake Blog: Data warehousing and cloud computing
    'https://theseattledataguy.com/feed/',  # Seattle Data Guy Blog: Analytics and data science implementation
    'https://www.precisely.com/blog/feed',  # Precisely Blog: Data integration and quality
    'https://towardsdatascience.com/tagged/data-engineering/rss',  # Data Engineering in Towards Data Science
    'https://aws.amazon.com/blogs/big-data/feed/',  # AWS Big Data Blog: Updates on big data services
    'https://databricks.com/feed',  # Databricks Blog: Product updates and best practices
    'https://eng.uber.com/feed/',  # Uber Engineering Blog: AI and machine learning technologies
    'https://medium.com/feed/@Pinterest_Engineering',  # Pinterest Engineering Blog: Innovations in engineering
    'https://engineeringblog.yelp.com/feed.xml',  # Yelp Engineering Blog: Technical insights and updates
    'https://medium.com/feed/@AirbyteHQ',  # Airbyte Blog: Open-source data integration
    'https://engineering.atspotify.com/feed/',  # Spotify Engineering: Data engineering and infrastructure
    'https://www.infoq.com/data-eng/news.atom',  # InfoQ Data Engineering: News and articles
    'https://www.datacamp.com/blog/category/data-engineering/rss',  # DataCamp Data Engineering Blog
            ]
            
            posts = []
            for feed_url in feeds:
                try:
                    print(f"Checking feed: {feed_url}")
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:2]:  # Get 2 most recent from each
                        posts.append({
                            'title': entry.title,
                            'summary': entry.get('summary', ''),
                            'link': entry.link,
                            'source': feed.feed.title,
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
        """Generate the emerging trends section using GPT-4."""
        try:
            if not papers:
                print("No papers found to analyze")
                return "# No Recent Papers Found\n\nUnable to fetch recent research papers for analysis."

            print("Creating GPT prompt...")
            prompt = f"""Analyze these recent research papers and identify emerging trends in data science and patent analysis.
            Focus on implications for patent professionals and data scientists.

            Recent Papers:
            {self._format_papers_for_prompt(papers)}

            Generate a comprehensive analysis in markdown format that includes:
            1. Overview of key emerging trends
            2. Specific applications to patent analysis
            3. Future implications for USPTO and patent professionals
            4. Code examples or technical concepts where relevant

            Format the content with clear headers, bullet points, and emphasis on key concepts.
            Include relevant code snippets if applicable.
            """

            print("Sending request to OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert data scientist specializing in patent analysis and USPTO systems. Your task is to analyze research papers and identify emerging trends relevant to patent professionals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            print("Successfully received GPT response")
            self.logger.info("Successfully generated emerging trends section")
            return content

        except Exception as e:
            print(f"Error in generate_trends_section: {str(e)}")
            self.logger.error(f"Error generating trends section: {e}")
            return "# Error Generating Trends\n\nThere was an error analyzing the trends. Please try again later."

    def _format_papers_for_prompt(self, papers: List[Dict]) -> str:
        """Format papers into a string for the GPT prompt."""
        formatted = ""
        for i, paper in enumerate(papers, 1):
            formatted += f"\nPaper {i}:\n"
            formatted += f"Title: {paper['title']}\n"
            formatted += f"Summary: {paper['summary']}\n"
            formatted += f"Authors: {', '.join(paper['authors'])}\n"
            formatted += f"Published: {paper['published']}\n"
            formatted += "-" * 50 + "\n"
        return formatted