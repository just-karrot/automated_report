import os
import io
import base64
import json
import concurrent.futures
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

    try:
        client = Groq(api_key=api_key)
        
        # --- PROJECT REPORT (Multi-Pass Generation) ---
        if report_format == 'project_report':
            # Phase 1: Metadata, Titles, Abstract, References
            system_prompt_base = (
                "You are an expert academic project coordinator. "
                "Define the metadata, detailed abstract, references, and 6 relevant technical chapter titles for a dissertation. "
                "Tone: Formal and Academic. Format: JSON schema provided. "
                "You may use simple HTML for the abstract: <p> for paragraphs, <b> for bold, <i> for italics, and <ul>/<li> for lists if needed."
            )
            
            base_schema = {
                "name": "project_report_base_schema",
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "project_type": {"type": "string"},
                        "branch": {"type": "string"},
                        "session": {"type": "string"},
                        "professor_name": {"type": "string"},
                        "professor_designation": {"type": "string"},
                        "certificate_students_text": {"type": "string"},
                        "students": {
                            "type": "array",
                            "items": {"type": "object", "properties": {"name": {"type": "string"}, "reg_no": {"type": "string"}, "roll_no": {"type": "string"}}}
                        },
                        "abstract_title": {"type": "string", "default": "ABSTRACT"},
                        "abstract_content": {"type": "string"},
                        "keywords": {"type": "string"},
                        "chapter_1_title": {"type": "string"},
                        "chapter_2_title": {"type": "string"},
                        "chapter_3_title": {"type": "string"},
                        "chapter_4_title": {"type": "string"},
                        "chapter_5_title": {"type": "string"},
                        "chapter_6_title": {"type": "string"},
                        "references": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["title", "chapter_1_title"]
                }
            }

            prompt_base = f"Create the foundation for an engineering dissertation based on this description: {description}. Provide descriptive metadata, an extensive multi-paragraph abstract, 5-8 IEEE references, and 6 technical chapter titles (starting with CHAPTER X: ...)."
            
            response_base = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "system", "content": system_prompt_base}, {"role": "user", "content": prompt_base}],
                response_format={"type": "json_schema", "json_schema": base_schema}
            )
            result = json.loads(response_base.choices[0].message.content or "{}")

            # Phase 2: Chapter Content Generation (Parallel)
            def generate_chapter_content(idx, chapter_title):
                chap_system_prompt = (
                    "You are a senior engineering student writing a highly detailed, professional project dissertation. "
                    "Write extensive, multi-paragraph content for the requested chapter. "
                    "Focus on technical depth, clear explanations, and academic rigor. "
                    "You are encouraged to use simple HTML to structure your content: "
                    "Use <p> for paragraphs, <b> for bold, <i> for italics, <ul>/<li> for bulleted lists, "
                    "and <table>/<tr>/<td> for data or comparisons. No raw markdown. "
                    "Do NOT use multiple <br> tags to simulate page breaks; the system will handle pagination. "
                    "The report must feel long and comprehensive (equivalent to 3-4 pages per chapter)."
                )
                chap_prompt = f"Write the complete, extremely detailed, multi-paragraph content for {chapter_title} of the project: {result.get('title')}. Context: {description}"
                
                chap_resp = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "system", "content": chap_system_prompt}, {"role": "user", "content": chap_prompt}],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "chapter_content",
                            "strict": False,
                            "schema": {
                                "type": "object",
                                "properties": {"content": {"type": "string"}},
                                "required": ["content"]
                            }
                        }
                    }
                )
                return json.loads(chap_resp.choices[0].message.content or "{}").get("content", "")

            # Execute parallel calls
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                future_to_idx = {}
                for i in range(1, 7):
                    title = result.get(f'chapter_{i}_title', f'CHAPTER {i}: CONTENT')
                    future_to_idx[executor.submit(generate_chapter_content, i, title)] = i
                
                for future in concurrent.futures.as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    try:
                        result[f'chapter_{idx}_content'] = future.result()
                    except Exception:
                        result[f'chapter_{idx}_content'] = "Content generation failed for this section."
            
            return jsonify(result)

        # --- EVENT REPORT (Single Pass, unchanged) ---
        else:
            system_prompts = {
                "cultural": "You are a professional report writer for a college cultural event. Write in a warm, lighthearted tone. MAINTAIN FORMALITY. JSON schema provided.",
                "sports": "You are a professional report writer for a college sports event. Focus on format, rules, and spirit. JSON schema provided.",
                "technical": "You are a professional report writer for a college technical event. Use precise terminology and emphasize innovation. JSON schema provided."
            }
            system_prompt = system_prompts.get(event_category, system_prompts["technical"])
            
            json_schema = {
                "name": "full_event_report_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "event_name": {"type": "string"},
                        "event_date": {"type": "string"},
                        "event_duration": {"type": "string"},
                        "event_type": {"type": "string"},
                        "organized_by": {"type": "string"},
                        "coordinators": {"type": "string"},
                        "learning_outcome_1": {"type": "string"},
                        "learning_outcome_2": {"type": "string"},
                        "learning_outcome_3": {"type": "string"},
                        "learning_outcome_4": {"type": "string"},
                        "introduction": {"type": "string"},
                        "details_of_the_event": {"type": "string"},
                        "description_of_the_event": {"type": "string"},
                        "beneficiaries": {"type": "string"},
                        "session_overview": {"type": "string"},
                        "key_highlights": {"type": "array", "items": {"type": "string"}},
                        "conclusion": {"type": "string"}
                    },
                    "required": ["event_name", "introduction", "conclusion"]
                }
            }
            
            prompt = f"Extract and professionally expand the following event description into a full formal event report JSON payload: {description}"
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                response_format={"type": "json_schema", "json_schema": json_schema}
            )
            return jsonify(json.loads(response.choices[0].message.content or "{}"))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/render', methods=['POST'])
def render_report_preview():
    data = request.json
    report_format = data.get('report_format', 'event_report')
    template = 'project_schema.html' if report_format == 'project_report' else 'schema.html'
    return render_template(template, **data)

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from lxml import html

def add_html_to_docx(html_content, doc_or_cell):
    """Parses HTML and adds corresponding elements to a python-docx document or table cell."""
    if not html_content:
        return
    
    try:
        # Wrap in a div to ensure a single root for lxml
        tree = html.fromstring(f"<div>{html_content}</div>")
    except Exception:
        doc_or_cell.add_paragraph(html_content)
        return

    def process_element(element, parent_docx):
        # Handle child nodes
        for child in element.xpath('node()'):
            if isinstance(child, html.HtmlElement):
                tag = child.tag.lower()
                
                if tag == 'p':
                    p = parent_docx.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    process_element(child, p)
                
                elif tag == 'br':
                    # If parent is a paragraph, add a break
                    if hasattr(parent_docx, 'add_run'):
                        parent_docx.add_run().add_break()
                    else:
                        parent_docx.add_paragraph()
                
                elif tag in ['b', 'strong']:
                    if hasattr(parent_docx, 'add_run'):
                        run = parent_docx.add_run()
                        run.bold = True
                        # We need to process children of <b> to handle nested tags like <b><i>text</i></b>
                        # But for simplicity, if it's just text:
                        run.text = child.text if child.text else ""
                        process_element(child, parent_docx)
                    else:
                        p = parent_docx.add_paragraph()
                        run = p.add_run()
                        run.bold = True
                        run.text = child.text if child.text else ""
                        process_element(child, p)

                elif tag in ['i', 'em']:
                    if hasattr(parent_docx, 'add_run'):
                        run = parent_docx.add_run()
                        run.italic = True
                        run.text = child.text if child.text else ""
                        process_element(child, parent_docx)
                    else:
                        p = parent_docx.add_paragraph()
                        run = p.add_run()
                        run.italic = True
                        run.text = child.text if child.text else ""
                        process_element(child, p)

                elif tag == 'ul':
                    for li in child.xpath('./li'):
                        p = parent_docx.add_paragraph(style='List Bullet')
                        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        process_element(li, p)
                
                elif tag == 'ol':
                    for li in child.xpath('./li'):
                        p = parent_docx.add_paragraph(style='List Number')
                        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        process_element(li, p)

                elif tag == 'table':
                    rows = child.xpath('.//tr')
                    if rows:
                        # Find max columns
                        max_cols = 0
                        for row in rows:
                            max_cols = max(max_cols, len(row.xpath('./td | ./th')))
                        
                        if max_cols > 0:
                            table = parent_docx.add_table(rows=len(rows), cols=max_cols)
                            table.style = 'Table Grid'
                            for r_idx, row in enumerate(rows):
                                for c_idx, cell in enumerate(row.xpath('./td | ./th')):
                                    if c_idx < max_cols:
                                        process_element(cell, table.cell(r_idx, c_idx))

                elif tag in ['td', 'th', 'li']:
                    # These are containers, just process their children
                    process_element(child, parent_docx)
                
                else:
                    # Unknown tag, just process children
                    process_element(child, parent_docx)
                    
            elif isinstance(child, str):
                # This is text content
                text = str(child).strip()
                if text:
                    if hasattr(parent_docx, 'add_run'):
                        # If the current parent is a paragraph, add text to it
                        parent_docx.add_run(text)
                    elif hasattr(parent_docx, 'add_paragraph'):
                        # If the current parent is a Document or Cell, create a paragraph
                        p = parent_docx.add_paragraph(text)
                        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    process_element(tree, doc_or_cell)

@app.route('/export-docx', methods=['POST'])
def export_docx():
    data = request.json
    report_format = data.get('report_format', 'event_report')
    doc = Document()
    
    # Global Style Settings
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    if report_format == 'project_report':
        report_name = data.get('title', 'Project_Report')
        
        # --- COVER PAGE ---
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_p.add_run(data.get('title', '[TITLE]').upper())
        run.bold = True
        run.font.size = Pt(16)
        
        doc.add_paragraph() # Spacer
        
        type_p = doc.add_paragraph()
        type_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        type_p.add_run(f"A {data.get('project_type', '[Type]')} Report submitted in partial fulfilment of the requirements of")
        
        degree_p = doc.add_paragraph()
        degree_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        degree_p.add_run("The award of the degree of")
        
        btech_p = doc.add_paragraph()
        btech_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = btech_p.add_run("Bachelor of Technology")
        run.bold = True
        run.font.size = Pt(14)
        
        in_p = doc.add_paragraph()
        in_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        in_p.add_run("in")
        
        branch_p = doc.add_paragraph()
        branch_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = branch_p.add_run(data.get('branch', '[Branch]'))
        run.bold = True
        run.font.size = Pt(14)
        
        doc.add_paragraph()
        by_p = doc.add_paragraph()
        by_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        by_p.add_run("by")
        
        for student in data.get('students', []):
            sp = doc.add_paragraph()
            sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = sp.add_run(f"{student.get('name')}, Reg No: {student.get('reg_no')}")
            run.bold = True
            
        doc.add_paragraph()
        doc.add_paragraph("Under the guidance of").alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        prof_p = doc.add_paragraph()
        prof_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = prof_p.add_run(data.get('professor_name', '[Professor Name]'))
        run.bold = True
        doc.add_paragraph(data.get('professor_designation', 'Assistant Professor')).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Department of Advance Computing").alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Logo
        logo_path = os.path.join(app.static_folder, 'images', 'pce_logo.jpg')
        if os.path.exists(logo_path):
            doc.add_picture(logo_path, width=Inches(1.5))
            last_p = doc.paragraphs[-1]
            last_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        doc.add_paragraph(f"(Session {data.get('session', '2025-26')})").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Department of Advance Computing").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Poornima College of Engineering").alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Jan-June, 2026").alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_page_break() # Break after Cover Page
        
        # --- CERTIFICATES ---
        doc.add_heading('DEPARTMENT CERTIFICATE', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        cert_p = doc.add_paragraph("This is to certify that ")
        cert_p.add_run(data.get('certificate_students_text', '[Students]')).bold = True
        cert_p.add_run(" of the IV semester Department of Advance Computing, has submitted this Project report entitled ")
        cert_p.add_run(data.get('title', '[Title]')).bold = True
        cert_p.add_run(f" under the supervision of {data.get('professor_name')}, {data.get('professor_designation')}...")
        
        doc.add_page_break() # Break after Dept Certificate
        
        doc.add_heading("CANDIDATE'S DECLARATION", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("We hereby declare that the work which is being presented in this project report...")
        doc.add_page_break() # Break after Candidate Declaration
        
        doc.add_heading("SUPERVISOR'S CERTIFICATE", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("This is to certify that, to the best of my knowledge...")
        doc.add_page_break() # Break after Supervisor Certificate
        
        doc.add_heading("ACKNOWLEDGEMENT", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("We would like to convey our profound sense of reverence...")
        doc.add_page_break() # Break after Acknowledgement
        
        doc.add_heading("TABLE OF CONTENTS", level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph("Contents...")
        doc.add_page_break() # Break after Table of Contents
        
        # --- ABSTRACT ---
        doc.add_heading(data.get('abstract_title', 'ABSTRACT'), level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_html_to_docx(data.get('abstract_content', ''), doc)
        doc.add_paragraph(f"Keywords: {data.get('keywords', '')}")
        
        doc.add_page_break() # Break after Keywords (before chapters)
        
        # --- CHAPTERS ---
        for i in range(1, 7):
            title = data.get(f'chapter_{i}_title')
            content = data.get(f'chapter_{i}_content', '')
            if title:
                doc.add_heading(title, level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_html_to_docx(content, doc)
                doc.add_page_break()
                
        # --- REFERENCES ---
        doc.add_heading('REFERENCES', level=1).alignment = WD_ALIGN_PARAGRAPH.CENTER
        for ref in data.get('references', []):
            doc.add_paragraph(ref, style='List Bullet')

    else:
        # --- EVENT REPORT ---
        report_name = data.get('event_name', 'Event_Report')
        
        # Header Image
        header_path = os.path.join(app.static_folder, 'images', 'header.jpg')
        if os.path.exists(header_path):
            doc.add_picture(header_path, width=Inches(6))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph("A report on").alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title_p.add_run(data.get('event_name', '').upper())
        run.bold = True
        run.underline = True
        
        details = [
            ("NAME OF THE EVENT:", data.get('event_name')),
            ("DATE AND DURATION:", f"{data.get('event_date')} - {data.get('event_duration')}"),
            ("TYPE OF ACTIVITY:", data.get('event_type')),
            ("ORGANIZED BY:", data.get('organized_by')),
            ("COORDINATORS:", data.get('coordinators', '').replace('<br>', '\n'))
        ]
        
        for label, val in details:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(label)
            run.bold = True
            p.add_run(f" {val}")

        doc.add_page_break()
        
        # Outcomes, Content, etc.
        doc.add_heading('LEARNING OUTCOMES', level=2)
        for i in range(1, 5):
            doc.add_paragraph(f"CO{i}: {data.get(f'learning_outcome_{i}', '')}")
            
        sections = [
            ("INTRODUCTION", data.get('introduction')),
            ("DETAILS OF THE EVENT", data.get('details_of_the_event')),
            ("DESCRIPTION OF THE EVENT", data.get('description_of_the_event')),
            ("BENEFICIARIES", data.get('beneficiaries')),
            ("SESSION OVERVIEW", data.get('session_overview')),
            ("CONCLUSION", data.get('conclusion'))
        ]
        
        for title, content in sections:
            doc.add_heading(title, level=2)
            add_html_to_docx(content, doc)

    # Save to buffer
    f = io.BytesIO()
    doc.save(f)
    f.seek(0)

    # Clean filename
    safe_name = "".join(c for c in report_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_name or 'Report'}.docx"

    return Response(
        f.read(),
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
    )

if __name__ == '__main__':
    app.run(debug=True)

