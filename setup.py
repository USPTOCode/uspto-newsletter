import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_directory(path):
    """Create directory if it doesn't exist"""
    Path(path).mkdir(parents=True, exist_ok=True)

def create_file(path, content=''):
    """Create file with optional content"""
    with open(path, 'w') as f:
        f.write(content)

def setup_project(base_path):
    """Set up the complete project structure"""
    base_dir = Path(base_path) / 'uspto-newsletter'
    
    # Create root directory
    create_directory(base_dir)
    
    # Backend structure
    backend_dir = base_dir / 'backend'
    create_directory(backend_dir / 'src' / 'agent')
    create_directory(backend_dir / 'src' / 'integrator')
    create_directory(backend_dir / 'src' / 'utils')
    create_directory(backend_dir / 'tests')
    create_directory(backend_dir / 'data' / 'generated')
    create_directory(backend_dir / 'data' / 'cache')
    create_directory(backend_dir / 'config')
    
    # Frontend structure
    frontend_dir = base_dir / 'frontend'
    create_directory(frontend_dir / 'src' / 'components' / 'NewsletterViewer')
    create_directory(frontend_dir / 'src' / 'components' / 'common')
    create_directory(frontend_dir / 'src' / 'hooks')
    create_directory(frontend_dir / 'src' / 'utils')
    create_directory(frontend_dir / 'src' / 'styles')
    create_directory(frontend_dir / 'public' / 'assets' / 'images')
    
    # Scripts directory
    create_directory(base_dir / 'scripts')
    
    # Create necessary files
    
    # Backend files
    create_file(backend_dir / 'requirements.txt', '''openai>=1.0.0
requests>=2.31.0
pandas>=2.0.0
feedparser>=6.0.0
beautifulsoup4>=4.12.0
arxiv>=1.4.0
python-dotenv>=1.0.0
pytest>=7.4.0
''')

    create_file(backend_dir / 'README.md', '''# USPTO Newsletter Backend

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate virtual environment: `.\venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy .env.example to .env and fill in required values

## Development
- Run tests: `pytest`
- Generate newsletter: `python -m src.main`
''')

    # Frontend files
    package_json_content = '''{
  "name": "uspto-newsletter-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@heroicons/react": "^2.0.18",
    "tailwindcss": "^3.3.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}'''
    
    create_file(frontend_dir / 'package.json', package_json_content)
    create_file(frontend_dir / 'vite.config.js', '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
''')

    create_file(frontend_dir / 'README.md', '''# USPTO Newsletter Frontend

## Setup
1. Install dependencies: `npm install`
2. Start development server: `npm run dev`
3. Build for production: `npm run build`
''')

    # Root files
    create_file(base_dir / '.gitignore', '''# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Node
node_modules/
dist/
.env.local

# IDE
.vscode/
.idea/

# Project specific
backend/data/generated/*
backend/data/cache/*
!backend/data/generated/.gitkeep
!backend/data/cache/.gitkeep
''')

    create_file(base_dir / 'README.md', '''# USPTO Newsletter Project

## Structure
- `backend/`: Python backend for newsletter generation
- `frontend/`: React frontend for newsletter display
- `scripts/`: Utility scripts

## Setup
1. Run `scripts/setup.py` to initialize project
2. Follow setup instructions in backend/README.md
3. Follow setup instructions in frontend/README.md
''')

    create_file(base_dir / 'docker-compose.yml', '''version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    env_file:
      - ./backend/.env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
''')

    print(f"Project structure created at: {base_dir}")
    return str(base_dir)

def setup_virtual_environment(project_dir):
    """Set up Python virtual environment"""
    backend_dir = Path(project_dir) / 'backend'
    os.chdir(backend_dir)
    
    print("Setting up Python virtual environment...")
    subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    
    if os.name == 'nt':  # Windows
        pip_path = backend_dir / 'venv' / 'Scripts' / 'pip'
    else:  # Unix/Linux
        pip_path = backend_dir / 'venv' / 'bin' / 'pip'
    
    subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'])

def setup_frontend(project_dir):
    """Set up frontend dependencies"""
    frontend_dir = Path(project_dir) / 'frontend'
    os.chdir(frontend_dir)
    
    print("Setting up frontend dependencies...")
    subprocess.run(['npm', 'install'])

def main():
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = r'C:\Development'
    
    try:
        project_dir = setup_project(base_path)
        setup_virtual_environment(project_dir)
        setup_frontend(project_dir)
        print("\nProject setup completed successfully!")
        print(f"\nNext steps:")
        print(f"1. cd {project_dir}")
        print(f"2. Create and configure backend/.env")
        print(f"3. Start backend: cd backend && .\\venv\\Scripts\\activate && python -m src.main")
        print(f"4. Start frontend: cd frontend && npm run dev")
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()