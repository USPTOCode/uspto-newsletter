import asyncio
import os
from datetime import datetime
from pathlib import Path
import sys

# Get the absolute path to the backend directory
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from src.integrator.newsletter_integrator import NewsletterIntegrator

def generate_test_content():
    """Generate sample newsletter content for testing."""
    return {
        'metadata': {
            'month': 'January 2025',
            'generatedAt': datetime.now().isoformat(),
            'source_counts': {
                'papers': 3,
                'blog_posts': 2,
                'github_projects': 2
            }
        },
        'sections': {
            'emerging_trends': {
                'title': 'Emerging Trends in Data Science',
                'content': """
## Machine Learning in Patent Analysis

Recent developments in machine learning are transforming patent analysis:

* **Deep Learning for Classification**: New models achieve 95% accuracy in patent classification
* **Natural Language Processing**: Improved semantic analysis for prior art search
* **Computer Vision**: Automated analysis of patent drawings and diagrams

### Key Insights

1. Transfer learning models are reducing training time by 60%
2. Multi-modal analysis combining text and images shows promising results
3. Smaller, more efficient models are making deployment easier

```python
# Example of efficiency gains
def analyze_patent(text, images):
    results = ml_model.process(text, images)
    return results.classification
```

> "The combination of NLP and computer vision is revolutionizing how we analyze patents" - Recent Research Paper
                """
            },
            'tools_and_projects': {
                'title': 'Innovative Tools & Projects',
                'content': """
## Featured Tools

### 1. PatentBERT
A new open-source tool for patent analysis using BERT models:
- Fine-tuned on patent data
- Supports 5 languages
- Easy integration with existing workflows

### 2. DataViz Suite
Interactive visualization tools specifically for patent data:
- Network graphs
- Technology landscapes
- Citation analysis

## Recent Updates
* Added support for bulk processing
* Improved memory efficiency
* New API endpoints for integration
                """
            },
            'learning_resources': {
                'title': 'Learning & Development',
                'content': """
## Learning Resources

### Online Courses
1. [Patent Analysis Fundamentals](https://example.com)
2. [Machine Learning for IP Professionals](https://example.com)
3. [Data Science in Patent Law](https://example.com)

### Recommended Reading
* "Modern Patent Analysis" - New publication covering latest techniques
* "Machine Learning Applications in IP" - Comprehensive guide
* "Data Science for Patents" - Practical handbook

### Upcoming Webinars
- Jan 20: Introduction to Patent Analytics
- Feb 5: Advanced ML Techniques
- Feb 15: Visualization Best Practices
                """
            }
        }
    }

async def main():
    try:
        print("Starting test newsletter generation...")
        
        # Initialize integrator
        integrator = NewsletterIntegrator()
        
        # Generate test content
        newsletter = generate_test_content()
        
        # Save newsletter
        test_file = 'test_newsletter.html'
        html_path = integrator.save_newsletter_as(newsletter, 'html', test_file)
        
        print(f"\nTest newsletter generated successfully!")
        print(f"HTML version saved to: {html_path}")
        print("\nPlease open the file in a browser to verify the formatting.")
        
    except Exception as e:
        print(f"Error generating test newsletter: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())