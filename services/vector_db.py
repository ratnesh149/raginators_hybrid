"""
Vector Database Service for HR Assistant
Handles document storage, retrieval, and similarity search
"""

import os
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HRVectorDB:
    """Vector database service for HR-related document storage and retrieval"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the vector database"""
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize Chroma client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize collections for different HR document types
        self.collections = {
            "job_descriptions": self._get_or_create_collection("job_descriptions"),
            "resumes": self._get_or_create_collection("resumes"),
            "hr_policies": self._get_or_create_collection("hr_policies"),
            "interview_questions": self._get_or_create_collection("interview_questions"),
            "company_info": self._get_or_create_collection("company_info")
        }
        
        # Text splitter for document chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(name)
    
    def add_job_description(self, job_title: str, description: str, metadata: Dict[str, Any] = None):
        """Add a job description to the vector database"""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "type": "job_description",
            "job_title": job_title,
            "timestamp": datetime.now().isoformat()
        })
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(description)
        
        # Add to collection
        for i, chunk in enumerate(chunks):
            doc_id = f"{job_title.lower().replace(' ', '_')}_{i}"
            self.collections["job_descriptions"].add(
                documents=[chunk],
                metadatas=[metadata],
                ids=[doc_id]
            )
        
        logger.info(f"Added job description for {job_title} with {len(chunks)} chunks")
    
    def add_resume(self, candidate_name: str, resume_text: str, metadata: Dict[str, Any] = None):
        """Add a resume to the vector database"""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "type": "resume",
            "candidate_name": candidate_name,
            "timestamp": datetime.now().isoformat()
        })
        
        chunks = self.text_splitter.split_text(resume_text)
        
        for i, chunk in enumerate(chunks):
            doc_id = f"{candidate_name.lower().replace(' ', '_')}_{i}"
            self.collections["resumes"].add(
                documents=[chunk],
                metadatas=[metadata],
                ids=[doc_id]
            )
        
        logger.info(f"Added resume for {candidate_name} with {len(chunks)} chunks")
    
    def add_hr_policy(self, policy_name: str, policy_text: str, metadata: Dict[str, Any] = None):
        """Add HR policy document to the vector database"""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "type": "hr_policy",
            "policy_name": policy_name,
            "timestamp": datetime.now().isoformat()
        })
        
        chunks = self.text_splitter.split_text(policy_text)
        
        for i, chunk in enumerate(chunks):
            doc_id = f"{policy_name.lower().replace(' ', '_')}_{i}"
            self.collections["hr_policies"].add(
                documents=[chunk],
                metadatas=[metadata],
                ids=[doc_id]
            )
        
        logger.info(f"Added HR policy {policy_name} with {len(chunks)} chunks")
    
    def search_similar_jobs(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar job descriptions"""
        results = self.collections["job_descriptions"].query(
            query_texts=[query],
            n_results=n_results
        )
        
        return self._format_search_results(results)
    
    def search_candidates(self, job_requirements: str, n_results: int = 10) -> List[Dict]:
        """Search for candidates matching job requirements"""
        results = self.collections["resumes"].query(
            query_texts=[job_requirements],
            n_results=n_results
        )
        
        return self._format_search_results(results)
    
    def search_hr_policies(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search HR policies for relevant information"""
        results = self.collections["hr_policies"].query(
            query_texts=[query],
            n_results=n_results
        )
        
        return self._format_search_results(results)
    
    def get_interview_questions(self, job_role: str, n_results: int = 10) -> List[Dict]:
        """Get relevant interview questions for a job role"""
        results = self.collections["interview_questions"].query(
            query_texts=[f"interview questions for {job_role}"],
            n_results=n_results
        )
        
        return self._format_search_results(results)
    
    def _format_search_results(self, results: Dict) -> List[Dict]:
        """Format search results into a consistent structure"""
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                result = {
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None,
                    "id": results['ids'][0][i] if results['ids'] else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def add_sample_data(self):
        """Add sample HR data for testing"""
        # Sample job descriptions
        sample_jobs = [
            {
                "title": "Frontend Developer",
                "description": """We are looking for a skilled Frontend Developer to join our team. 
                Requirements: React, JavaScript, HTML, CSS, TypeScript. 
                Experience with modern frameworks and responsive design. 
                3+ years experience required.""",
                "metadata": {"department": "Engineering", "level": "Mid", "remote": True}
            },
            {
                "title": "Data Scientist",
                "description": """Seeking a Data Scientist with expertise in machine learning and analytics. 
                Requirements: Python, SQL, TensorFlow, scikit-learn, statistics. 
                Experience with big data and cloud platforms. 
                5+ years experience required.""",
                "metadata": {"department": "Data", "level": "Senior", "remote": False}
            },
            {
                "title": "Backend Developer",
                "description": """Looking for a Backend Developer with strong API development skills.
                Requirements: Python, Django, PostgreSQL, REST APIs, Docker.
                Experience with cloud platforms and microservices.
                4+ years experience required.""",
                "metadata": {"department": "Engineering", "level": "Senior", "remote": True}
            }
        ]
        
        for job in sample_jobs:
            self.add_job_description(job["title"], job["description"], job["metadata"])
        
        # Sample resumes
        sample_resumes = [
            {
                "name": "John Doe",
                "resume": """John Doe - Senior Frontend Developer
                Email: john.doe@email.com | Phone: (555) 123-4567
                
                EXPERIENCE: 5 years
                
                SKILLS:
                - React, JavaScript, TypeScript, HTML5, CSS3
                - Redux, Next.js, Vue.js
                - Responsive Design, Mobile-First Development
                - Git, Webpack, npm, yarn
                - REST APIs, GraphQL
                - Testing: Jest, Cypress, React Testing Library
                
                EXPERIENCE:
                Senior Frontend Developer at TechCorp (2021-2024)
                - Led development of React-based web applications
                - Implemented responsive designs for mobile and desktop
                - Collaborated with backend teams on API integration
                - Mentored junior developers
                
                Frontend Developer at StartupXYZ (2019-2021)
                - Built user interfaces using React and TypeScript
                - Optimized application performance and loading times
                - Implemented automated testing strategies""",
                "metadata": {
                    "experience_years": 5,
                    "skills": "React, JavaScript, TypeScript, HTML, CSS",
                    "email": "john.doe@email.com",
                    "phone": "(555) 123-4567"
                }
            },
            {
                "name": "Jane Smith",
                "resume": """Jane Smith - Data Scientist
                Email: jane.smith@email.com | Phone: (555) 234-5678
                
                EXPERIENCE: 7 years
                
                SKILLS:
                - Python, R, SQL, Scala
                - Machine Learning: scikit-learn, TensorFlow, PyTorch
                - Data Analysis: pandas, numpy, matplotlib, seaborn
                - Big Data: Spark, Hadoop, Kafka
                - Cloud: AWS, GCP, Azure
                - Statistics, A/B Testing, Experimental Design
                
                EXPERIENCE:
                Senior Data Scientist at DataTech Inc (2020-2024)
                - Developed ML models for customer segmentation and recommendation systems
                - Led data science projects from conception to production
                - Collaborated with engineering teams to deploy models at scale
                - Mentored junior data scientists
                
                Data Scientist at Analytics Corp (2017-2020)
                - Built predictive models for business forecasting
                - Performed statistical analysis and hypothesis testing
                - Created data visualizations and dashboards""",
                "metadata": {
                    "experience_years": 7,
                    "skills": "Python, Machine Learning, SQL, TensorFlow, Statistics",
                    "email": "jane.smith@email.com",
                    "phone": "(555) 234-5678"
                }
            },
            {
                "name": "Mike Johnson",
                "resume": """Mike Johnson - Backend Developer
                Email: mike.johnson@email.com | Phone: (555) 345-6789
                
                EXPERIENCE: 4 years
                
                SKILLS:
                - Python, Django, Flask, FastAPI
                - PostgreSQL, MySQL, MongoDB
                - REST APIs, GraphQL
                - Docker, Kubernetes
                - AWS, GCP
                - Redis, Celery
                - Git, CI/CD, Jenkins
                
                EXPERIENCE:
                Backend Developer at CloudSoft (2022-2024)
                - Designed and implemented RESTful APIs using Django
                - Optimized database queries and improved application performance
                - Implemented microservices architecture
                - Set up CI/CD pipelines and automated testing
                
                Junior Backend Developer at WebSolutions (2020-2022)
                - Developed web applications using Python and Django
                - Worked with PostgreSQL databases
                - Integrated third-party APIs and services""",
                "metadata": {
                    "experience_years": 4,
                    "skills": "Python, Django, PostgreSQL, REST APIs, Docker",
                    "email": "mike.johnson@email.com",
                    "phone": "(555) 345-6789"
                }
            },
            {
                "name": "Sarah Wilson",
                "resume": """Sarah Wilson - Full Stack Developer
                Email: sarah.wilson@email.com | Phone: (555) 456-7890
                
                EXPERIENCE: 3 years
                
                SKILLS:
                - Frontend: React, JavaScript, TypeScript, HTML, CSS
                - Backend: Node.js, Express, Python, Django
                - Databases: PostgreSQL, MongoDB
                - Cloud: AWS, Heroku
                - DevOps: Docker, Git, CI/CD
                
                EXPERIENCE:
                Full Stack Developer at InnovateTech (2021-2024)
                - Built end-to-end web applications using React and Node.js
                - Developed RESTful APIs and integrated with databases
                - Implemented responsive designs and user interfaces
                - Collaborated with designers and product managers
                
                Junior Developer at StartupHub (2021)
                - Assisted in frontend development using React
                - Learned backend development with Node.js and Express""",
                "metadata": {
                    "experience_years": 3,
                    "skills": "React, JavaScript, Node.js, Python, Full Stack",
                    "email": "sarah.wilson@email.com",
                    "phone": "(555) 456-7890"
                }
            }
        ]
        
        for resume in sample_resumes:
            self.add_resume(resume["name"], resume["resume"], resume["metadata"])
        
        # Sample interview questions
        interview_questions = [
            "Tell me about your experience with React and modern JavaScript frameworks",
            "How do you approach responsive web design?",
            "Describe your experience with version control systems like Git",
            "What's your process for debugging frontend issues?",
            "How do you ensure cross-browser compatibility?",
            "Explain your experience with machine learning algorithms",
            "How do you handle missing data in your datasets?",
            "Describe your approach to A/B testing and experimental design",
            "What's your experience with cloud platforms like AWS or GCP?",
            "How do you optimize database queries for performance?"
        ]
        
        for i, question in enumerate(interview_questions):
            category = "frontend" if i < 5 else "data_science" if i < 8 else "backend"
            self.collections["interview_questions"].add(
                documents=[question],
                metadatas=[{"type": "interview_question", "category": category}],
                ids=[f"{category}_q_{i}"]
            )
        
        logger.info("Added sample data to vector database")

# Global instance
vector_db = None

def get_vector_db() -> HRVectorDB:
    """Get or create the global vector database instance"""
    global vector_db
    if vector_db is None:
        vector_db = HRVectorDB()
    return vector_db
