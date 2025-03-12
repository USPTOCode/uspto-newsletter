import asyncio
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

from src.integrator.scheduler import NewsletterScheduler

async def main():
    try:
        print("Starting newsletter scheduler...")
        
        # Initialize scheduler with 24-hour scan interval
        scheduler = NewsletterScheduler(scan_interval_hours=24)
        
        # Run the scheduler
        await scheduler.run()
        
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
    except Exception as e:
        print(f"Error running scheduler: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 