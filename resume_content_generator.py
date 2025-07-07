from typing import Dict, List, Optional
from openai import OpenAI
import json
import weave
from pathlib import Path


class ResumeContentGenerator:
    def __init__(self, 
                 experience_file: str = "resume_data/experience.md",
                 personal_info_file: str = "resume_data/personal_info.md",
                 openai_model: str = "gpt-4o-mini",
                 weave_project: str = "resume-generator"):
        """
        Initialize the resume content generator.
        
        Args:
            experience_file: Path to the experience markdown file
            personal_info_file: Path to the personal info markdown file  
            openai_model: OpenAI model to use for content generation
            weave_project: Weave project name for logging
        """
        self.experience_file = experience_file
        self.personal_info_file = personal_info_file
        self.openai_model = openai_model
        self.weave_project = weave_project
        
        # Initialize OpenAI client
        self.client = OpenAI()
        
        # Initialize Weave for logging
        weave.init(self.weave_project)
        
        # Load resume data
        self.experience_data = self._load_file(self.experience_file)
        self.personal_info_data = self._load_file(self.personal_info_file)
        
        # System prompt for OpenAI
        self.system_prompt = """
Create a profile for the following job using using information from this applicant given some job posting. 
Break down the key qualifications, technical and soft skills, relevant experience, and project work that would make a candidate stand out. Highlight essential industry certifications, domain expertise, and the impact of past roles in shaping their suitability.
Additionally, evaluate leadership qualities, problem-solving abilities, and adaptability to evolving industry trends. If applicable, consider cultural fit, teamwork, and communication skills required for success in the organization.
First list all the abilities that both the candidate and the job posting have in common and some of the skills that would be nice to have.
Before writing the profile, provide a structured assessment framework what an exceptional profile should look like, red flags to avoid, and how to differentiate between a good candidate and a perfect hire. Ensure your response is comprehensive, strategic, and aligned with real-world hiring best practices.
The profile must be writen in one row and must be in english and must be written from the perspective of the candidate.
Do no mention the job posting or the organization, just the candidate's qualifications and skills that would be relevant for the position. If a skill is relevant but there is no project or experience with it you can mention it in the skills portion but not in the profile.
You must also return a list of the most relevant skills that the candidate has for this job, focus on the skills that are required or wanted for the job posting and then some skills that might be relevant.
Respond in the following format with the max number of skills that you want to include in the profile being 12:
```json
{
"profile": "profile here"
"skills": ["skill1", "skill2", "skill3"]
}
```

""" + self.experience_data

    def _load_file(self, file_path: str) -> str:
        """Load content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {e}")

    @weave.op
    def generate_job_profile(self, job_title: str, company: str, job_description: str) -> Dict:
        """
        Generate a job-specific profile using OpenAI API.
        
        Args:
            job_title: Job title for the position
            company: Company name
            job_description: Full job description
            
        Returns:
            Dictionary containing profile and skills
        """
        user_prompt = f"""
Job Title: {job_title}
Company: {company}
Job Description: {job_description}
"""
        
        response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
        )
        
        response_text = response.choices[0].message.content
        return self._extract_json_from_text(response_text)

    def _extract_json_from_text(self, text: str) -> Dict:
        """Extract JSON content from OpenAI response."""
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            return {}
        return {}

    def generate_resume_content(self, job_title: str, company: str, job_description: str) -> str:
        """
        Generate complete resume content in markdown format.
        
        Args:
            job_title: Job title for the position
            company: Company name  
            job_description: Full job description
            
        Returns:
            Complete markdown resume content
        """
        # Generate job-specific profile and skills
        profile_data = self.generate_job_profile(job_title, company, job_description)
        
        # Build markdown components
        profile_section = self._build_profile_section(profile_data)
        experience_section = self._build_experience_section()
        skills_section = self._build_skills_section(profile_data)
        projects_section = self._build_projects_section()
        
        # Combine all sections
        complete_resume = f"""
{self.personal_info_data}
{profile_section}
{experience_section}
{skills_section}
{projects_section}
"""
        
        return complete_resume.strip()

    def _build_profile_section(self, profile_data: Dict) -> str:
        """Build the profile section."""
        profile_text = profile_data.get("profile", "")
        return f"""
## Profile

{profile_text}

---

"""

    def _build_experience_section(self) -> str:
        """Build the experience section from loaded data."""
        # Extract experience section (everything before "## Projects")
        projects_start = self.experience_data.find("## Projects")
        if projects_start != -1:
            return self.experience_data[:projects_start]
        return self.experience_data

    def _build_skills_section(self, profile_data: Dict) -> str:
        """Build the skills section."""
        skills_list = profile_data.get("skills", [])
        formatted_skills = [f"- {skill.split('(')[0].strip()}" for skill in skills_list]
        skills_text = "\n".join(formatted_skills)
        
        return f"""
## Skills
{skills_text}

"""

    def _build_projects_section(self) -> str:
        """Build the projects section from loaded data."""
        projects_start = self.experience_data.find("## Projects")
        skills_start = self.experience_data.find("## Skills")
        
        if projects_start != -1:
            if skills_start != -1:
                return self.experience_data[projects_start:skills_start]
            else:
                return self.experience_data[projects_start:]
        return ""

    def save_resume_content(self, content: str, output_file: str = "resume_data/complete_resume.md") -> str:
        """
        Save the generated resume content to a file.
        
        Args:
            content: The markdown content to save
            output_file: Path to save the file
            
        Returns:
            Path to the saved file
        """
        # Ensure directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file