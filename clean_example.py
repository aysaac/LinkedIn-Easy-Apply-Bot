from typing import Union
from openai import OpenAI
import json

with open(r"C:\Users\isaac\PycharmProjects\LinkedIn-Easy-Apply-Bot\resume_data\experience.md", "r") as f:
    experience = f.read()


OPEN_AI_SYSTEM_PROMPT = """
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


"""+ experience



#%%
JOB_POSTING_PROMPT ="""
About Krevera
Krevera builds AI-powered vision systems that spot defects on the factory floor before scrap happens. Our deep-learning pipelines detect anomalies in real-time, diagnose root causes, and feed insights back to injection-molding machines and robotics so that quality issues are fixed automatically.
We are a VC-backed startup (pre-seed raised) with our first paying customers and a clear path to scale.


Overview
As a Senior Machine Learning Engineer - Computer Vision, you’ll play a key role in developing Krevera’s Computer Vision & AI stack—helping build a robust data-to-deployment pipeline that gathers and generates training data, orchestrates cloud-scale training, and seamlessly pushes models to factory edge nodes for inference. You’ll contribute directly to innovation in multi-view vision transformers and VLMs, collaborating closely with Simulation and Software Engineering to keep every release production-ready and customer-focused.


Key Responsibilities
Contribute to the full AI pipeline: data collection & synthetic generation, cloud-scale distributed training (Ray on AWS), automated testing, and deployment to our inference systems.
Develop and refine state-of-the-art models (multi-view ViTs, VLMs) for real-time defect detection.
Support the engineering of ultra-reliable edge inference systems that meet stringent latency and throughput targets on factory hardware.
Implement and adhere to MLOps best practices—model versioning, monitoring, rollback, and CI/CD workflows.
Collaborate cross-functionally with Simulation, Software Engineering, and Sales to align technical deliverables with customer needs and ROI.


What We’re Looking For
A strong individual contributor who excels technically and helps those around them.
A good communicator adept at collaborating across multiple disciplines in a dynamic, fast-paced startup environment.
A creative problem solver excited by the challenge of innovating in an ever-evolving technology landscape.


Skills & Tools
Python and C++ programming proficiency; you write clean, production-ready code.
ROS 2 and OpenCV for orchestrating real-time inference on factory-floor devices.
PyTorch with experience building deep neural networks from the ground up.
Experience with multi-view architectures, Vision Transformers (ViT), and/or Vision-Language Models (VLMs).
Experience with distributed cloud computing using tools such as Ray (Anyscale).
Strong AWS background, especially EKS/Kubernetes, S3, etc.


Why Krevera
Collaborative, fun, innovative culture: Enjoy a startup environment with a flat hierarchy where teamwork and creativity thrive—whether brainstorming ideas, playing occasional video games over lunch, or taking company walks.
Real impact: Your work will directly shape our technology, culture, and growth from day one.
Front-row seat to AI in manufacturing: Help define a market that’s just beginning to explode.
Momentum & resources: Fresh off a venture-capital raise and 12 months of booked contracts, we have runway and customers eager for your models. We are well funded and moving fast!


Logistics
Location: On-site, Waltham, MA.
Compensation: Competitive salary + meaningful equity.
Benefits: Health insurance, dental, and 401(k).
Start date: ASAP – we’re moving fast.


How to Apply
Email careers.ai@krevera.com with your résumé, a brief note on why you’re excited to join, and links to any relevant papers, repos, or projects.
"""




#%%
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": OPEN_AI_SYSTEM_PROMPT},
        {"role": "user", "content": JOB_POSTING_PROMPT}
    ],
    temperature=0,
)
#%%

text = response.choices[0].message.content


def extract_json_from_text(text: str) -> dict:
    try:
        # Find the JSON content between the first { and last }
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        return {}
    return {}


parsed_response = extract_json_from_text(text)
#%%
