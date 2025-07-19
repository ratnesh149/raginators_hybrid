#!/usr/bin/env python3
"""
Complete HR Workflow Example
Demonstrates: Import resumes → Create JD → Shortlist candidates
"""

import os
from services.vector_db import get_vector_db
from tools.candidate_shortlist import candidate_shortlist_tool

def create_sample_resumes():
    """Create sample resume directory with mock data"""
    resume_dir = "./sample_resumes"
    os.makedirs(resume_dir, exist_ok=True)
    
    # Sample resume contents
    resumes = {
        "john_doe_frontend.txt": """
John Doe - Frontend Developer
Email: john.doe@email.com
Phone: (555) 123-4567

EXPERIENCE: 5 years

SKILLS:
- React.js, Vue.js, Angular
- JavaScript, TypeScript, HTML5, CSS3
- Node.js, Express.js
- Git, Webpack, Docker
- Responsive Design, UI/UX

EXPERIENCE:
Senior Frontend Developer at TechCorp (2021-2024)
- Built responsive web applications using React and TypeScript
- Collaborated with design team on UI/UX improvements
- Optimized application performance and accessibility

Frontend Developer at StartupXYZ (2019-2021)
- Developed single-page applications with Vue.js
- Implemented RESTful API integrations
- Mentored junior developers

EDUCATION:
Bachelor of Computer Science, State University (2019)
        """,
        
        "jane_smith_fullstack.txt": """
Jane Smith - Full Stack Developer
Email: jane.smith@email.com
Phone: (555) 987-6543

EXPERIENCE: 7 years

SKILLS:
- React, Angular, JavaScript, TypeScript
- Python, Django, Flask
- PostgreSQL, MongoDB
- AWS, Docker, Kubernetes
- GraphQL, REST APIs

EXPERIENCE:
Lead Full Stack Developer at BigTech Inc (2020-2024)
- Led team of 6 developers on enterprise applications
- Architected microservices using Python and React
- Implemented CI/CD pipelines and cloud infrastructure

Full Stack Developer at MidSize Corp (2017-2020)
- Developed web applications using Django and React
- Designed database schemas and optimized queries
- Integrated third-party APIs and payment systems

EDUCATION:
Master of Computer Science, Tech University (2017)
        """,
        
        "alex_johnson_backend.txt": """
Alex Johnson - Backend Developer
Email: alex.johnson@email.com
Phone: (555) 456-7890

EXPERIENCE: 4 years

SKILLS:
- Python, Java, Go
- Django, Spring Boot, FastAPI
- PostgreSQL, Redis, Elasticsearch
- Docker, Kubernetes, AWS
- Microservices, API Design

EXPERIENCE:
Backend Developer at CloudCorp (2022-2024)
- Built scalable APIs serving 1M+ requests/day
- Implemented caching strategies with Redis
- Designed microservices architecture

Junior Backend Developer at DataFlow (2020-2022)
- Developed REST APIs using Django
- Optimized database performance
- Implemented automated testing

EDUCATION:
Bachelor of Software Engineering, Code University (2020)
        """,
        
        "sarah_wilson_designer.txt": """
Sarah Wilson - UI/UX Designer & Frontend Developer
Email: sarah.wilson@email.com
Phone: (555) 321-0987

EXPERIENCE: 3 years

SKILLS:
- UI/UX Design, Figma, Adobe Creative Suite
- HTML5, CSS3, JavaScript
- React basics, Vue.js
- Responsive Design, Accessibility
- User Research, Prototyping

EXPERIENCE:
UI/UX Designer at DesignStudio (2022-2024)
- Created user interfaces for web and mobile applications
- Conducted user research and usability testing
- Collaborated with developers on implementation

Frontend Designer at Creative Agency (2021-2022)
- Designed and coded responsive websites
- Worked with clients on brand identity
- Basic React component development

EDUCATION:
Bachelor of Graphic Design, Art Institute (2021)
        """
    }
    
    # Write sample resumes
    for filename, content in resumes.items():
        with open(os.path.join(resume_dir, filename), 'w') as f:
            f.write(content.strip())
    
    print(f"✅ Created {len(resumes)} sample resumes in {resume_dir}/")
    return resume_dir

def import_resumes(resume_dir):
    """Import resumes into vector database"""
    print("\n📁 Importing resumes into vector database...")
    
    vector_db = get_vector_db()
    
    # Import each resume with metadata
    resume_files = [
        ("john_doe_frontend.txt", "John Doe", 5),
        ("jane_smith_fullstack.txt", "Jane Smith", 7),
        ("alex_johnson_backend.txt", "Alex Johnson", 4),
        ("sarah_wilson_designer.txt", "Sarah Wilson", 3)
    ]
    
    for filename, name, experience in resume_files:
        filepath = os.path.join(resume_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        metadata = {"experience_years": experience}
        vector_db.add_resume(name, content, metadata)
        print(f"   ✅ Added: {name} ({experience} years experience)")

def create_job_description():
    """Create a sample job description"""
    print("\n📝 Creating job description...")
    
    jd_content = """
Senior Frontend Developer

We are looking for an experienced Senior Frontend Developer to join our growing engineering team.

REQUIREMENTS:
- 4+ years of experience in frontend development
- Expert knowledge of React.js and TypeScript
- Strong understanding of HTML5, CSS3, and modern JavaScript
- Experience with state management (Redux, Context API)
- Knowledge of responsive design and cross-browser compatibility
- Experience with version control (Git) and CI/CD pipelines
- Strong problem-solving skills and attention to detail

PREFERRED QUALIFICATIONS:
- Experience with Node.js and backend integration
- Knowledge of testing frameworks (Jest, Cypress)
- Familiarity with cloud platforms (AWS, Azure)
- Experience with design systems and component libraries
- Leadership or mentoring experience

RESPONSIBILITIES:
- Develop and maintain high-quality web applications
- Collaborate with design and backend teams
- Code review and mentor junior developers
- Optimize application performance and user experience
- Stay updated with latest frontend technologies
    """
    
    vector_db = get_vector_db()
    metadata = {"department": "Engineering", "level": "Senior", "remote": True}
    vector_db.add_job_description("Senior Frontend Developer", jd_content, metadata)
    print("   ✅ Job description created and stored in vector database")
    
    return jd_content

def shortlist_candidates(job_requirements):
    """Shortlist candidates based on job requirements"""
    print("\n🎯 Shortlisting candidates...")
    
    # Use the shortlisting tool
    result = candidate_shortlist_tool._run(
        job_requirements="React TypeScript frontend 4+ years senior developer",
        min_experience=3,
        n_candidates=5
    )
    
    print(result)

def main():
    """Run the complete workflow"""
    print("🚀 HR Workflow Demo: Resume Import → JD Creation → Candidate Shortlisting")
    print("=" * 80)
    
    # Step 1: Create sample resumes
    resume_dir = create_sample_resumes()
    
    # Step 2: Import resumes
    import_resumes(resume_dir)
    
    # Step 3: Create job description
    jd_content = create_job_description()
    
    # Step 4: Shortlist candidates
    shortlist_candidates(jd_content)
    
    print("\n" + "=" * 80)
    print("🎉 Workflow completed successfully!")
    print("\nNext steps:")
    print("1. Run 'python run.py' to start the HR assistant")
    print("2. Ask: 'Help me shortlist candidates for a frontend developer role'")
    print("3. The assistant will use the vector database to find matching candidates")

if __name__ == "__main__":
    main()
