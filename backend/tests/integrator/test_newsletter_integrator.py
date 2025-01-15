import pytest
import os
import json
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict
from unittest.mock import Mock, patch

from src.integrator.newsletter_integrator import NewsletterIntegrator

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for newsletter output."""
    output_dir = tmp_path / "newsletter_output"
    output_dir.mkdir()
    return str(output_dir)

@pytest.fixture
def mock_newsletter_agent():
    """Create a mock newsletter agent."""
    mock_agent = Mock()
    mock_agent.api_key = "mock-key"
    
    async def mock_compile_newsletter():
        return {
            'month': 'January 2025',
            'sections': {
                'emerging_trends': 'Sample trends content',
                'tools_and_projects': 'Sample tools content',
                'learning_resources': 'Sample learning content'
            },
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source_counts': {
                    'papers': 5,
                    'blog_posts': 3,
                    'github_projects': 4
                }
            }
        }
    
    mock_agent.compile_newsletter = mock_compile_newsletter
    return mock_agent

@pytest.fixture
def integrator(temp_output_dir, mock_newsletter_agent):
    """Create an integrator instance with a temporary output directory."""
    with patch('src.integrator.newsletter_integrator.NewsletterAgent', return_value=mock_newsletter_agent):
        return NewsletterIntegrator(output_dir=temp_output_dir)

@pytest.fixture
def sample_raw_newsletter() -> Dict:
    """Create a sample raw newsletter for testing."""
    return {
        'month': 'January 2025',
        'sections': {
            'emerging_trends': 'Sample trends content',
            'tools_and_projects': 'Sample tools content',
            'learning_resources': 'Sample learning content'
        },
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'source_counts': {
                'papers': 5,
                'blog_posts': 3,
                'github_projects': 4
            }
        }
    }

@pytest.mark.asyncio
async def test_generate_newsletter(integrator):
    """Test complete newsletter generation process."""
    newsletter = await integrator.generate_newsletter()
    
    assert newsletter is not None
    assert 'metadata' in newsletter
    assert 'sections' in newsletter
    assert 'display' in newsletter
    
    # Check metadata structure
    assert all(key in newsletter['metadata'] for key in ['month', 'generatedAt', 'sourceCounts'])
    
    # Check sections
    assert all(key in newsletter['sections'] for key in ['emergingTrends', 'toolsAndProjects', 'learningResources'])
    
    # Check display preferences
    assert all(key in newsletter['display'] for key in ['theme', 'layout', 'showMetadata'])

def test_transform_for_frontend(integrator, sample_raw_newsletter):
    """Test transformation of raw newsletter data to frontend format."""
    frontend_data = integrator._transform_for_frontend(sample_raw_newsletter)
    
    # Check structure
    assert 'metadata' in frontend_data
    assert 'sections' in frontend_data
    assert 'display' in frontend_data
    
    # Check sections have required fields
    for section in frontend_data['sections'].values():
        assert 'title' in section
        assert 'content' in section
        assert 'icon' in section

def test_save_newsletter(integrator, sample_raw_newsletter):
    """Test saving newsletter data to file."""
    # Save raw version
    raw_path = integrator._save_newsletter(sample_raw_newsletter, 'raw')
    assert os.path.exists(raw_path)
    
    # Save frontend version
    frontend_data = integrator._transform_for_frontend(sample_raw_newsletter)
    frontend_path = integrator._save_newsletter(frontend_data, 'frontend')
    assert os.path.exists(frontend_path)
    
    # Check file content
    with open(raw_path, 'r', encoding='utf-8') as f:
        saved_raw = json.load(f)
        assert saved_raw == sample_raw_newsletter

def test_get_latest_newsletter(integrator, sample_raw_newsletter):
    """Test retrieving the latest newsletter."""
    # Save multiple versions
    frontend_data = integrator._transform_for_frontend(sample_raw_newsletter)
    integrator._save_newsletter(frontend_data, 'frontend')
    
    # Wait a moment to ensure different timestamps
    import time
    time.sleep(1)
    
    # Save another version with slight modification
    frontend_data['metadata']['month'] = 'February 2025'
    integrator._save_newsletter(frontend_data, 'frontend')
    
    # Get latest
    latest = integrator.get_latest_newsletter()
    assert latest is not None
    assert latest['metadata']['month'] == 'February 2025'

def test_list_available_newsletters(integrator, sample_raw_newsletter):
    """Test listing available newsletter files."""
    # Save multiple newsletters
    frontend_data = integrator._transform_for_frontend(sample_raw_newsletter)
    integrator._save_newsletter(sample_raw_newsletter, 'raw')
    integrator._save_newsletter(frontend_data, 'frontend')
    
    available = integrator.list_available_newsletters()
    assert 'raw' in available
    assert 'frontend' in available
    assert len(available['raw']) == 1
    assert len(available['frontend']) == 1

def test_output_directory_creation(temp_output_dir):
    """Test that output directory is created if it doesn't exist."""
    # Remove the directory created by fixture
    shutil.rmtree(temp_output_dir)
    
    # Create integrator with mocked NewsletterAgent
    with patch('src.integrator.newsletter_integrator.NewsletterAgent') as mock_agent_class:
        mock_agent = Mock()
        mock_agent.api_key = "mock-key"
        mock_agent_class.return_value = mock_agent
        
        integrator = NewsletterIntegrator(output_dir=temp_output_dir)
        assert os.path.exists(temp_output_dir)

def test_error_handling(integrator):
    """Test error handling in various scenarios."""
    # Test with invalid raw data
    with pytest.raises(Exception):
        integrator._transform_for_frontend({})
    
    # Test with invalid file path
    assert integrator.get_latest_newsletter(version='nonexistent') is None
    
    # Test with empty directory
    available = integrator.list_available_newsletters()
    assert available == {'raw': [], 'frontend': []}