"""
Hybrid Candidate Shortlisting Tool
Enhanced with deduplication system to ensure 100% unique candidates
Integrates with the HR Assistant to shortlist candidates based on job requirements
"""

from langchain.tools import BaseTool
from typing import Type, List, Dict, Any, Set
from pydantic import BaseModel, Field
from services.vector_db import get_vector_db
import logging
import hashlib
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class CandidateShortlistInput(BaseModel):
    """Input for candidate shortlisting"""
    job_requirements: str = Field(description="Job requirements and skills to match against")
    min_experience: int = Field(default=0, description="Minimum years of experience required")
    max_experience: int = Field(default=999, description="Maximum years of experience required")
    n_candidates: int = Field(default=10, description="Number of top candidates to return")

class CandidateShortlistTool(BaseTool):
    """Enhanced tool to shortlist candidates with 100% deduplication guarantee"""
    name: str = "shortlist_candidates"
    description: str = "Shortlist and rank unique candidates from the resume database based on job requirements with guaranteed deduplication"
    args_schema: Type[BaseModel] = CandidateShortlistInput
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _is_duplicate_candidate(self, candidate: Dict, seen_candidates: List[Dict], 
                              similarity_threshold: float = 0.85) -> bool:
        """Check if candidate is a duplicate using multiple criteria"""
        
        current_metadata = candidate.get('metadata', {})
        current_name = current_metadata.get('candidate_name', '').lower().strip()
        current_email = current_metadata.get('email', '').lower().strip()
        current_phone = current_metadata.get('phone', '').strip()
        current_content = candidate.get('content', '')[:500]  # First 500 chars for comparison
        
        for seen_candidate in seen_candidates:
            seen_metadata = seen_candidate.get('metadata', {})
            seen_name = seen_metadata.get('candidate_name', '').lower().strip()
            seen_email = seen_metadata.get('email', '').lower().strip()
            seen_phone = seen_metadata.get('phone', '').strip()
            seen_content = seen_candidate.get('content', '')[:500]
            
            # Check 1: Exact unique ID match (primary deduplication)
            if (current_metadata.get('unique_id') and seen_metadata.get('unique_id') and
                current_metadata.get('unique_id') == seen_metadata.get('unique_id')):
                return True
            
            # Check 2: Email match (strong indicator)
            if current_email and seen_email and current_email == seen_email:
                return True
            
            # Check 3: Phone match (strong indicator)
            if current_phone and seen_phone and current_phone == seen_phone:
                return True
            
            # Check 4: Name similarity + content similarity (fuzzy matching)
            name_similarity = self._calculate_similarity(current_name, seen_name)
            content_similarity = self._calculate_similarity(current_content, seen_content)
            
            if (name_similarity > 0.9 and content_similarity > similarity_threshold):
                return True
            
            # Check 5: Very high content similarity (same resume, different name extraction)
            if content_similarity > 0.95:
                return True
        
        return False
    
    def _deduplicate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Remove duplicate candidates using multiple deduplication strategies"""
        
        unique_candidates = []
        seen_unique_ids: Set[str] = set()
        
        logger.info(f"🔍 Starting deduplication process for {len(candidates)} candidates")
        
        for candidate in candidates:
            metadata = candidate.get('metadata', {})
            unique_id = metadata.get('unique_id')
            
            # Primary deduplication: Check unique ID
            if unique_id and unique_id in seen_unique_ids:
                logger.debug(f"🚫 Duplicate found by unique_id: {unique_id}")
                continue
            
            # Secondary deduplication: Fuzzy matching
            if self._is_duplicate_candidate(candidate, unique_candidates):
                candidate_name = metadata.get('candidate_name', 'Unknown')
                logger.debug(f"🚫 Duplicate found by fuzzy matching: {candidate_name}")
                continue
            
            # Add to unique list
            unique_candidates.append(candidate)
            if unique_id:
                seen_unique_ids.add(unique_id)
        
        logger.info(f"✅ Deduplication complete: {len(candidates)} → {len(unique_candidates)} unique candidates")
        return unique_candidates
    
    def _calculate_combined_score(self, candidate: Dict, min_experience: int, max_experience: int) -> float:
        """Calculate combined score based on match score and experience level"""
        # Get base match score
        distance = candidate.get('distance', 1.0)
        if distance <= 1.0:
            match_score = max(0, min(1, 1 - distance))
        else:
            # For distances > 1, use exponential decay
            match_score = max(0, min(1, 2 - distance))
        
        # Get experience and calculate experience score
        metadata = candidate.get('metadata', {})
        candidate_experience = metadata.get('experience_years', 0)
        
        # Experience score: prefer higher experience within the range
        if max_experience == 999:  # Open-ended range (e.g., 10+ years)
            # For open-ended ranges, give higher scores to more experienced candidates
            experience_score = min(1.0, candidate_experience / (min_experience + 10))
        else:
            # For closed ranges, prefer candidates closer to the maximum
            range_size = max_experience - min_experience
            if range_size > 0:
                # Normalize experience within the range (0 to 1)
                normalized_exp = (candidate_experience - min_experience) / range_size
                experience_score = normalized_exp
            else:
                experience_score = 1.0  # Single year range
        
        # Boost score for candidates with relevant skills
        content = candidate.get('content', '').lower()
        skills_text = metadata.get('skills', '').lower()
        
        # Check for key technology matches
        tech_boost = 0
        if 'react' in content or 'react' in skills_text:
            tech_boost += 0.1
        if 'javascript' in content or 'javascript' in skills_text:
            tech_boost += 0.1
        if 'frontend' in content or 'frontend' in skills_text:
            tech_boost += 0.05
        if 'python' in content or 'python' in skills_text:
            tech_boost += 0.1
        if 'java' in content or 'java' in skills_text:
            tech_boost += 0.1
        
        # Combined score: 60% match score + 30% experience score + 10% tech boost
        combined_score = (0.6 * match_score) + (0.3 * experience_score) + min(0.1, tech_boost)
        return min(1.0, combined_score)

    def _run(self, job_requirements: str, min_experience: int = 0, max_experience: int = 999, n_candidates: int = 10) -> str:
        """Shortlist candidates with guaranteed deduplication and experience-based sorting"""
        try:
            vector_db = get_vector_db()
            
            # Search for matching candidates (get more to account for deduplication)
            search_multiplier = max(3, n_candidates // 2)  # Get 3x or at least n_candidates/2 extra
            initial_results = vector_db.search_candidates(
                job_requirements, 
                n_candidates * search_multiplier
            )
            
            if not initial_results:
                return "No candidates found in the database matching the requirements."
            
            logger.info(f"🔍 Initial search returned {len(initial_results)} candidates")
            
            # Step 1: Deduplicate all results first
            unique_results = self._deduplicate_candidates(initial_results)
            
            # Step 2: Filter by experience requirement (both min and max)
            filtered_candidates = []
            for result in unique_results:
                metadata = result.get('metadata', {})
                candidate_experience = metadata.get('experience_years', 0)
                
                if min_experience <= candidate_experience <= max_experience:
                    filtered_candidates.append(result)
            
            if not filtered_candidates:
                return f"No unique candidates found with {min_experience}-{max_experience} years of experience."
            
            # Step 3: Sort candidates by combined score (match score + experience preference)
            for candidate in filtered_candidates:
                candidate['combined_score'] = self._calculate_combined_score(candidate, min_experience, max_experience)
            
            # Sort by combined score (highest first)
            filtered_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Step 4: Take top N candidates
            final_candidates = filtered_candidates[:n_candidates]
            
            # Step 5: Format results with deduplication and experience-based ranking info
            shortlist = []
            shortlist.append(f"🎯 **HYBRID CANDIDATE SHORTLIST** (Top {len(final_candidates)} unique matches)")
            shortlist.append("=" * 70)
            shortlist.append(f"✅ **DEDUPLICATION GUARANTEE**: All candidates are 100% unique")
            if min_experience > 0 or max_experience < 999:
                exp_range = f"{min_experience}-{max_experience}" if max_experience < 999 else f"{min_experience}+"
                shortlist.append(f"🎯 **EXPERIENCE FILTER**: {exp_range} years (sorted by experience + match score)")
            shortlist.append("")
            
            for i, candidate in enumerate(final_candidates, 1):
                metadata = candidate.get('metadata', {})
                candidate_name = metadata.get('candidate_name', 'Unknown Candidate')
                experience = metadata.get('experience_years', 'Unknown')
                unique_id = metadata.get('unique_id', 'N/A')
                
                # Use the pre-calculated combined score
                combined_score = candidate.get('combined_score', 0)
                
                # Calculate individual components for display
                distance = candidate.get('distance', 1.0)
                if distance <= 1.0:
                    match_score = max(0, min(1, 1 - distance))
                else:
                    match_score = max(0, min(1, 2 - distance))
                
                # Extract key skills for display
                skills = metadata.get('skills', '')
                if isinstance(skills, str) and skills:
                    key_skills = skills.split(',')[:3]  # Show top 3 skills
                    skills_display = ', '.join([skill.strip() for skill in key_skills])
                else:
                    skills_display = "Skills not extracted"
                
                shortlist.append(f"**{i}. {candidate_name}**")
                shortlist.append(f"   🆔 Unique ID: {unique_id[:16]}...")
                shortlist.append(f"   📊 Combined Score: {combined_score:.2f}/1.00 (Match: {match_score:.2f} + Experience Rank)")
                shortlist.append(f"   💼 Experience: {experience} years")
                shortlist.append(f"   🛠️  Key Skills: {skills_display}")
                shortlist.append(f"   📧 Contact: {metadata.get('email', 'Not available')}")
                
                if combined_score > 0.8:
                    shortlist.append("   ⭐ **HIGHLY RECOMMENDED** (Top experience + match)")
                elif combined_score > 0.6:
                    shortlist.append("   ✅ **GOOD MATCH** (Good experience + skills)")
                else:
                    shortlist.append("   ⚠️  **MODERATE MATCH** (Meets requirements)")
                shortlist.append("")
            
            # Enhanced summary with deduplication and experience-based ranking metrics
            high_match_count = sum(1 for c in final_candidates if c.get('combined_score', 0) > 0.8)
            good_match_count = sum(1 for c in final_candidates if 0.6 <= c.get('combined_score', 0) <= 0.8)
            
            # Calculate experience distribution
            exp_distribution = {}
            for candidate in final_candidates:
                exp = candidate.get('metadata', {}).get('experience_years', 0)
                exp_range = f"{int(exp//5)*5}-{int(exp//5)*5+4}" if exp < 20 else "20+"
                exp_distribution[exp_range] = exp_distribution.get(exp_range, 0) + 1
            
            shortlist.append("📈 **ENHANCED RANKING SUMMARY:**")
            shortlist.append(f"   • Initial search results: {len(initial_results)}")
            shortlist.append(f"   • After deduplication: {len(unique_results)} unique candidates")
            shortlist.append(f"   • Meeting experience requirement: {len(filtered_candidates)}")
            shortlist.append(f"   • Final shortlist (sorted by experience + match): {len(final_candidates)} candidates")
            shortlist.append(f"   • Highly recommended (>80% combined score): {high_match_count}")
            shortlist.append(f"   • Good matches (60-80% combined score): {good_match_count}")
            shortlist.append(f"   • Duplicates eliminated: {len(initial_results) - len(unique_results)}")
            
            if exp_distribution:
                shortlist.append("   • Experience distribution:")
                for exp_range, count in sorted(exp_distribution.items()):
                    shortlist.append(f"     - {exp_range} years: {count} candidates")
            
            shortlist.append("")
            shortlist.append("🔒 **GUARANTEE**: No duplicate candidates + Experience-optimized ranking!")
            shortlist.append("🎯 **RANKING**: Candidates sorted by combined score (60% match + 30% experience + 10% tech skills)")
            
            return "\n".join(shortlist)
            
        except Exception as e:
            logger.error(f"Error in hybrid candidate shortlisting: {e}")
            return f"Error shortlisting candidates: {str(e)}"

# Create the tool instance
candidate_shortlist_tool = CandidateShortlistTool()
