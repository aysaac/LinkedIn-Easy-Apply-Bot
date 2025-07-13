from typing import Union
from openai import OpenAI
import json

with open(r"C:\Users\isaac\PycharmProjects\LinkedIn-Easy-Apply-Bot\resume_data\experience.md", "r",
          encoding='utf-8') as f:
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
Our team is responsible for developing state-of-the-art CV/NLP/ML algorithms and strategies to improve user consumption experience, inspire merchants' service quality and revenue, and build a fair and flourishing ecosystem on our E-commerce Platform. More specifically, our team is responsible for the algorithms of Product Knowledge Graphs under TikTok's global e-commerce business.

What You Will Do:

 Participate in the development of massive knowledge graphs of real-world products to support feed ranking, recommendations, and ads.
 Collaborate with product managers, data scientists, and the product strategy & operation team to define product strategies and features.

Responsibilities:

 Knowledge graph construction, including product/content/feedback understanding and category/brand/SPU construction.
 Explore the implementation of Knowledge Graph and Cognitive Graph on the e-commerce side of TikTok e-commerce shopping guide.
 Responsible for the mining of e-commerce shopping guide knowledge such as shopping scenes/people/goods matching/product layering.
 Responsible for the optimization and iteration of computer vision related models in the e-commerce scene, including fine grain classification, product object recognition, product subject recognition, feature extraction, logo detection, brand recognition, etc., to optimize the merchant's product loading and unloading process.
 Responsible for e-commerce short video and livestream classification, multi-modal content mining, multi-modal content understanding, optimize e-commerce short video and livestream shopping experience.
 Responsible for e-commerce image search, photo search goods, goods duplication algorithm.
 Explore the cutting-edge technology of computer vision, responsible for the iteration and evolution of the overall algorithm and system.

Qualifications

Minimum Qualifications

In-depth knowledge in a certain field of multimedia and computer vision, including but not limited to: image search, image/video classification and recognition, image segmentation, object detection, OCR, graph neural networks, multimodal, unsupervised and self-supervised learning, etc.;
 Familiar with the training and deployment of one or more framework models of TensorFlow/PyTorch/MXNet, and understand training acceleration methods such as hybrid precision training and distributed training;

Job Information

【For Pay Transparency】Compensation Description (Annually)

The base salary range for this position in the selected city is $145000 - $355000 annually.

Compensation may vary outside of this range depending on a number of factors, including a candidate’s qualifications, skills, competencies and experience, and location. Base pay is one part of the Total Package that is provided to compensate and recognize employees for their work, and this role may be eligible for additional discretionary bonuses/incentives, and restricted stock units.

Benefits may vary depending on the nature of employment and the country work location. Employees have day one access to medical, dental, and vision insurance, a 401(k) savings plan with company match, paid parental leave, short-term and long-term disability coverage, life insurance, wellbeing benefits, among others. Employees also receive 10 paid holidays per year, 10 paid sick days per year and 17 days of Paid Personal Time (prorated upon hire with increasing accruals by tenure).

The Company reserves the right to modify or change these benefits programs at any time, with or without notice.

For Los Angeles County (unincorporated) Candidates:

Qualified applicants with arrest or conviction records will be considered for employment in accordance with all federal, state, and local laws including the Los Angeles County Fair Chance Ordinance for Employers and the California Fair Chance Act. Our company believes that criminal history may have a direct, adverse and negative relationship on the following job duties, potentially resulting in the withdrawal of the conditional offer of employment:

 Interacting and occasionally having unsupervised contact with internal/external clients and/or colleagues;
 Appropriately handling and managing confidential information including proprietary and trade secret information and access to information technology systems; and
 Exercising sound judgment.

About TikTok

TikTok is the leading destination for short-form mobile video. At TikTok, our mission is to inspire creativity and bring joy. TikTok's global headquarters are in Los Angeles and Singapore, and we also have offices in New York City, London, Dublin, Paris, Berlin, Dubai, Jakarta, Seoul, and Tokyo.

Why Join Us

Inspiring creativity is at the core of TikTok's mission. Our innovative product is built to help people authentically express themselves, discover and connect – and our global, diverse teams make that possible. Together, we create value for our communities, inspire creativity and bring joy - a mission we work towards every day.

We strive to do great things with great people. We lead with curiosity, humility, and a desire to make impact in a rapidly growing tech company. Every challenge is an opportunity to learn and innovate as one team. We're resilient and embrace challenges as they come. By constantly iterating and fostering an "Always Day 1" mindset, we achieve meaningful breakthroughs for ourselves, our company, and our users. When we create and grow together, the possibilities are limitless. Join us.

Diversity & Inclusion

TikTok is committed to creating an inclusive space where employees are valued for their skills, experiences, and unique perspectives. Our platform connects people from across the globe and so does our workplace. At TikTok, our mission is to inspire creativity and bring joy. To achieve that goal, we are committed to celebrating our diverse voices and to creating an environment that reflects the many communities we reach. We are passionate about this and hope you are too.

TikTok Accommodation

TikTok is committed to providing reasonable accommodations in our recruitment processes for candidates with disabilities, pregnancy, sincerely held religious beliefs or other reasons protected by applicable laws. If you need assistance or a reasonable accommodation, please reach out to us at https://tinyurl.com/RA-request
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
with open(r"C:\Users\isaac\PycharmProjects\LinkedIn-Easy-Apply-Bot\resume_data\personal_info.md", "r",
          encoding='utf-8') as f:
    personal_info=f.read()

PROFILE_TEMPLATE=f"""
## Profile

{parsed_response.get("profile", "")}

---

"""

EXPERIENCE_TEMPLATE=experience[:experience.find("## Projects")]

Projects=experience[experience.find("## Projects"):experience.find("## Skills")]

SKILL_LIST = [("- " + x.split('(')[0].strip()) for x in parsed_response.get("skills", [])]
SKILL_LIST="\n".join(SKILL_LIST)

SKILL_TEMPLATE = f"""
## Skills
{SKILL_LIST}

"""

COMPLETE_MARKDOWN=f"""
{personal_info}
{PROFILE_TEMPLATE}
{EXPERIENCE_TEMPLATE}
{SKILL_TEMPLATE}

{Projects}

"""

with open(r"C:\Users\isaac\PycharmProjects\LinkedIn-Easy-Apply-Bot\resume_data\complete_resume.md", "w",encoding="utf-8") as f:
    f.write(COMPLETE_MARKDOWN)


