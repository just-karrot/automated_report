# AI-Powered Event Report Generator

A Flask-based web application that generates professional college event reports using AI (Groq API).

## Features

- 🤖 AI-powered content generation with category-specific prompts (Technical, Cultural, Sports)
- 📄 Professional report formatting with CO-PO mapping tables
- 📊 Assessment/Feedback form generation
- 📥 Export to Word (.doc) format for manual editing
- 🖨️ Print to PDF functionality
- 📱 Clean, minimalist UI with live preview

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: Groq API (openai/gpt-oss-120b model)
- **Templating**: Jinja2

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd report_a3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage

1. **Enter API Key**: Input your Groq API key (or set it in .env)
2. **Select Category**: Choose event type (Technical/Cultural/Sports)
3. **Describe Event**: Provide event details in the description field
4. **Generate**: Click "Generate Full Report" to create AI-powered content
5. **Edit**: Modify generated content in the collapsible sections
6. **Preview**: Click "Update Preview" to see the formatted report
7. **Export**: Use "Export to Word" or "Print / PDF" buttons

## Project Structure

```
report_a3/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
├── static/
│   └── images/
│       └── header.jpg    # College header image
├── templates/
│   ├── index.html        # Main UI
│   └── schema.html       # Report template
└── README.md             # This file
```

## Configuration

### Event Categories

The application supports three event categories with tailored AI prompts:
- **Technical**: Emphasizes industry trends, career relevance, skill development
- **Cultural**: Focuses on artistic expression, diversity, student talent
- **Sports**: Highlights competition format, sportsmanship, teamwork

### Report Sections

Generated reports include:
- Event metadata (name, date, organizers, coordinators)
- Learning outcomes (CO1-CO4)
- CO-PO mapping table
- Assessment/Feedback form
- Introduction, details, and description
- Session overview and key highlights
- Conclusion
- Attendance list

## API Key

Get your Groq API key from: https://console.groq.com/

## License

MIT License

## Support

For issues or questions, please open an issue on GitHub.
