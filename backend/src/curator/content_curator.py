import logging
from typing import List, Dict, Any
import re
from collections import Counter


class ContentCurator:
    """Curates content for the newsletter, selecting the most relevant and engaging items."""
    
    def __init__(self):
        """Initialize the content curator."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='curator.log'
        )
        self.logger = logging.getLogger('ContentCurator')
        
        # Keywords relevant to open data enthusiasts
        self.relevant_keywords = [
            'open data', 'data visualization', 'data storytelling', 'public data',
            'data journalism', 'citizen science', 'community data', 'data ethics',
            'data literacy', 'open government', 'data democratization', 'data commons',
            'open source', 'data sharing', 'civic tech', 'data for good',
            'data innovation', 'accessible data', 'data transparency'
        ]
    
    def score_relevance(self, text: str) -> float:
        """Score the relevance of text based on keyword presence and readability."""
        if not text:
            return 0.0
        
        text = text.lower()
        
        # Count keyword matches
        keyword_score = sum(1 for keyword in self.relevant_keywords if keyword in text)
        
        # Basic readability assessment (prefer shorter sentences and paragraphs)
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        readability_score = 1.0 if avg_sentence_length < 20 else 0.5
        
        # Check for engaging elements (questions, examples, analogies)
        engagement_score = 0
        if '?' in text:
            engagement_score += 0.5
        if 'example' in text or 'instance' in text or 'case study' in text:
            engagement_score += 0.5
        if 'like' in text or 'similar to' in text or 'imagine' in text:
            engagement_score += 0.5
        
        # Calculate final score
        return (keyword_score * 0.5) + (readability_score * 0.3) + (engagement_score * 0.2)
    
    def curate_blog_posts(self, posts: List[Dict[str, Any]], max_posts: int = 5) -> List[Dict[str, Any]]:
        """Curate blog posts based on relevance and engagement potential."""
        try:
            if not posts:
                return []
            
            # Score each post
            scored_posts = []
            for post in posts:
                # Combine title and summary for scoring
                content = f"{post.get('title', '')} {post.get('summary', '')}"
                score = self.score_relevance(content)
                
                # Consider recency as a factor
                if 'published' in post and post['published']:
                    # Simple boost for recent posts
                    score += 0.2
                
                scored_posts.append((score, post))
            
            # Sort by score (descending) and take top posts
            sorted_posts = [post for _, post in sorted(scored_posts, key=lambda x: x[0], reverse=True)]
            curated_posts = sorted_posts[:max_posts]
            
            self.logger.info(f"Curated {len(curated_posts)} blog posts from {len(posts)} total")
            return curated_posts
            
        except Exception as e:
            self.logger.error(f"Error curating blog posts: {e}")
            # Fall back to the original posts if curation fails
            return posts[:max_posts]
    
    def curate_github_projects(self, projects: List[Dict[str, Any]], max_projects: int = 5) -> List[Dict[str, Any]]:
        """Curate GitHub projects based on relevance, stars, and description quality."""
        try:
            if not projects:
                return []
            
            # Score each project
            scored_projects = []
            for project in projects:
                base_score = self.score_relevance(f"{project.get('name', '')} {project.get('description', '')}")
                
                # Adjust score based on stars (logarithmic scale to prevent domination by very popular projects)
                star_score = min(1.0, (project.get('stars', 0) / 1000))
                
                # Penalize projects with very short descriptions
                description_length = len(project.get('description', ''))
                description_score = 0.0 if description_length < 10 else (
                    0.5 if description_length < 50 else 1.0
                )
                
                final_score = (base_score * 0.6) + (star_score * 0.2) + (description_score * 0.2)
                scored_projects.append((final_score, project))
            
            # Sort by score (descending) and take top projects
            sorted_projects = [project for _, project in sorted(scored_projects, key=lambda x: x[0], reverse=True)]
            curated_projects = sorted_projects[:max_projects]
            
            self.logger.info(f"Curated {len(curated_projects)} GitHub projects from {len(projects)} total")
            return curated_projects
            
        except Exception as e:
            self.logger.error(f"Error curating GitHub projects: {e}")
            # Fall back to the original projects if curation fails
            return projects[:max_projects]
    
    def suggest_themes(self, content_items: List[Dict[str, Any]]) -> List[str]:
        """Suggest potential newsletter themes based on common topics in content."""
        try:
            # Extract all text content
            all_text = " ".join([
                f"{item.get('title', '')} {item.get('description', '')} {item.get('summary', '')}"
                for item in content_items
            ]).lower()
            
            # Extract potential theme keywords
            words = re.findall(r'\b\w+\b', all_text)
            word_counts = Counter(words)
            
            # Filter out common stop words
            stop_words = {'and', 'the', 'to', 'of', 'in', 'for', 'a', 'is', 'with', 'that', 'on', 'as', 'at', 'by'}
            theme_words = [(word, count) for word, count in word_counts.most_common(20) 
                           if word not in stop_words and len(word) > 3]
            
            # Suggest themes based on frequent words
            themes = []
            if theme_words:
                top_words = [word for word, _ in theme_words[:5]]
                themes = [
                    f"Exploring {top_words[0].title()} in Open Data",
                    f"The Future of {top_words[1].title()}",
                    f"{top_words[2].title()} for Everyone: Breaking Down Barriers",
                    f"Innovation through {top_words[0].title()} and {top_words[1].title()}",
                    f"Community-Driven {top_words[3].title()}: Success Stories"
                ]
            
            # Add some generic themes as fallbacks
            default_themes = [
                "Data for Good: Making a Difference",
                "Democratizing Data: Tools and Techniques",
                "The Open Data Revolution",
                "Data Storytelling: Finding the Signal in the Noise",
                "Building Community Through Shared Data"
            ]
            
            return (themes or default_themes)[:3]
            
        except Exception as e:
            self.logger.error(f"Error suggesting themes: {e}")
            return ["The Open Data Explorer", "Data Insights This Month", "Community Data Spotlight"]


# Example usage:
"""
curator = ContentCurator()

# Curate blog posts
curated_posts = curator.curate_blog_posts(all_blog_posts)

# Curate GitHub projects
curated_projects = curator.curate_github_projects(all_github_projects)

# Suggest themes
all_content = curated_posts + curated_projects
suggested_themes = curator.suggest_themes(all_content)
"""