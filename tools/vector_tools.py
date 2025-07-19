"""
Vector Database Tools for HR Assistant Agents
Provides search and retrieval capabilities using vector similarity
"""

from langchain.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from services.vector_db import get_vector_db
import logging

logger = logging.getLogger(__name__)

class JobSearchInput(BaseModel):
    """Input for job description search"""
    query: str = Field(description="Search query for similar job descriptions")
    n_results: int = Field(default=5, description="Number of results to return")

class CandidateSearchInput(BaseModel):
    """Input for candidate search"""
    job_requirements: str = Field(description="Job requirements to match against resumes")
    n_results: int = Field(default=10, description="Number of candidates to return")

class PolicySearchInput(BaseModel):
    """Input for HR policy search"""
    query: str = Field(description="Query for HR policy information")
    n_results: int = Field(default=5, description="Number of policy results to return")

class InterviewQuestionsInput(BaseModel):
    """Input for interview questions search"""
    job_role: str = Field(description="Job role to get interview questions for")
    n_results: int = Field(default=10, description="Number of questions to return")

class JobDescriptionSearchTool(BaseTool):
    """Tool to search for similar job descriptions"""
    name: str = "search_similar_jobs"
    description: str = "Search for similar job descriptions in the database to get inspiration and templates"
    args_schema: Type[BaseModel] = JobSearchInput
    
    def _run(self, query: str, n_results: int = 5) -> str:
        """Search for similar job descriptions"""
        try:
            vector_db = get_vector_db()
            results = vector_db.search_similar_jobs(query, n_results)
            
            if not results:
                return "No similar job descriptions found."
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                job_title = metadata.get('job_title', 'Unknown')
                department = metadata.get('department', 'Unknown')
                level = metadata.get('level', 'Unknown')
                
                formatted_results.append(
                    f"{i}. **{job_title}** ({department}, {level})\n"
                    f"   {result['content'][:200]}...\n"
                )
            
            return "Similar Job Descriptions Found:\n\n" + "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error searching job descriptions: {e}")
            return f"Error searching job descriptions: {str(e)}"

class CandidateSearchTool(BaseTool):
    """Tool to search for candidates matching job requirements"""
    name: str = "search_candidates"
    description: str = "Search for candidates whose resumes match specific job requirements"
    args_schema: Type[BaseModel] = CandidateSearchInput
    
    def _run(self, job_requirements: str, n_results: int = 10) -> str:
        """Search for matching candidates"""
        try:
            vector_db = get_vector_db()
            results = vector_db.search_candidates(job_requirements, n_results)
            
            if not results:
                return "No matching candidates found in the database."
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                candidate_name = metadata.get('candidate_name', 'Unknown')
                
                formatted_results.append(
                    f"{i}. **{candidate_name}**\n"
                    f"   Match: {result['content'][:150]}...\n"
                    f"   Similarity Score: {1 - result.get('distance', 1):.2f}\n"
                )
            
            return "Matching Candidates Found:\n\n" + "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error searching candidates: {e}")
            return f"Error searching candidates: {str(e)}"

class HRPolicySearchTool(BaseTool):
    """Tool to search HR policies and guidelines"""
    name: str = "search_hr_policies"
    description: str = "Search HR policies and company guidelines for relevant information"
    args_schema: Type[BaseModel] = PolicySearchInput
    
    def _run(self, query: str, n_results: int = 5) -> str:
        """Search HR policies"""
        try:
            vector_db = get_vector_db()
            results = vector_db.search_hr_policies(query, n_results)
            
            if not results:
                return "No relevant HR policies found."
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                policy_name = metadata.get('policy_name', 'Unknown Policy')
                
                formatted_results.append(
                    f"{i}. **{policy_name}**\n"
                    f"   {result['content'][:200]}...\n"
                )
            
            return "Relevant HR Policies:\n\n" + "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error searching HR policies: {e}")
            return f"Error searching HR policies: {str(e)}"

class InterviewQuestionsTool(BaseTool):
    """Tool to get relevant interview questions for a job role"""
    name: str = "get_interview_questions"
    description: str = "Get relevant interview questions for a specific job role"
    args_schema: Type[BaseModel] = InterviewQuestionsInput
    
    def _run(self, job_role: str, n_results: int = 10) -> str:
        """Get interview questions for a job role"""
        try:
            vector_db = get_vector_db()
            results = vector_db.get_interview_questions(job_role, n_results)
            
            if not results:
                return f"No interview questions found for {job_role}."
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(f"{i}. {result['content']}")
            
            return f"Interview Questions for {job_role}:\n\n" + "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Error getting interview questions: {e}")
            return f"Error getting interview questions: {str(e)}"

# Export all tools
from .candidate_shortlist import candidate_shortlist_tool

vector_tools = [
    JobDescriptionSearchTool(),
    CandidateSearchTool(),
    HRPolicySearchTool(),
    InterviewQuestionsTool(),
    candidate_shortlist_tool
]
