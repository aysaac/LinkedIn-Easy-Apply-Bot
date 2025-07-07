import markdown
import pdfkit
from pathlib import Path
import re
from typing import Optional


class ResumePDFConverter:
    def __init__(self, 
                 wkhtmltopdf_path: Optional[str] = None,
                 use_weasyprint_fallback: bool = True):
        """
        Initialize the PDF converter.
        
        Args:
            wkhtmltopdf_path: Path to wkhtmltopdf executable
            use_weasyprint_fallback: Whether to use weasyprint as fallback
        """
        self.wkhtmltopdf_path = wkhtmltopdf_path or "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
        self.use_weasyprint_fallback = use_weasyprint_fallback
        
        # PDF generation options
        self.pdf_options = {
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # CSS styling for professional resume format
        self.css_style = """
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
        
        /* Force Projects section to start on new page */
        .projects-section {
            page-break-before: always;
            margin-top: 0;
        }

        /* Three-column layout for Skills section using table */
        .skills-grid {
            display: table;
            width: 100%;
            margin: 8px 0;
            table-layout: fixed;
        }

        .skills-row {
            display: table-row;
        }

        .skill-item {
            display: table-cell;
            width: 33.33%;
            padding: 2px 8px 2px 0;
            vertical-align: top;
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

    def convert_to_pdf(self, markdown_content: str, output_pdf_path: str) -> str:
        """
        Convert markdown content to PDF.
        
        Args:
            markdown_content: The markdown content to convert
            output_pdf_path: Path where the PDF should be saved
            
        Returns:
            Path to the generated PDF file
        """
        try:
            # Convert markdown to HTML
            html_content = self._markdown_to_html(markdown_content)
            
            # Process HTML for resume formatting
            processed_html = self._process_resume_html(html_content)
            
            # Generate PDF using pdfkit
            pdf_path = self._generate_pdf_pdfkit(processed_html, output_pdf_path)
            
            return pdf_path
            
        except Exception as e:
            if self.use_weasyprint_fallback:
                print(f"pdfkit failed: {e}")
                print("Trying weasyprint as fallback...")
                return self._generate_pdf_weasyprint(markdown_content, output_pdf_path)
            else:
                raise e

    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML."""
        md = markdown.Markdown(extensions=['extra'])
        return md.convert(markdown_content)

    def _process_resume_html(self, html_content: str) -> str:
        """Process HTML content for resume formatting."""
        # Replace the main heading structure
        html_content = re.sub(
            r'<h1>Isaac Gutierrez</h1>\s*<h2>AI Research Engineer</h2>',
            '<h1>Isaac Gutierrez, Artificial Intelligence Engineer</h1>',
            html_content
        )

        # Process contact information
        contact_pattern = r'<p><strong>Location:</strong>(.*?)</p>'
        html_content = re.sub(contact_pattern, 
                            lambda m: self._format_contact_info(m.group(1)), 
                            html_content, flags=re.DOTALL)

        # Process employment entries
        html_content = self._process_employment_entries(html_content)
        
        # Add projects section class
        html_content = re.sub(r'<h2>Projects</h2>', 
                            '<h2 class="projects-section">Projects</h2>', 
                            html_content)
        
        # Create skills layout
        html_content = self._create_skills_layout(html_content)

        return html_content

    def _format_contact_info(self, contact_text: str) -> str:
        """Format contact information."""
        return '<p>Puebla, Mexico, +52 2224738808, isaacgr2121@gmail.com</p>'

    def _process_employment_entries(self, html_content: str) -> str:
        """Process employment entries for proper formatting."""
        # Pattern to match job entries
        job_pattern = r'<h3>(.*?)\s*\|\s*(.*?)</h3>\s*<p><strong>(.*?)</strong></p>'

        def format_job_entry(match):
            job_title = match.group(1).strip()
            company = match.group(2).strip()
            date_range = match.group(3).strip()
            return f'''<h3><span class="job-info"><span class="job-title">{job_title}</span>, <span class="company">{company}</span></span><span class="date-range">({date_range})</span></h3>'''

        html_content = re.sub(job_pattern, format_job_entry, html_content)

        # Handle project entries
        project_pattern = r'<h3>(.*?)</h3>\s*<p><strong>(.*?)</strong></p>'
        
        def format_project_entry(match):
            project_title = match.group(1).strip()
            date_range = match.group(2).strip()
            return f'''<h3><span class="job-info"><span class="job-title">{project_title}</span></span><span class="date-range">({date_range})</span></h3>'''
        
        html_content = re.sub(project_pattern, format_project_entry, html_content)

        return html_content

    def _create_skills_layout(self, html_content: str) -> str:
        """Convert Skills section to a 3-column layout."""
        skills_pattern = r'<h2>Skills</h2>\s*<ul>(.*?)</ul>'
        
        def create_skills_table(match):
            items_html = match.group(1)
            items = re.findall(r'<li>(.*?)</li>', items_html)
            
            rows = []
            for i in range(0, len(items), 3):
                row_items = items[i:i+3]
                while len(row_items) < 3:
                    row_items.append('')
                
                cells = ''.join(f'<div class="skill-item">{"• " + item if item else ""}</div>' for item in row_items)
                rows.append(f'<div class="skills-row">{cells}</div>')
            
            table_content = ''.join(rows)
            
            return f'''<h2>Skills</h2>
<div class="skills-grid">
{table_content}
</div>'''
        
        html_content = re.sub(skills_pattern, create_skills_table, html_content, flags=re.DOTALL)
        return html_content

    def _generate_pdf_pdfkit(self, html_content: str, output_pdf_path: str) -> str:
        """Generate PDF using pdfkit."""
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {self.css_style}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)
        pdfkit.from_string(full_html, output_pdf_path, 
                          options=self.pdf_options, configuration=config)
        
        print(f"PDF successfully created: {output_pdf_path}")
        return output_pdf_path

    def _generate_pdf_weasyprint(self, markdown_content: str, output_pdf_path: str) -> str:
        """Generate PDF using weasyprint as fallback."""
        try:
            from weasyprint import HTML, CSS
            
            # Convert markdown to HTML
            html_content = self._markdown_to_html(markdown_content)
            processed_html = self._process_resume_html(html_content)
            
            # CSS for weasyprint
            css_content = """
            @page {
                size: A4;
                margin: 0.5in;
            }
            """ + self.css_style.replace('<style>', '').replace('</style>', '')

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

            HTML(string=full_html).write_pdf(
                output_pdf_path,
                stylesheets=[CSS(string=css_content)]
            )

            print(f"PDF successfully created using weasyprint: {output_pdf_path}")
            return output_pdf_path

        except ImportError:
            raise ImportError("Weasyprint not available. Please install it with: pip install weasyprint")
        except Exception as e:
            raise Exception(f"Error with weasyprint: {e}")

    def save_html_debug(self, html_content: str, output_path: str) -> str:
        """Save HTML content for debugging purposes."""
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            {self.css_style}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return output_path