import os
import io
import base64
import json
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_full_report():
    data = request.json
    api_key = data.get('api_key') or os.getenv('GROQ_API_KEY')
    description = data.get('description')
    event_category = data.get('event_category', 'technical')
    report_format = data.get('report_format', 'event_report')

    if not api_key:
        return jsonify({'error': 'API Key is required'}), 400
    
    if not description:
        return jsonify({'error': 'Event description is required'}), 400

    # Project Report specific prompt and schema
    if report_format == 'project_report':
        system_prompt = (
            "You are a senior engineering student writing a professional, academic project report. "
            "Your tone is formal, technical, and precise. "
            "Write highly detailed and coherent sections for an engineering project dissertation. "
            "For each chapter, you must provide a relevant, technical title and a comprehensive content body. "
            "The content should include technical explanations, methodologies, and academic context. "
            "You MUST also generate a list of 5-8 credible academic references (IEEE or APA style) "
            "relevant to the project topic. "
            "Strictly follow the provided JSON schema. Use valid HTML structure (like <br> or <b>) if necessary for emphasis, but no raw markdown."
        )
        
        json_schema = {
            "name": "project_report_schema",
            "strict": False,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Full formal title of the project"},
                    "project_type": {"type": "string", "description": "Type of project (e.g., Major Project, Research Project)"},
                    "branch": {"type": "string", "description": "Academic branch (e.g., Computer Science & Engineering)"},
                    "session": {"type": "string", "description": "Academic session (e.g., Jan-June, 2026)"},
                    "professor_name": {"type": "string", "description": "Full name of the supervisor/professor"},
                    "professor_designation": {"type": "string", "description": "Designation (e.g., Assistant Professor)"},
                    "certificate_students_text": {"type": "string", "description": "Names and reg numbers for certificate"},
                    "students": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "reg_no": {"type": "string"},
                                "roll_no": {"type": "string"}
                            }
                        }
                    },
                    "abstract_title": {"type": "string", "default": "ABSTRACT"},
                    "abstract_content": {"type": "string"},
                    "keywords": {"type": "string"},
                    "chapter_1_title": {"type": "string", "default": "CHAPTER 1: INTRODUCTION"},
                    "chapter_1_content": {"type": "string"},
                    "chapter_2_title": {"type": "string", "default": "CHAPTER 2: LITERATURE SURVEY"},
                    "chapter_2_content": {"type": "string"},
                    "chapter_3_title": {"type": "string", "default": "CHAPTER 3: SYSTEM DESIGN"},
                    "chapter_3_content": {"type": "string"},
                    "chapter_4_title": {"type": "string", "default": "CHAPTER 4: IMPLEMENTATION"},
                    "chapter_4_content": {"type": "string"},
                    "chapter_5_title": {"type": "string", "default": "CHAPTER 5: RESULTS AND DISCUSSION"},
                    "chapter_5_content": {"type": "string"},
                    "chapter_6_title": {"type": "string", "default": "CHAPTER 6: CONCLUSION"},
                    "chapter_6_content": {"type": "string"},
                    "references": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["title", "project_type", "students"]
            }
        }
    else:
        # Category-specific system prompts for Event Report
        system_prompts = {
            "cultural": (
                "You are a professional report writer for a college cultural event. "
                "Write in a warm, lighthearted, and friendly yet formal tone. "
                "Celebrate the artistic and creative spirit of the event. "
                "Use vivid, expressive language to capture the energy and enthusiasm of performances, "
                "competitions, and celebrations. Highlight cultural diversity, student talent, "
                "and the joy of participation. The report should feel inviting and uplifting "
                "while maintaining academic formality. "
                "Generate a highly detailed and coherent formal event report strictly matching "
                "the provided JSON schema based on the user's description. "
                "Use valid HTML structure (like <br> or <b>) if necessary for emphasis, but no raw markdown."
            ),
            "sports": (
                "You are a professional report writer for a college sports event. "
                "Focus on clearly conveying the format, rules, and structure of the competition. "
                "Use an energetic and factual tone that captures the competitive spirit. "
                "Emphasize sportsmanship, teamwork, physical fitness, and fair play. "
                "Mention specific match formats, scores, winners, and participation statistics "
                "where possible. The report should read like a well-structured sports bulletin — "
                "precise, informative, and motivating. "
                "Generate a highly detailed and coherent formal event report strictly matching "
                "the provided JSON schema based on the user's description. "
                "Use valid HTML structure (like <br> or <b>) if necessary for emphasis, but no raw markdown."
            ),
            "technical": (
                "You are a professional report writer for a college technical event. "
                "Project technical expertise and authority in the subject matter. "
                "Weave in references to current industry trends, job market demands, "
                "and how the skills learned align with professional career paths. "
                "Use precise technical terminology where appropriate. "
                "Emphasize hands-on learning, innovation, problem-solving, and skill development. "
                "The report should convey that participants gained tangible, career-relevant knowledge. "
                "Generate a highly detailed and coherent formal event report strictly matching "
                "the provided JSON schema based on the user's description. "
                "Use valid HTML structure (like <br> or <b>) if necessary for emphasis, but no raw markdown."
            )
        }
        system_prompt = system_prompts.get(event_category, system_prompts["technical"])
        json_schema = {
            "name": "full_event_report_schema",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "event_name": {"type": "string", "description": "The formal name of the event"},
                    "event_date": {"type": "string", "description": "The date the event was held (e.g., 6 October, 2025)"},
                    "event_duration": {"type": "string", "description": "The duration of the event (e.g., 3 Hours)"},
                    "event_type": {"type": "string", "description": "The type of activity (e.g., Technical Workshop)"},
                    "organized_by": {"type": "string", "description": "The organizing entities, e.g. AWS Cloud Club x Coding Club"},
                    "coordinators": {"type": "string", "description": "List of coordinators, format with <br> for newlines"},
                    "learning_outcome_1": {"type": "string", "description": "1st learning outcome (CO1)"},
                    "learning_outcome_2": {"type": "string", "description": "2nd learning outcome (CO2)"},
                    "learning_outcome_3": {"type": "string", "description": "3rd learning outcome (CO3)"},
                    "learning_outcome_4": {"type": "string", "description": "4th learning outcome (CO4)"},
                    "introduction": {"type": "string", "description": "A 1-2 paragraph formal introduction to the event"},
                    "details_of_the_event": {"type": "string", "description": "A detailed 2 paragraph explanation of what the event was about and objective"},
                    "description_of_the_event": {"type": "string", "description": "A paragraph explaining the flow of the event, speakers, and activities"},
                    "beneficiaries": {"type": "string", "description": "Who benefited from the event (e.g., Students from 2nd and 3rd year)"},
                    "session_overview": {"type": "string", "description": "A paragraph summarizing the content of the sessions"},
                    "key_highlights": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of 4-6 key highlights or major takeaways"
                    },
                    "civilian_conclusion": {"type": "string", "description": "A concluding formal paragraph about the overall success of the event"}
                },
                "required": [
                    "event_name", "event_date", "event_duration", "event_type", 
                    "organized_by", "coordinators", 
                    "learning_outcome_1", "learning_outcome_2", "learning_outcome_3", "learning_outcome_4",
                    "introduction", "details_of_the_event", "description_of_the_event",
                    "beneficiaries", "session_overview", "key_highlights", "civilian_conclusion"
                ],
                "additionalProperties": False
            }
        }

    try:
        client = Groq(api_key=api_key)
        
        if report_format == 'project_report':
            prompt = (
                f"Write a full engineering dissertation for this project: {description}. "
                "Include abstract, keywords, 6 technical chapters with unique titles, and references. "
                "Keep content dense but concise to fit the response. Complete all fields."
            )
        else:
            prompt = f"Extract and professionally expand the following event description into a full formal event report JSON payload: {description}"

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": json_schema
            }
        )
        
        result = json.loads(response.choices[0].message.content or "{}")
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/render', methods=['POST'])
def render_report_preview():
    data = request.json
    report_format = data.get('report_format', 'event_report')
    template = 'project_schema.html' if report_format == 'project_report' else 'schema.html'
    return render_template(template, **data)

@app.route('/export-docx', methods=['POST'])
def export_docx():
    data = request.json
    report_format = data.get('report_format', 'event_report')
    template = 'project_schema.html' if report_format == 'project_report' else 'schema.html'
    
    if report_format == 'project_report':
        report_name = data.get('title', 'Project_Report')
    else:
        report_name = data.get('event_name', 'Event_Report')

    # Render the appropriate template
    html_content = render_template(template, **data)

    # For Event Report, handle the static header
    if report_format == 'event_report':
        header_path = os.path.join(app.static_folder, 'images', 'header.jpg')
        if os.path.exists(header_path):
            with open(header_path, 'rb') as img_file:
                header_b64 = base64.b64encode(img_file.read()).decode('utf-8')
            html_content = html_content.replace(
                '/static/images/header.jpg',
                f'data:image/jpeg;base64,{header_b64}'
            )

    # Wrap in Word-compatible MHTML envelope
    word_html = f'''<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word"
      xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta charset="utf-8">
<!--[if gte mso 9]>
<xml>
<w:WordDocument>
<w:View>Print</w:View>
<w:Zoom>100</w:Zoom>
<w:DoNotOptimizeForBrowser/>
</w:WordDocument>
</xml>
<![endif]-->
{html_content[html_content.find('<style'):html_content.find('</head>')]}
</head>
{html_content[html_content.find('<body'):]}'''

    # Clean filename
    safe_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_name or 'Report'}.doc"

    return Response(
        word_html,
        mimetype='application/msword',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )

if __name__ == '__main__':
    app.run(debug=True)

