"""
Candidate Shortlisting Tool
Integrates with the HR Assistant to shortlist candidates based on job requirements
"""

from langchain.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from services.vector_db import get_vector_db
import logging

logger = logging.getLogger(__name__)

class CandidateShortlistInput(BaseModel):
    """Input for candidate shortlisting"""
    job_requirements: str = Field(description="Job requirements and skills to match against")
    min_experience: int = Field(default=0, description="Minimum years of experience required")
    n_candidates: int = Field(default=10, description="Number of top candidates to return")

class CandidateShortlistTool(BaseTool):
    """Tool to shortlist candidates based on job requirements"""
    name: str = "shortlist_candidates"
    description: str = "Shortlist and rank candidates from the resume database based on job requirements"
    args_schema: Type[BaseModel] = CandidateShortlistInput
    
    def _run(self, job_requirements: str, min_experience: int = 0, n_candidates: int = 10) -> str:
        """Shortlist candidates based on job requirements"""
        try:
            vector_db = get_vector_db()
            
            # Search for matching candidates
            results = vector_db.search_candidates(job_requirements, n_candidates * 2)  # Get more to filter
            
            if not results:
                return "No candidates found in the database matching the requirements."
            
            # Filter by experience if specified
            filtered_candidates = []
            for result in results:
                metadata = result.get('metadata', {})
                candidate_experience = metadata.get('experience_years', 0)
                
                if candidate_experience >= min_experience:
                    filtered_candidates.append(result)
                
                if len(filtered_candidates) >= n_candidates:
                    break
            
            if not filtered_candidates:
                return f"No candidates found with minimum {min_experience} years of experience."
            
            # Format results
            shortlist = []
            shortlist.append(f"🎯 **CANDIDATE SHORTLIST** (Top {len(filtered_candidates)} matches)")
            shortlist.append("=" * 60)
            
            for i, candidate in enumerate(filtered_candidates, 1):
                metadata = candidate.get('metadata', {})
                candidate_name = metadata.get('candidate_name', 'Unknown Candidate')
                experience = metadata.get('experience_years', 'Unknown')
                match_score = 1 - candidate.get('distance', 1)
                
                shortlist.append(f"\n**{i}. {candidate_name}**")
                shortlist.append(f"   📊 Match Score: {match_score:.2f}/1.00")
                shortlist.append(f"   💼 Experience: {experience} years")
                shortlist.append(f"   📝 Key Match: {candidate['content'][:150]}...")
                
                if match_score > 0.7:
                    shortlist.append("   ⭐ **HIGHLY RECOMMENDED**")
                elif match_score > 0.5:
                    shortlist.append("   ✅ **GOOD MATCH**")
                else:
                    shortlist.append("   ⚠️  **MODERATE MATCH**")
            
            shortlist.append(f"\n📈 **SUMMARY:**")
            shortlist.append(f"   • Total candidates in database: {len(results)}")
            shortlist.append(f"   • Candidates meeting experience requirement: {len(filtered_candidates)}")
            shortlist.append(f"   • Highly recommended (>70% match): {sum(1 for c in filtered_candidates if (1 - c.get('distance', 1)) > 0.7)}")
            
            return "\n".join(shortlist)
            
        except Exception as e:
            logger.error(f"Error shortlisting candidates: {e}")
            return f"Error shortlisting candidates: {str(e)}"

# Create the tool instance
candidate_shortlist_tool = CandidateShortlistTool()
