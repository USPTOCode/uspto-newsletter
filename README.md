# USPTO Newsletter Project

## Structure
- `backend/`: Python backend for newsletter generation
- `frontend/`: React frontend for newsletter display
- `scripts/`: Utility scripts

The **USPTO Newsletter** project is a tool designed to streamline the generation and formatting of newsletters for the USPTO Open Data Enthusiasts Club. This repository provides a robust pipeline for creating newsletters in multiple formats, including JSON, HTML, and plain-text email, while supporting modular integration with data sources and customizable templates.

## Features

- **Multi-format Output**: Generates newsletters in multiple formats: JSON, HTML, and email.
- **Dynamic Content Integration**: Easily integrates dynamic data such as research papers, blog posts, and GitHub projects.
- **Customizable Templates**: Leverages Jinja2 templates for HTML rendering.
- **Extensible Design**: Modular design allows easy addition of new formats and features.
- **Responsive and Stylish Layout**: CSS-enhanced templates ensure a professional look and feel.

## Requirements

- Python 3.8+
- pip or conda for dependency management

### Python Libraries
The following libraries are required and can be installed via `requirements.txt`:

- `Jinja2`
- `markdown`
- `python-dotenv`
- `aiohttp`
- `json`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/USPTOCode/uspto-newsletter.git
   cd uspto-newsletter
   ```

2. Initialize project:
   ```bash
   scripts/setup.py 
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Create a `.env` file in the `backend/` directory.
   - Add the following variables:
     ```
     # OpenAI API Key (if required)
     OPENAI_API_KEY=your_api_key_here

     # Output directory for generated files
     OUTPUT_DIR=./data/generated/newsletters
     ```

### Generating a Newsletter

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Run the main script:
   ```bash
   python scripts/generate_newsletter.py
   ```

3. The generated newsletter will be saved in the `data/generated/newsletters` directory in the specified formats.

### Customizing Templates

1. Templates are located in `src/integrator/templates/`.
2. Modify `newsletter.html` to change the layout and style of the HTML newsletter.
3. Use the included CSS file or link your own for styling adjustments.

### Adding Content

To include new data sources:
1. Extend the `generate_newsletter` function in `src/integrator/newsletter_integrator.py`.
2. Integrate your data source, ensuring it conforms to the expected `data` dictionary structure.

## Directory Structure

```plaintext
uspto-newsletter/
├── backend/
│   ├── scripts/
│   │   └── generate_newsletter.py  # Main script
│   ├── src/
│   │   ├── integrator/            # Core logic and templates
│   │   │   ├── templates/         # HTML templates
│   │   │   └── newsletter_integrator.py
│   │   └── formatter.py           # Handles formatting logic
│   └── data/                      # Generated newsletters
├── README.md                      # Documentation
├── requirements.txt               # Python dependencies
└── .env.example                   # Example environment variables
```

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute this software in accordance with the license terms.

