"""
Enhanced Skills Matching System
Provides intelligent skills-based filtering and scoring for candidates
"""

import re
import logging
from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class SkillsMatcher:
    """Advanced skills matching and filtering system"""
    
    def __init__(self):
        # Skill synonyms and variations
        self.skill_synonyms = {
            'javascript': ['js', 'ecmascript', 'javascript', 'java script'],
            'python': ['python', 'py', 'python3'],
            'react': ['react', 'reactjs', 'react.js'],
            'angular': ['angular', 'angularjs', 'angular.js'],
            'vue': ['vue', 'vuejs', 'vue.js'],
            'node': ['node', 'nodejs', 'node.js'],
            'typescript': ['typescript', 'ts'],
            'css': ['css', 'css3', 'cascading style sheets'],
            'html': ['html', 'html5', 'hypertext markup language'],
            'sql': ['sql', 'mysql', 'postgresql', 'sqlite'],
            'aws': ['aws', 'amazon web services'],
            'docker': ['docker', 'containerization'],
            'kubernetes': ['kubernetes', 'k8s'],
            'git': ['git', 'github', 'gitlab', 'version control'],
            'java': ['java', 'openjdk'],
            'c++': ['c++', 'cpp', 'c plus plus'],
            'c#': ['c#', 'csharp', 'c sharp'],
            'php': ['php', 'php7', 'php8'],
            'ruby': ['ruby', 'ruby on rails', 'rails'],
            'go': ['go', 'golang'],
            'rust': ['rust', 'rust-lang'],
            'swift': ['swift', 'ios'],
            'kotlin': ['kotlin', 'android'],
            'scala': ['scala'],
            'r': ['r', 'r-lang', 'r programming'],
            'matlab': ['matlab'],
            'tensorflow': ['tensorflow', 'tf'],
            'pytorch': ['pytorch', 'torch'],
            'pandas': ['pandas', 'pd'],
            'numpy': ['numpy', 'np'],
            'scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
            'mongodb': ['mongodb', 'mongo'],
            'redis': ['redis'],
            'elasticsearch': ['elasticsearch', 'elastic search'],
            'jenkins': ['jenkins', 'ci/cd'],
            'terraform': ['terraform', 'infrastructure as code'],
            'ansible': ['ansible', 'automation'],
            'linux': ['linux', 'unix'],
            'windows': ['windows', 'microsoft windows'],
            'macos': ['macos', 'mac os', 'osx']
        }
        
        # Skill categories for better matching
        self.skill_categories = {
            'frontend': ['react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css', 'sass', 'less'],
            'backend': ['python', 'java', 'node', 'php', 'ruby', 'go', 'c#', 'scala'],
            'database': ['sql', 'mongodb', 'redis', 'postgresql', 'mysql', 'elasticsearch'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'mobile': ['swift', 'kotlin', 'react native', 'flutter'],
            'data_science': ['python', 'r', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn'],
            'devops': ['docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'git']
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize a skill name to its canonical form"""
        skill_lower = skill.lower().strip()
        
        # Remove common prefixes/suffixes
        skill_lower = re.sub(r'\b(programming|language|framework|library|tool)\b', '', skill_lower).strip()
        
        # Find canonical form from synonyms
        for canonical, synonyms in self.skill_synonyms.items():
            if skill_lower in synonyms:
                return canonical
        
        return skill_lower
    
    def extract_skills_from_text(self, text: str) -> Set[str]:
        """Extract skills from candidate text/resume content"""
        if not text:
            return set()
        
        text_lower = text.lower()
        found_skills = set()
        
        # Check for each skill and its synonyms
        for canonical_skill, synonyms in self.skill_synonyms.items():
            for synonym in synonyms:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(synonym) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.add(canonical_skill)
                    break
        
        return found_skills
    
    def calculate_skills_match_score(self, required_skills: List[str], candidate_skills: Set[str], 
                                   candidate_content: str = "") -> Dict[str, float]:
        """Calculate detailed skills matching score"""
        
        if not required_skills:
            return {"match_score": 1.0, "matched_skills": [], "missing_skills": [], "bonus_skills": []}
        
        # Normalize required skills
        normalized_required = [self.normalize_skill(skill) for skill in required_skills]
        
        # Get candidate skills from metadata and content
        all_candidate_skills = candidate_skills.copy()
        if candidate_content:
            content_skills = self.extract_skills_from_text(candidate_content)
            all_candidate_skills.update(content_skills)
        
        # Find matches
        matched_skills = []
        missing_skills = []
        
        for required_skill in normalized_required:
            if required_skill in all_candidate_skills:
                matched_skills.append(required_skill)
            else:
                # Check for partial matches or related skills
                partial_match = self._find_partial_match(required_skill, all_candidate_skills)
                if partial_match:
                    matched_skills.append(f"{required_skill} (similar: {partial_match})")
                else:
                    missing_skills.append(required_skill)
        
        # Find bonus skills (candidate has skills not required but relevant)
        bonus_skills = []
        for candidate_skill in all_candidate_skills:
            if candidate_skill not in normalized_required:
                # Check if it's in the same category as required skills
                if self._is_related_skill(candidate_skill, normalized_required):
                    bonus_skills.append(candidate_skill)
        
        # Calculate match score
        if len(normalized_required) == 0:
            match_score = 1.0
        else:
            exact_matches = len([s for s in matched_skills if "similar:" not in s])
            partial_matches = len([s for s in matched_skills if "similar:" in s])
            
            # Exact matches worth full points, partial matches worth half
            score = (exact_matches + partial_matches * 0.5) / len(normalized_required)
            
            # Bonus for having additional relevant skills
            bonus = min(0.2, len(bonus_skills) * 0.05)  # Max 20% bonus
            
            match_score = min(1.0, score + bonus)
        
        return {
            "match_score": match_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "bonus_skills": bonus_skills[:5],  # Limit to top 5 bonus skills
            "total_required": len(normalized_required),
            "exact_matches": len([s for s in matched_skills if "similar:" not in s]),
            "partial_matches": len([s for s in matched_skills if "similar:" in s])
        }
    
    def _find_partial_match(self, required_skill: str, candidate_skills: Set[str]) -> str:
        """Find partial/similar skill matches"""
        best_match = ""
        best_score = 0.6  # Minimum similarity threshold
        
        for candidate_skill in candidate_skills:
            # Check string similarity
            similarity = SequenceMatcher(None, required_skill, candidate_skill).ratio()
            if similarity > best_score:
                best_match = candidate_skill
                best_score = similarity
            
            # Check if they're in the same category
            if self._skills_in_same_category(required_skill, candidate_skill):
                if similarity > 0.3:  # Lower threshold for same category
                    best_match = candidate_skill
                    best_score = similarity
        
        return best_match
    
    def _is_related_skill(self, skill: str, required_skills: List[str]) -> bool:
        """Check if a skill is related to the required skills"""
        for required_skill in required_skills:
            if self._skills_in_same_category(skill, required_skill):
                return True
        return False
    
    def _skills_in_same_category(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are in the same category"""
        for category, skills in self.skill_categories.items():
            if skill1 in skills and skill2 in skills:
                return True
        return False
    
    def filter_candidates_by_skills(self, candidates: List[Dict], required_skills: List[str], 
                                  min_match_threshold: float = 0.3) -> List[Dict]:
        """Filter candidates based on skills matching threshold"""
        
        if not required_skills:
            return candidates
        
        filtered_candidates = []
        
        for candidate in candidates:
            metadata = candidate.get('metadata', {})
            content = candidate.get('content', '')
            
            # Extract candidate skills
            candidate_skills_text = metadata.get('skills', '')
            candidate_skills = set()
            
            if candidate_skills_text:
                # Parse skills from metadata
                skills_list = [s.strip() for s in candidate_skills_text.split(',') if s.strip()]
                candidate_skills = {self.normalize_skill(skill) for skill in skills_list}
            
            # Calculate skills match
            skills_analysis = self.calculate_skills_match_score(
                required_skills, candidate_skills, content
            )
            
            # Add skills analysis to candidate data
            candidate['skills_analysis'] = skills_analysis
            
            # Filter based on threshold
            if skills_analysis['match_score'] >= min_match_threshold:
                filtered_candidates.append(candidate)
        
        # Sort by skills match score (descending)
        filtered_candidates.sort(key=lambda x: x['skills_analysis']['match_score'], reverse=True)
        
        return filtered_candidates
    
    def get_skills_recommendations(self, job_title: str) -> List[str]:
        """Get skill recommendations based on job title"""
        
        job_title_lower = job_title.lower()
        recommendations = []
        
        # Job title based recommendations
        if any(word in job_title_lower for word in ['frontend', 'front-end', 'ui', 'ux']):
            recommendations.extend(['javascript', 'react', 'html', 'css', 'typescript'])
        
        elif any(word in job_title_lower for word in ['backend', 'back-end', 'api', 'server']):
            recommendations.extend(['python', 'java', 'node', 'sql', 'aws'])
        
        elif any(word in job_title_lower for word in ['fullstack', 'full-stack', 'full stack']):
            recommendations.extend(['javascript', 'python', 'react', 'node', 'sql'])
        
        elif any(word in job_title_lower for word in ['data', 'analytics', 'scientist', 'analyst']):
            recommendations.extend(['python', 'sql', 'pandas', 'numpy', 'tensorflow'])
        
        elif any(word in job_title_lower for word in ['devops', 'sre', 'infrastructure']):
            recommendations.extend(['docker', 'kubernetes', 'aws', 'terraform', 'jenkins'])
        
        elif any(word in job_title_lower for word in ['mobile', 'ios', 'android']):
            recommendations.extend(['swift', 'kotlin', 'react native', 'flutter'])
        
        else:
            # Generic software development skills
            recommendations.extend(['python', 'javascript', 'sql', 'git', 'aws'])
        
        return recommendations[:8]  # Return top 8 recommendations

# Global skills matcher instance
skills_matcher = SkillsMatcher()
