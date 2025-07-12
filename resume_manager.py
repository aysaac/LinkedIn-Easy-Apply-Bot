from typing import Optional
from pathlib import Path
import os
from datetime import datetime

from resume_content_generator import ResumeContentGenerator
from resume_pdf_converter import ResumePDFConverter


class ResumeManager:
    def __init__(self, 
                 experience_file: str = "resume_data/experience.md",
                 personal_info_file: str = "resume_data/personal_info.md",
                 output_dir: str = "generated_resumes",
                 openai_model: str = "gpt-4.1",
                 weave_project: str = "resume-generator",
                 wkhtmltopdf_path: Optional[str] = None):
        """
        Initialize the resume manager.
        
        Args:
            experience_file: Path to experience markdown file
            personal_info_file: Path to personal info markdown file
            output_dir: Directory to save generated resumes
            openai_model: OpenAI model for content generation
            weave_project: Weave project name for logging
            wkhtmltopdf_path: Path to wkhtmltopdf executable
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize content generator
        self.content_generator = ResumeContentGenerator(
            experience_file=experience_file,
            personal_info_file=personal_info_file,
            openai_model=openai_model,
            weave_project=weave_project
        )
        
        # Initialize PDF converter
        self.pdf_converter = ResumePDFConverter(
            wkhtmltopdf_path=wkhtmltopdf_path,
            use_weasyprint_fallback=True
        )

    def create_resume(self, job: str, company: str, description: str) -> str:
        """
        Create a complete resume tailored to a specific job.
        
        Args:
            job: Job title/position
            company: Company name
            description: Job description
            
        Returns:
            Path to the generated PDF resume
        """
        try:
            # Generate resume content
            print(f"Generating resume content for {job} at {company}...")
            markdown_content = self.content_generator.generate_resume_content(
                job_title=job,
                company=company,
                job_description=description
            )
            
            # Create output filename
            safe_job = self._sanitize_filename(job)
            safe_company = self._sanitize_filename(company)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save markdown file
            markdown_filename = f"{safe_job}_{safe_company}_{timestamp}.md"
            markdown_path = self.output_dir / markdown_filename
            self.content_generator.save_resume_content(str(markdown_content), str(markdown_path))
            
            # Generate PDF
            pdf_filename = f"{safe_job}_{safe_company}_{timestamp}.pdf"
            pdf_path = self.output_dir / pdf_filename
            
            print(f"Converting to PDF: {pdf_path}")
            final_pdf_path = self.pdf_converter.convert_to_pdf(
                markdown_content=markdown_content,
                output_pdf_path=str(pdf_path)
            )
            
            print(f"Resume generated successfully: {final_pdf_path}")
            return final_pdf_path
            
        except Exception as e:
            print(f"Error generating resume: {e}")
            raise e

    def create_resume_with_custom_output(self, job: str, company: str, description: str, 
                                       output_filename: str) -> str:
        """
        Create a resume with a custom output filename.
        
        Args:
            job: Job title/position
            company: Company name
            description: Job description
            output_filename: Custom filename for the PDF (without extension)
            
        Returns:
            Path to the generated PDF resume
        """
        try:
            # Generate resume content
            print(f"Generating resume content for {job} at {company}...")
            markdown_content = self.content_generator.generate_resume_content(
                job_title=job,
                company=company,
                job_description=description
            )
            
            # Create output paths
            pdf_filename = f"{output_filename}.pdf"
            pdf_path = self.output_dir / pdf_filename
            
            # Also save markdown version
            markdown_filename = f"{output_filename}.md"
            markdown_path = self.output_dir / markdown_filename
            self.content_generator.save_resume_content(str(markdown_content), str(markdown_path))
            
            # Generate PDF
            print(f"Converting to PDF: {pdf_path}")
            final_pdf_path = self.pdf_converter.convert_to_pdf(
                markdown_content=markdown_content,
                output_pdf_path=str(pdf_path)
            )
            
            print(f"Resume generated successfully: {final_pdf_path}")
            return final_pdf_path
            
        except Exception as e:
            print(f"Error generating resume: {e}")
            raise e

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be safe for use as a filename.
        
        Args:
            filename: The string to sanitize
            
        Returns:
            Sanitized filename string
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        sanitized = filename
        
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove extra spaces and replace with underscores
        sanitized = '_'.join(sanitized.split())
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized

    def get_output_directory(self) -> str:
        """Get the current output directory path."""
        return str(self.output_dir)

    def set_output_directory(self, new_dir: str) -> None:
        """
        Set a new output directory.
        
        Args:
            new_dir: New directory path
        """
        self.output_dir = Path(new_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def list_generated_resumes(self) -> list:
        """
        List all generated resume files in the output directory.
        
        Returns:
            List of generated resume file paths
        """
        if not self.output_dir.exists():
            return []
        
        pdf_files = list(self.output_dir.glob("*.pdf"))
        return [str(f) for f in sorted(pdf_files, key=lambda x: x.stat().st_mtime, reverse=True)]

    def create_debug_html(self, job: str, company: str, description: str) -> str:
        """
        Create an HTML version of the resume for debugging purposes.
        
        Args:
            job: Job title/position
            company: Company name
            description: Job description
            
        Returns:
            Path to the generated HTML file
        """
        try:
            # Generate resume content
            markdown_content = self.content_generator.generate_resume_content(
                job_title=job,
                company=company,
                job_description=description
            )
            
            # Convert to HTML
            html_content = self.pdf_converter._markdown_to_html(markdown_content)
            processed_html = self.pdf_converter._process_resume_html(html_content)
            
            # Save HTML file
            safe_job = self._sanitize_filename(job)
            safe_company = self._sanitize_filename(company)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            html_filename = f"{safe_job}_{safe_company}_{timestamp}_debug.html"
            html_path = self.output_dir / html_filename
            
            final_html_path = self.pdf_converter.save_html_debug(
                html_content=processed_html,
                output_path=str(html_path)
            )
            
            print(f"Debug HTML generated: {final_html_path}")
            return final_html_path
            
        except Exception as e:
            print(f"Error generating debug HTML: {e}")
            raise e


# Example usage
if __name__ == "__main__":
    # Initialize the resume manager
    manager = ResumeManager()
    
    # Example job details
    job_title = "Senior Machine Learning Engineer"
    company_name = "Tech Innovators Inc."
    job_description = """
    We are seeking a Senior Machine Learning Engineer to join our AI team.
    The ideal candidate will have experience with deep learning, computer vision,
    and deploying ML models at scale. Knowledge of Python, TensorFlow, and cloud
    platforms is essential.
    """
    
    # Generate resume
    try:
        pdf_path = manager.create_resume(
            job=job_title,
            company=company_name,
            description=job_description
        )
        print(f"Resume saved to: {pdf_path}")
    except Exception as e:
        print(f"Failed to generate resume: {e}")