# AI-Powered Report Automation Suite

A Flask-based web application that generates professional reports using AI (Groq API). Supports multiple formats including Event Reports and high-depth Project Reports.

## Features

- **Multi-Format Support**: Generate Event Reports, Subject Reports, and detailed Project Reports.
- **High-Depth Generation**: Uses parallel multi-pass AI generation (1 metadata pass + 6 content chapters) to produce 20+ page Project Reports.
- **Parallel Processing**: Utilizes `concurrent.futures` for simultaneous chapter generation.
- **Professional Formatting**: Replicates specific institutional formatting styles (Times New Roman, specific alignments, bolding).
- **Reliable Export**: High-fidelity export to Microsoft Word (.docx) using `python-docx` with proper layout preservation.
- **Brutalist UI**: Modern, responsive UI with a distinct brutalist aesthetic (sidebar navigation, sharp corners).
- **Print to PDF**: Built-in support for browser-based PDF printing.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3 (Vanilla), Vanilla JavaScript
- **AI**: Groq API (`openai/gpt-oss-120b`)
- **Export**: `python-docx`
- **Concurrency**: `concurrent.futures.ThreadPoolExecutor`
- **Templating**: Jinja2

## Installation

1. Clone the repository:
```bash
git clone https://github.com/just-karrot/automated_report.git
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

## Project Structure

```
report_a3/
├── app.py                 # Main Flask application with multi-pass logic
├── requirements.txt       # Python dependencies (includes python-docx)
├── static/
│   └── images/            # Assets (header.jpg, pce_logo.jpg)
├── templates/
│   ├── index.html         # Responsive UI with format toggles
│   ├── schema.html        # Event Report template
│   ├── project_schema.html # Project Report template
│   └── subject_schema.html # Subject Report template
└── README.md              # This file
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
