#!/usr/bin/env python3
"""
Combined Resume Generation Script
Combines the functionality of markdown2pdf.py and resume_pdf_converter.py
using the ResumeManager class for a streamlined experience.
"""

import os
import argparse
from pathlib import Path
from typing import Optional
from resume_manager import ResumeManager


def main():
    """Main function to generate a custom resume from job posting details."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a custom resume tailored to a specific job posting")
    parser.add_argument("--job", "-j", required=True, help="Job title/position")
    parser.add_argument("--company", "-c", required=True, help="Company name")
    parser.add_argument("--description", "-d", required=True, help="Job description (text or file path)")
    parser.add_argument("--output", "-o", help="Output filename (without extension)")
    parser.add_argument("--output-dir", help="Output directory", default="generated_resumes")
    parser.add_argument("--model", help="OpenAI model to use", default="gpt-4o-mini")
    parser.add_argument("--weave-project", help="Weave project name", default="resume-generator")
    parser.add_argument("--debug", action="store_true", help="Generate debug HTML file")
    parser.add_argument("--markdown-only", action="store_true", help="Generate only markdown, skip PDF")
    
    args = parser.parse_args()
    
    # Handle job description input (text or file path)
    job_description = get_job_description(args.description)
    
    # Initialize Resume Manager
    print("Initializing Resume Manager...")
    resume_manager = ResumeManager(
        output_dir=args.output_dir,
        openai_model=args.model,
        weave_project=args.weave_project
    )
    
    try:
        if args.output:
            # Use custom output filename
            if args.markdown_only:
                # Generate only markdown
                print(f"Generating markdown resume for {args.job} at {args.company}...")
                markdown_content = resume_manager.content_generator.generate_resume_content(
                    job_title=args.job,
                    company=args.company,
                    job_description=job_description
                )
                
                # Save markdown file
                markdown_path = Path(args.output_dir) / f"{args.output}.md"
                resume_manager.content_generator.save_resume_content(
                    markdown_content, str(markdown_path)
                )
                print(f"Markdown resume saved to: {markdown_path}")
                
            else:
                # Generate both markdown and PDF
                pdf_path = resume_manager.create_resume_with_custom_output(
                    job=args.job,
                    company=args.company,
                    description=job_description,
                    output_filename=args.output
                )
                print(f"Resume generated successfully: {pdf_path}")
        else:
            # Use automatic filename
            pdf_path = resume_manager.create_resume(
                job=args.job,
                company=args.company,
                description=job_description
            )
            print(f"Resume generated successfully: {pdf_path}")
        
        # Generate debug HTML if requested
        if args.debug:
            print("Generating debug HTML...")
            html_path = resume_manager.create_debug_html(
                job=args.job,
                company=args.company,
                description=job_description
            )
            print(f"Debug HTML generated: {html_path}")
        
        # Show summary
        print("\n" + "="*50)
        print("RESUME GENERATION SUMMARY")
        print("="*50)
        print(f"Job Title: {args.job}")
        print(f"Company: {args.company}")
        print(f"Output Directory: {resume_manager.get_output_directory()}")
        
        # List all generated files
        print("\nGenerated Files:")
        for file_path in resume_manager.list_generated_resumes():
            print(f"  - {file_path}")
            
    except Exception as e:
        print(f"Error generating resume: {e}")
        return 1
    
    return 0


def get_job_description(description_input: str) -> str:
    """
    Get job description from input (either text or file path).
    
    Args:
        description_input: Either job description text or path to file containing it
        
    Returns:
        Job description text
    """
    # Check if it's a file path
    if os.path.isfile(description_input):
        try:
            with open(description_input, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading file {description_input}: {e}")
            return description_input
    else:
        # Treat as direct text input
        return description_input


def interactive_mode():
    """Interactive mode for generating resumes."""
    print("="*50)
    print("INTERACTIVE RESUME GENERATOR")
    print("="*50)
    
    # Get job details interactively
    job_title = input("Enter job title: ").strip()
    company = input("Enter company name: ").strip()
    
    print("\nEnter job description (type 'END' on a new line to finish):")
    description_lines = []
    while True:
        line = input()
        if line.strip() == 'END':
            break
        description_lines.append(line)
    
    job_description = '\n'.join(description_lines)
    
    if not job_title or not company or not job_description:
        print("Error: All fields are required!")
        return 1
    
    # Initialize Resume Manager
    print("\nInitializing Resume Manager...")
    resume_manager = ResumeManager()
    
    try:
        # Generate resume
        print(f"Generating resume for {job_title} at {company}...")
        pdf_path = resume_manager.create_resume(
            job=job_title,
            company=company,
            description=job_description
        )
        
        print(f"\nResume generated successfully: {pdf_path}")
        
        # Ask if user wants debug HTML
        generate_debug = input("\nGenerate debug HTML? (y/n): ").lower().startswith('y')
        if generate_debug:
            html_path = resume_manager.create_debug_html(
                job=job_title,
                company=company,
                description=job_description
            )
            print(f"Debug HTML generated: {html_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error generating resume: {e}")
        return 1


if __name__ == "__main__":
    import sys
    
    # Check if running in interactive mode
    if len(sys.argv) == 1:
        print("No arguments provided. Starting interactive mode...")
        exit_code = interactive_mode()
    else:
        exit_code = main()
    
    sys.exit(exit_code)