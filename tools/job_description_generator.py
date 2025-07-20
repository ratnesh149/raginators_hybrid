"""
Job Description Generator Tool
Generates professional job descriptions based on form inputs
"""

from langchain.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class JobDescriptionInput(BaseModel):
    """Input for job description generation"""
    job_title: str = Field(description="Job title/position")
    required_skills: str = Field(default="", description="Required skills and technologies")
    experience_level: str = Field(default="Any", description="Experience level requirement")
    location: str = Field(default="", description="Job location or remote work preference")
    education: str = Field(default="Any", description="Education level requirement")
    company_name: str = Field(default="Our Company", description="Company name")
    department: str = Field(default="", description="Department or team")

class JobDescriptionGenerator(BaseTool):
    """Tool to generate professional job descriptions based on form inputs"""
    name: str = "generate_job_description"
    description: str = "Generate a professional job description based on job requirements and criteria"
    args_schema: Type[BaseModel] = JobDescriptionInput
    
    def _generate_responsibilities(self, job_title: str, skills: list) -> list:
        """Generate job responsibilities based on title and skills"""
        responsibilities = []
        
        # Base responsibilities based on job title
        if "software engineer" in job_title.lower() or "developer" in job_title.lower():
            responsibilities.extend([
                "Design, develop, and maintain high-quality software applications",
                "Collaborate with cross-functional teams to define and implement new features",
                "Write clean, maintainable, and efficient code following best practices",
                "Participate in code reviews and provide constructive feedback",
                "Debug and resolve technical issues in a timely manner"
            ])
        elif "data scientist" in job_title.lower() or "analyst" in job_title.lower():
            responsibilities.extend([
                "Analyze large datasets to extract meaningful insights and patterns",
                "Develop and implement machine learning models and algorithms",
                "Create data visualizations and reports for stakeholders",
                "Collaborate with business teams to understand requirements",
                "Present findings and recommendations to leadership"
            ])
        elif "product manager" in job_title.lower():
            responsibilities.extend([
                "Define product strategy and roadmap based on market research",
                "Collaborate with engineering and design teams to deliver features",
                "Gather and prioritize product requirements from stakeholders",
                "Monitor product performance and user feedback",
                "Coordinate product launches and go-to-market strategies"
            ])
        else:
            # Generic responsibilities
            responsibilities.extend([
                f"Execute core {job_title.lower()} responsibilities with excellence",
                "Collaborate effectively with team members and stakeholders",
                "Contribute to project planning and execution",
                "Maintain high standards of quality and professionalism",
                "Support continuous improvement initiatives"
            ])
        
        # Add skill-specific responsibilities
        if any(skill.lower() in ['react', 'javascript', 'frontend'] for skill in skills):
            responsibilities.append("Develop responsive and user-friendly frontend interfaces")
        
        if any(skill.lower() in ['python', 'java', 'backend', 'api'] for skill in skills):
            responsibilities.append("Build and maintain robust backend systems and APIs")
        
        if any(skill.lower() in ['aws', 'azure', 'cloud', 'devops'] for skill in skills):
            responsibilities.append("Manage cloud infrastructure and deployment processes")
        
        if any(skill.lower() in ['sql', 'database', 'mongodb'] for skill in skills):
            responsibilities.append("Design and optimize database schemas and queries")
        
        return responsibilities[:6]  # Limit to 6 key responsibilities
    
    def _generate_requirements(self, experience_level: str, education: str, skills: list) -> Dict[str, list]:
        """Generate job requirements based on inputs"""
        
        # Experience requirements
        experience_req = []
        if experience_level != "Any":
            if "0-2" in experience_level:
                experience_req.append("0-2 years of relevant professional experience")
                experience_req.append("Strong foundation in computer science fundamentals")
            elif "3-5" in experience_level:
                experience_req.append("3-5 years of hands-on experience in software development")
                experience_req.append("Proven track record of delivering quality projects")
            elif "6-10" in experience_level:
                experience_req.append("6-10 years of senior-level experience")
                experience_req.append("Experience leading technical projects and mentoring junior developers")
            elif "10+" in experience_level:
                experience_req.append("10+ years of expert-level experience")
                experience_req.append("Demonstrated leadership in technical architecture and strategy")
        else:
            experience_req.append("Relevant professional experience preferred")
        
        # Education requirements
        education_req = []
        if education != "Any":
            if education == "High School":
                education_req.append("High school diploma or equivalent")
            elif education == "Bachelor's":
                education_req.append("Bachelor's degree in Computer Science, Engineering, or related field")
            elif education == "Master's":
                education_req.append("Master's degree in Computer Science, Engineering, or related field")
            elif education == "PhD":
                education_req.append("PhD in Computer Science, Engineering, or related field")
        else:
            education_req.append("Relevant education or equivalent experience")
        
        # Technical requirements based on skills
        technical_req = []
        if skills:
            technical_req.append(f"Proficiency in: {', '.join(skills[:5])}")
            
            # Add specific technical requirements
            if any(skill.lower() in ['react', 'javascript'] for skill in skills):
                technical_req.append("Strong knowledge of modern JavaScript frameworks and libraries")
            
            if any(skill.lower() in ['python', 'java'] for skill in skills):
                technical_req.append("Experience with object-oriented programming and design patterns")
            
            if any(skill.lower() in ['aws', 'cloud'] for skill in skills):
                technical_req.append("Experience with cloud platforms and distributed systems")
        
        # Soft skills
        soft_skills = [
            "Excellent problem-solving and analytical skills",
            "Strong communication and collaboration abilities",
            "Self-motivated with ability to work independently",
            "Attention to detail and commitment to quality"
        ]
        
        return {
            "experience": experience_req,
            "education": education_req,
            "technical": technical_req,
            "soft_skills": soft_skills
        }
    
    def _generate_benefits(self) -> list:
        """Generate standard benefits package"""
        return [
            "Competitive salary and performance-based bonuses",
            "Comprehensive health, dental, and vision insurance",
            "Flexible work arrangements and remote work options",
            "Professional development opportunities and training budget",
            "401(k) retirement plan with company matching",
            "Generous PTO and paid holidays",
            "Modern equipment and technology stipend",
            "Collaborative and inclusive work environment"
        ]
    
    def _run(self, job_title: str, required_skills: str = "", experience_level: str = "Any", 
             location: str = "", education: str = "Any", company_name: str = "Our Company", 
             department: str = "") -> str:
        """Generate a professional job description"""
        
        try:
            # Parse skills
            skills = []
            if required_skills:
                skills = [skill.strip() for skill in required_skills.replace('\n', ',').split(',') if skill.strip()]
            
            # Generate job description components
            responsibilities = self._generate_responsibilities(job_title, skills)
            requirements = self._generate_requirements(experience_level, education, skills)
            benefits = self._generate_benefits()
            
            # Build the job description
            job_description = []
            
            # Header
            job_description.append(f"# {job_title}")
            if department:
                job_description.append(f"**Department:** {department}")
            if location:
                job_description.append(f"**Location:** {location}")
            else:
                job_description.append("**Location:** Remote/Hybrid")
            
            if experience_level != "Any":
                exp_display = experience_level.replace("Level ", "").replace("(", "- ").replace(")", "")
                job_description.append(f"**Experience Level:** {exp_display}")
            
            job_description.append("")
            
            # Company overview
            job_description.append("## About the Role")
            job_description.append(f"We are seeking a talented {job_title} to join our dynamic team at {company_name}. This is an exciting opportunity to work on cutting-edge projects and make a significant impact in a collaborative environment.")
            job_description.append("")
            
            # Key responsibilities
            job_description.append("## Key Responsibilities")
            for responsibility in responsibilities:
                job_description.append(f"• {responsibility}")
            job_description.append("")
            
            # Requirements
            job_description.append("## Requirements")
            
            if requirements["experience"]:
                job_description.append("### Experience")
                for req in requirements["experience"]:
                    job_description.append(f"• {req}")
                job_description.append("")
            
            if requirements["education"]:
                job_description.append("### Education")
                for req in requirements["education"]:
                    job_description.append(f"• {req}")
                job_description.append("")
            
            if requirements["technical"]:
                job_description.append("### Technical Skills")
                for req in requirements["technical"]:
                    job_description.append(f"• {req}")
                job_description.append("")
            
            job_description.append("### Soft Skills")
            for skill in requirements["soft_skills"]:
                job_description.append(f"• {skill}")
            job_description.append("")
            
            # Benefits
            job_description.append("## What We Offer")
            for benefit in benefits:
                job_description.append(f"• {benefit}")
            job_description.append("")
            
            # Call to action
            job_description.append("## How to Apply")
            job_description.append(f"If you're passionate about {job_title.lower()} and ready to take on exciting challenges, we'd love to hear from you! Please submit your resume and a brief cover letter explaining why you're the perfect fit for this role.")
            job_description.append("")
            job_description.append(f"*{company_name} is an equal opportunity employer committed to diversity and inclusion.*")
            
            return "\n".join(job_description)
            
        except Exception as e:
            logger.error(f"Error generating job description: {e}")
            return f"Error generating job description: {str(e)}"

# Create the tool instance
job_description_generator = JobDescriptionGenerator()
