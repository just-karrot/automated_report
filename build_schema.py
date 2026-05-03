import re
import os

source_file = 'project_report_sample.html'
dest_file = 'templates/project_schema.html'

if not os.path.exists('templates'):
    os.makedirs('templates')

with open(source_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Global replacements (Cover, Certificate, etc.)
replacements = {
    '[Title]': '{{ title }}',
    '[type of project]': '{{ project_type }}',
    '[branch]': '{{ branch }}',
    '[professor name]': '{{ professor_name }}',
    'Assistant Professor': '{{ professor_designation }}',
    'Appoorva Bansal': '{{ professor_name }}',
    'Jan-June, 2026': '{{ session }}',
    'Jan 2026 to June 2026': '{{ session }}',
    '[Name], Reg No: [registration number]': '{{ students[0].name }}, Reg No: {{ students[0].reg_no }}'
}

for old, new in replacements.items():
    content = content.replace(old, new)

# 2. Certificate Students
cert_pattern = r'This is to certify that.*?of the IV semester Department of Advance Computing'
cert_replacement = 'This is to certify that </span><span class="c1">{{ certificate_students_text }}</span><span class="c3"> of the IV semester Department of Advance Computing'
content = re.sub(cert_pattern, cert_replacement, content, flags=re.DOTALL)

# 3. Signatures
def sig_replacer(match):
    sig_replacer.count += 1
    idx = sig_replacer.count - 1
    return f'<span class="c1 c25">{{{{ students[{idx}].name if students|length > {idx} else "Student Name" }}}},</span><span class="c1">&nbsp;Department of</span><span class="c3">&nbsp;</span><span class="c13 c1">Advanced Computing, {{{{ students[{idx}].roll_no if students|length > {idx} else "[Roll number]" }}}}</span>'

sig_replacer.count = 0
sig_pattern = r'<span class="c1 c25">Student Name,</span>.*?Department of</span>.*?Advanced Computing, \[Roll number\]'
content = re.sub(sig_pattern, sig_replacer, content, flags=re.DOTALL)

# 4. Dynamic Chapters (Titles and Content)
# Mapping of search text to variable base name
chapters = {
    'ABSTRACT': 'abstract',
    'CHAPTER 1: INTRODUCTION': 'chapter_1',
    'CHAPTER 2: DATA STRUCTURES USED': 'chapter_2',
    'CHAPTER 3: SYSTEM DESIGN': 'chapter_3',
    'CHAPTER 4: IMPLEMENTATION': 'chapter_4',
    'CHAPTER 5: RESULTS AND DISCUSSION': 'chapter_5',
    'CHAPTER 6: CONCLUSION AND FUTURE ENHANCEMENT': 'chapter_6'
}

for search_text, var_base in chapters.items():
    # A. Replace in Table of Contents
    # The TOC entries look like: CHAPTER 1: INTRODUCTION&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2
    # We replace the text part but keep the spacer/page number for now
    content = content.replace(search_text + '&nbsp;', f'{{{{ {var_base}_title }}}}&nbsp;')
    # Handle the specific Chapter 5 which has " (WITH SCREENSHOT)"
    if var_base == 'chapter_5':
        content = content.replace(' (WITH SCREENSHOT)&nbsp;', '&nbsp;')

    # B. Replace in Body Heading and add Content Placeholder
    # Search for h1 containing the text, allowing for tags/newlines inside
    pattern = rf'(<h1.*?>.*?){re.escape(search_text)}.*?(</span></h1>)'
    replacement = rf'\1{{{{ {var_base}_title }}}}\2' + f'\n    <div class="content-block">{{{{ {var_base}_content | safe }}}}</div>\n    <div style="page-break-after: always;"></div>'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Fix Chapter 5 specifically if it lost its bold span during the first replacement
# Chapter 5 originally had c18 (not bold) in its inner span in some parts of the sample
content = content.replace('<span class="c18 c3 c51">{{ chapter_5_title }}</span>', '<span class="c18 c3 c51 c1">{{ chapter_5_title }}</span>')

# 5. Keywords
content = content.replace('Keywords: </span><span>&nbsp;', 'Keywords: </span><span>&nbsp;{{ keywords }}')

# 6. References List
# Search for the REFERENCES heading and add a loop for the references
ref_pattern = r'(<h1.*?>.*?REFERENCES.*?</span></h1>)'
ref_replacement = r'\1' + '\n    <ul class="references-list">\n        {% for ref in references %}\n        <li>{{ ref }}</li>\n        {% endfor %}\n    </ul>'
content = re.sub(ref_pattern, ref_replacement, content, flags=re.DOTALL)

with open(dest_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully created {dest_file} with dynamic chapter titles.")
