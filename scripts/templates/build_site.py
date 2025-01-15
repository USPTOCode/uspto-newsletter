import os
from pathlib import Path
import shutil
from datetime import datetime
import json
from typing import List, Dict

from jinja2 import Environment, PackageLoader, select_autoescape

class SiteBuilder:
    def __init__(self):
        self.env = Environment(
            loader=PackageLoader('scripts', 'templates'),
            autoescape=select_autoescape(['html'])
        )
        self.site_dir = Path('site')
        self.newsletters_dir = Path('newsletters')

    def build(self):
        """Build the complete site."""
        self._prepare_site_directory()
        newsletters = self._collect_newsletters()
        self._build_index(newsletters)
        self._copy_assets()

    def _prepare_site_directory(self):
        """Prepare the site directory."""
        if self.site_dir.exists():
            shutil.rmtree(self.site_dir)
        self.site_dir.mkdir()
        (self.site_dir / 'css').mkdir()
        (self.site_dir / 'newsletters').mkdir()

    def _collect_newsletters(self) -> List[Dict]:
        """Collect and sort all newsletters."""
        newsletters = []
        for file in self.newsletters_dir.glob('*.json'):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                newsletters.append({
                    'filename': file.stem,
                    'date': datetime.strptime(data['metadata']['generatedAt'], '%Y-%m-%dT%H:%M:%S.%f'),
                    'title': data['metadata']['month'],
                    'data': data
                })
        
        return sorted(newsletters, key=lambda x: x['date'], reverse=True)

    def _build_index(self, newsletters: List[Dict]):
        """Build the index page."""
        template = self.env.get_template('index.html')
        index_content = template.render(newsletters=newsletters)
        
        with open(self.site_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(index_content)

    def _copy_assets(self):
        """Copy static assets to the site directory."""
        css_src = Path('scripts/templates/css')
        css_dest = self.site_dir / 'css'
        
        if css_src.exists():
            shutil.copytree(css_src, css_dest, dirs_exist_ok=True)

if __name__ == '__main__':
    builder = SiteBuilder()
    builder.build()