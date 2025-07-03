import markdown
import pdfkit
from pathlib import Path
import re


def convert_resume_to_pdf(markdown_file_path, output_pdf_path):
    """
    Convert a markdown resume to a professionally formatted PDF
    """

    # Read the markdown file
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['extra'])
    html_content = md.convert(markdown_content)

    # Custom CSS styling to match the resume format
    css_style = """
    <style>
        body {
            font-family: 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.2;
            margin: 0.5in;
            color: #000;
        }

        h1 {
            text-align: center;
            font-size: 16pt;
            font-weight: bold;
            margin: 0 0 5px 0;
            padding: 0;
        }

        /* Contact info styling */
        body > p:first-of-type {
            text-align: center;
            font-size: 10pt;
            margin: 0 0 15px 0;
        }

        h2 {
            font-size: 12pt;
            font-weight: bold;
            text-transform: uppercase;
            margin: 15px 0 8px 0;
            padding: 0;
            border-bottom: 1px solid #000;
            padding-bottom: 2px;
        }

        h3 {
            font-size: 11pt;
            font-weight: bold;
            margin: 8px 0 4px 0;
            padding: 0;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }

        .job-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            width: 100%;
        }

        .job-info {
            flex: 1;
        }

        .date-range {
            font-weight: normal;
            white-space: nowrap;
            margin-left: 20px;
        }

        p {
            margin: 4px 0;
            text-align: justify;
        }

        ul {
            margin: 4px 0;
            padding-left: 20px;
        }

        li {
            margin: 2px 0;
        }

        /* Employment history specific styling */
        .job-title {
            font-weight: bold;
        }

        .company {
            font-weight: normal;
        }

        /* Links styling */
        a {
            color: #000;
            text-decoration: underline;
        }

        /* Table styling for skills/languages */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 8px 0;
        }

        td {
            padding: 2px 8px;
            border: none;
            vertical-align: top;
        }
    </style>
    """

    # Process the HTML to match the resume format better
    processed_html = process_resume_html(html_content)

    # Complete HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        {css_style}
    </head>
    <body>
        {processed_html}
    </body>
    </html>
    """

    # PDF generation options
    options = {
        'page-size': 'A4',
        'margin-top': '0.5in',
        'margin-right': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }

    # Convert HTML to PDF
    try:
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

        pdfkit.from_string(full_html, output_pdf_path, options=options,configuration=config)
        print(f"PDF successfully created: {output_pdf_path}")
    except Exception as e:
        print(f"Error creating PDF: {e}")
        # Fallback: save HTML file for debugging
        html_output = output_pdf_path.replace('.pdf', '.html')
        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"HTML file saved for debugging: {html_output}")


def process_resume_html(html_content):
    """
    Process the HTML content to better match resume formatting
    """
    # Replace the main heading structure
    html_content = re.sub(
        r'<h1>Isaac Gutierrez</h1>\s*<h2>AI Research Engineer</h2>',
        '<h1>Isaac Gutierrez, Artificial Intelligence Engineer</h1>',
        html_content
    )

    # Process contact information
    contact_pattern = r'<p><strong>Location:</strong>(.*?)</p>'
    html_content = re.sub(contact_pattern, lambda m: format_contact_info(m.group(1)), html_content, flags=re.DOTALL)

    # Process employment entries to add proper formatting
    html_content = process_employment_entries(html_content)

    return html_content


def format_contact_info(contact_text):
    """
    Format the contact information section
    """
    # Extract contact details and format them in a single line
    return '<p>Puebla, Mexico, +52 2224738808, isaacgr2121@gmail.com</p>'


def process_employment_entries(html_content):
    """
    Process employment entries to match the resume format with dates on the same line
    """
    # Pattern to match job entries - looking for h3 followed by date paragraph
    job_pattern = r'<h3>(.*?)\s*\|\s*(.*?)</h3>\s*<p><strong>(.*?)</strong></p>'

    def format_job_entry(match):
        job_title = match.group(1).strip()
        company = match.group(2).strip()
        date_range = match.group(3).strip()

        return f'''<h3><span class="job-info"><span class="job-title">{job_title}</span>, <span class="company">{company}</span></span><span class="date-range">({date_range})</span></h3>'''

    html_content = re.sub(job_pattern, format_job_entry, html_content)

    # Also handle education entries
    education_pattern = r'<h3>(.*?)\s*\|\s*(.*?)</h3>\s*<p><strong>(.*?)</strong></p>'
    html_content = re.sub(education_pattern, format_job_entry, html_content)
    
    # Handle project entries with dates
    project_pattern = r'<h3>(.*?)</h3>\s*<p><strong>(.*?)</strong></p>'
    
    def format_project_entry(match):
        project_title = match.group(1).strip()
        date_range = match.group(2).strip()
        
        return f'''<h3><span class="job-info"><span class="job-title">{project_title}</span></span><span class="date-range">({date_range})</span></h3>'''
    
    html_content = re.sub(project_pattern, format_project_entry, html_content)

    return html_content


# Alternative method using weasyprint (if pdfkit doesn't work)
def convert_resume_to_pdf_weasyprint(markdown_file_path, output_pdf_path):
    """
    Alternative method using weasyprint
    """
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration

        # Read markdown and convert to HTML
        with open(markdown_file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()

        md = markdown.Markdown(extensions=['extra'])
        html_content = md.convert(markdown_content)
        processed_html = process_resume_html(html_content)

        # CSS for weasyprint
        css_content = """
        @page {
            size: A4;
            margin: 0.5in;
        }

        body {
            font-family: 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.2;
            color: #000;
        }

        h1 {
            text-align: center;
            font-size: 16pt;
            font-weight: bold;
            margin: 0 0 5px 0;
        }

        body > p:first-of-type {
            text-align: center;
            font-size: 10pt;
            margin: 0 0 15px 0;
        }

        h2 {
            font-size: 12pt;
            font-weight: bold;
            text-transform: uppercase;
            margin: 15px 0 8px 0;
            border-bottom: 1px solid #000;
            padding-bottom: 2px;
        }

        h3 {
            font-size: 11pt;
            font-weight: bold;
            margin: 8px 0 4px 0;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }

        .job-info {
            flex: 1;
        }

        .date-range {
            font-weight: normal;
            white-space: nowrap;
            margin-left: 20px;
        }

        p {
            margin: 4px 0;
            text-align: justify;
        }

        ul {
            margin: 4px 0;
            padding-left: 20px;
        }

        li {
            margin: 2px 0;
        }
        """

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            {processed_html}
        </body>
        </html>
        """

        # Generate PDF
        HTML(string=full_html).write_pdf(
            output_pdf_path,
            stylesheets=[CSS(string=css_content)]
        )

        print(f"PDF successfully created using weasyprint: {output_pdf_path}")

    except ImportError:
        print("Weasyprint not available. Please install it with: pip install weasyprint")
    except Exception as e:
        print(f"Error with weasyprint: {e}")


# Main execution
if __name__ == "__main__":
    # File paths
    markdown_file = "example.md"  # Your markdown file
    pdf_output = "output.pdf"

    # Check if markdown file exists
    if not Path(markdown_file).exists():
        print(f"Markdown file '{markdown_file}' not found!")
        exit(1)

    print(f"Converting {markdown_file} to {pdf_output}...")

    # Try pdfkit first, then weasyprint as fallback
    try:
        convert_resume_to_pdf(markdown_file, pdf_output)
    except Exception as e:
        print(f"pdfkit failed: {e}")
        print("Trying weasyprint as alternative...")
        convert_resume_to_pdf_weasyprint(markdown_file, pdf_output)