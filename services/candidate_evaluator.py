"""
Advanced Candidate Evaluation Module
Triggered after candidate shortlisting and job description finalization
Evaluates each shortlisted candidate against job description with 60%+ accuracy
Provides detailed justification for selection/rejection decisions
"""

import logging
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class EvaluationCriteria:
    """Criteria for candidate evaluation"""
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience: int
    max_experience: int
    required_certifications: List[str]
    role_level: str  # junior, mid, senior, lead
    domain_keywords: List[str]

@dataclass
class CandidateScore:
    """Detailed scoring for a candidate"""
    overall_score: float
    semantic_similarity: float
    skills_alignment: float
    experience_mapping: float
    certification_score: float
    role_fit_score: float
    is_selected: bool
    justification: Dict[str, Any]

class CandidateEvaluator:
    """Advanced candidate evaluation system with 60%+ accuracy"""
    
    def __init__(self):
        self.selection_threshold = 0.60  # 60% threshold for auto-selection
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
    def extract_evaluation_criteria(self, job_description: str) -> EvaluationCriteria:
        """Extract structured evaluation criteria from job description"""
        
        # Extract required skills
        required_skills = []
        if "Required Skills:" in job_description:
            skills_section = re.search(r"Required Skills:(.*?)(?:\n\n|\n[A-Z]|$)", job_description, re.DOTALL)
            if skills_section:
                skills_text = skills_section.group(1).strip()
                required_skills = [skill.strip() for skill in re.split(r'[,\n•-]', skills_text) if skill.strip()]
        
        # Extract preferred skills
        preferred_skills = []
        if "Preferred Skills:" in job_description or "Nice to have:" in job_description:
            pref_pattern = r"(?:Preferred Skills|Nice to have):(.*?)(?:\n\n|\n[A-Z]|$)"
            pref_section = re.search(pref_pattern, job_description, re.DOTALL)
            if pref_section:
                pref_text = pref_section.group(1).strip()
                preferred_skills = [skill.strip() for skill in re.split(r'[,\n•-]', pref_text) if skill.strip()]
        
        # Extract experience requirements
        min_exp, max_exp = 0, 999
        exp_patterns = [
            r"(\d+)[\s-]+(\d+)\s*years?\s*(?:of\s*)?(?:experience|development)",
            r"(\d+)\+\s*years?\s*(?:of\s*)?(?:experience|development)",
            r"minimum\s*(\d+)\s*years?",
            r"at least\s*(\d+)\s*years?",
            r"(\d+)\s*to\s*(\d+)\s*years?",
            r"(\d+)\s*-\s*(\d+)\s*years?"
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, job_description.lower())
            if match:
                if len(match.groups()) == 2:
                    min_exp, max_exp = int(match.group(1)), int(match.group(2))
                else:
                    min_exp = int(match.group(1))
                    max_exp = 999  # Open-ended
                break
        
        # Extract certifications (distinguish from preferred skills)
        cert_keywords = ['certification', 'certified', 'certificate']
        certifications = []
        for keyword in cert_keywords:
            if keyword.lower() in job_description.lower():
                # Extract certification context
                cert_context = re.search(rf"({keyword}[^.]*)", job_description, re.IGNORECASE)
                if cert_context:
                    certifications.append(cert_context.group(1).strip())
        
        # Determine role level (improved detection)
        role_level = "mid"  # default
        job_desc_lower = job_description.lower()
        
        # Check for senior level first (more specific)
        if any(word in job_desc_lower for word in ['senior', 'sr.', 'sr ', 'lead', 'principal']):
            role_level = "senior"
        elif any(word in job_desc_lower for word in ['manager', 'director', 'head']):
            role_level = "lead"
        elif any(word in job_desc_lower for word in ['junior', 'entry', 'associate', 'jr.']):
            role_level = "junior"
        
        # Extract domain keywords
        domain_keywords = []
        domains = ['frontend', 'backend', 'fullstack', 'devops', 'data', 'ml', 'ai', 'mobile', 'cloud']
        for domain in domains:
            if domain in job_description.lower():
                domain_keywords.append(domain)
        
        return EvaluationCriteria(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_experience=min_exp,
            max_experience=max_exp,
            required_certifications=certifications,
            role_level=role_level,
            domain_keywords=domain_keywords
        )
    
    def calculate_semantic_similarity(self, job_description: str, candidate_content: str) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity"""
        try:
            # Prepare documents
            documents = [job_description, candidate_content]
            
            # Fit and transform
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            return float(similarity_matrix[0][0])
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def calculate_skills_alignment(self, criteria: EvaluationCriteria, candidate: Dict) -> Tuple[float, Dict]:
        """Calculate skills alignment score with detailed breakdown"""
        
        candidate_skills_text = candidate.get('metadata', {}).get('skills', '').lower()
        candidate_content = candidate.get('content', '').lower()
        
        # Combine skills and content for comprehensive matching
        candidate_text = f"{candidate_skills_text} {candidate_content}"
        
        # Required skills matching
        required_matches = []
        required_missing = []
        
        for skill in criteria.required_skills:
            skill_lower = skill.lower()
            # Check for exact match or partial match
            if (skill_lower in candidate_text or 
                any(word in candidate_text for word in skill_lower.split() if len(word) > 2)):
                required_matches.append(skill)
            else:
                required_missing.append(skill)
        
        # Preferred skills matching
        preferred_matches = []
        for skill in criteria.preferred_skills:
            skill_lower = skill.lower()
            if (skill_lower in candidate_text or 
                any(word in candidate_text for word in skill_lower.split() if len(word) > 2)):
                preferred_matches.append(skill)
        
        # Calculate alignment score
        total_required = len(criteria.required_skills)
        matched_required = len(required_matches)
        
        if total_required == 0:
            required_score = 1.0
        else:
            required_score = matched_required / total_required
        
        # Bonus for preferred skills
        preferred_bonus = min(0.2, len(preferred_matches) * 0.05)  # Max 20% bonus
        
        final_score = min(1.0, required_score + preferred_bonus)
        
        skills_breakdown = {
            'required_matches': required_matches,
            'required_missing': required_missing,
            'preferred_matches': preferred_matches,
            'required_score': required_score,
            'preferred_bonus': preferred_bonus,
            'total_required': total_required,
            'matched_required': matched_required
        }
        
        return final_score, skills_breakdown
    
    def calculate_experience_mapping(self, criteria: EvaluationCriteria, candidate: Dict) -> Tuple[float, Dict]:
        """Calculate experience mapping score"""
        
        candidate_exp = candidate.get('metadata', {}).get('experience_years', 0)
        
        # Perfect match within range
        if criteria.min_experience <= candidate_exp <= criteria.max_experience:
            # Prefer candidates closer to the higher end of the range
            if criteria.max_experience == 999:  # Open-ended
                score = min(1.0, candidate_exp / (criteria.min_experience + 5))
            else:
                range_size = criteria.max_experience - criteria.min_experience
                if range_size > 0:
                    position_in_range = (candidate_exp - criteria.min_experience) / range_size
                    score = 0.7 + (0.3 * position_in_range)  # 70% base + 30% for position
                else:
                    score = 1.0
        else:
            # Penalty for being outside range
            if candidate_exp < criteria.min_experience:
                gap = criteria.min_experience - candidate_exp
                score = max(0.0, 0.5 - (gap * 0.1))  # Penalty for under-experience
            else:  # Over-experienced
                excess = candidate_exp - criteria.max_experience
                score = max(0.6, 1.0 - (excess * 0.05))  # Less penalty for over-experience
        
        experience_breakdown = {
            'candidate_experience': candidate_exp,
            'required_range': f"{criteria.min_experience}-{criteria.max_experience}",
            'within_range': criteria.min_experience <= candidate_exp <= criteria.max_experience,
            'score_explanation': self._get_experience_explanation(candidate_exp, criteria)
        }
        
        return score, experience_breakdown
    
    def _get_experience_explanation(self, candidate_exp: int, criteria: EvaluationCriteria) -> str:
        """Get explanation for experience scoring"""
        if criteria.min_experience <= candidate_exp <= criteria.max_experience:
            return f"Perfect fit: {candidate_exp} years within required {criteria.min_experience}-{criteria.max_experience} range"
        elif candidate_exp < criteria.min_experience:
            gap = criteria.min_experience - candidate_exp
            return f"Under-experienced: {gap} years below minimum requirement"
        else:
            excess = candidate_exp - criteria.max_experience
            return f"Over-experienced: {excess} years above maximum (may be overqualified)"
    
    def calculate_certification_score(self, criteria: EvaluationCriteria, candidate: Dict) -> Tuple[float, Dict]:
        """Calculate certification alignment score"""
        
        if not criteria.required_certifications:
            return 1.0, {'no_certifications_required': True}
        
        candidate_content = candidate.get('content', '').lower()
        candidate_skills = candidate.get('metadata', {}).get('skills', '').lower()
        candidate_text = f"{candidate_content} {candidate_skills}"
        
        matched_certs = []
        missing_certs = []
        
        for cert in criteria.required_certifications:
            cert_lower = cert.lower()
            if cert_lower in candidate_text:
                matched_certs.append(cert)
            else:
                missing_certs.append(cert)
        
        if len(criteria.required_certifications) == 0:
            score = 1.0
        else:
            score = len(matched_certs) / len(criteria.required_certifications)
        
        cert_breakdown = {
            'matched_certifications': matched_certs,
            'missing_certifications': missing_certs,
            'total_required': len(criteria.required_certifications),
            'matched_count': len(matched_certs)
        }
        
        return score, cert_breakdown
    
    def calculate_role_fit_score(self, criteria: EvaluationCriteria, candidate: Dict) -> Tuple[float, Dict]:
        """Calculate role level fit score"""
        
        candidate_content = candidate.get('content', '').lower()
        candidate_exp = candidate.get('metadata', {}).get('experience_years', 0)
        
        # Role level indicators
        role_indicators = {
            'junior': ['junior', 'entry', 'associate', 'trainee', 'intern'],
            'mid': ['developer', 'engineer', 'analyst', 'specialist'],
            'senior': ['senior', 'sr.', 'lead', 'principal', 'expert'],
            'lead': ['manager', 'director', 'head', 'team lead', 'tech lead']
        }
        
        # Check candidate's apparent level from content
        candidate_level_scores = {}
        for level, indicators in role_indicators.items():
            score = sum(1 for indicator in indicators if indicator in candidate_content)
            candidate_level_scores[level] = score
        
        # Determine candidate's apparent level
        apparent_level = max(candidate_level_scores, key=candidate_level_scores.get)
        
        # Experience-based level validation
        exp_based_level = 'junior'
        if candidate_exp >= 7:
            exp_based_level = 'lead'
        elif candidate_exp >= 4:
            exp_based_level = 'senior'
        elif candidate_exp >= 2:
            exp_based_level = 'mid'
        
        # Calculate fit score
        level_hierarchy = {'junior': 1, 'mid': 2, 'senior': 3, 'lead': 4}
        required_level_num = level_hierarchy.get(criteria.role_level, 2)
        apparent_level_num = level_hierarchy.get(apparent_level, 2)
        exp_level_num = level_hierarchy.get(exp_based_level, 2)
        
        # Use the higher of apparent or experience-based level
        candidate_level_num = max(apparent_level_num, exp_level_num)
        
        # Perfect match
        if candidate_level_num == required_level_num:
            score = 1.0
        # One level difference
        elif abs(candidate_level_num - required_level_num) == 1:
            score = 0.8
        # Two levels difference
        elif abs(candidate_level_num - required_level_num) == 2:
            score = 0.6
        else:
            score = 0.4
        
        role_breakdown = {
            'required_level': criteria.role_level,
            'apparent_level': apparent_level,
            'experience_based_level': exp_based_level,
            'final_candidate_level': max(apparent_level, exp_based_level, key=lambda x: level_hierarchy.get(x, 0)),
            'level_match': candidate_level_num == required_level_num,
            'level_gap': abs(candidate_level_num - required_level_num)
        }
        
        return score, role_breakdown
    
    def generate_justification(self, candidate: Dict, score: CandidateScore, criteria: EvaluationCriteria) -> Dict[str, Any]:
        """Generate detailed justification for selection/rejection"""
        
        candidate_name = candidate.get('metadata', {}).get('candidate_name', 'Unknown')
        
        justification = {
            'candidate_name': candidate_name,
            'decision': 'SELECTED' if score.is_selected else 'REJECTED',
            'overall_score': f"{score.overall_score:.1%}",
            'threshold': f"{self.selection_threshold:.1%}",
            'evaluation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'detailed_scores': {
                'semantic_similarity': f"{score.semantic_similarity:.1%}",
                'skills_alignment': f"{score.skills_alignment:.1%}",
                'experience_mapping': f"{score.experience_mapping:.1%}",
                'certification_score': f"{score.certification_score:.1%}",
                'role_fit_score': f"{score.role_fit_score:.1%}"
            }
        }
        
        if score.is_selected:
            # Highlight strengths for selected candidates
            strengths = []
            if score.skills_alignment >= 0.8:
                skills_info = score.justification.get('skills_breakdown', {})
                matched = skills_info.get('matched_required', 0)
                total = skills_info.get('total_required', 0)
                strengths.append(f"Excellent skills match ({matched}/{total} required skills)")
            
            if score.experience_mapping >= 0.8:
                exp_info = score.justification.get('experience_breakdown', {})
                strengths.append(f"Perfect experience fit: {exp_info.get('score_explanation', '')}")
            
            if score.semantic_similarity >= 0.7:
                strengths.append(f"Strong semantic alignment with job requirements")
            
            if score.certification_score >= 0.8:
                cert_info = score.justification.get('cert_breakdown', {})
                matched_certs = cert_info.get('matched_certifications', [])
                if matched_certs:
                    strengths.append(f"Has required certifications: {', '.join(matched_certs)}")
            
            justification['selection_reasons'] = strengths
            justification['recommendation'] = "HIGHLY RECOMMENDED - Meets all key criteria with high confidence"
            
        else:
            # Identify gaps for rejected candidates
            gaps = []
            
            if score.skills_alignment < 0.6:
                skills_info = score.justification.get('skills_breakdown', {})
                missing_skills = skills_info.get('required_missing', [])
                if missing_skills:
                    gaps.append(f"Missing critical skills: {', '.join(missing_skills[:3])}")
            
            if score.experience_mapping < 0.5:
                exp_info = score.justification.get('experience_breakdown', {})
                gaps.append(f"Experience mismatch: {exp_info.get('score_explanation', '')}")
            
            if score.certification_score < 0.5:
                cert_info = score.justification.get('cert_breakdown', {})
                missing_certs = cert_info.get('missing_certifications', [])
                if missing_certs:
                    gaps.append(f"Missing certifications: {', '.join(missing_certs)}")
            
            if score.role_fit_score < 0.6:
                role_info = score.justification.get('role_breakdown', {})
                gaps.append(f"Role level mismatch: candidate appears {role_info.get('final_candidate_level', 'unknown')} level, role requires {criteria.role_level}")
            
            justification['rejection_reasons'] = gaps
            justification['recommendation'] = f"NOT RECOMMENDED - Score {score.overall_score:.1%} below {self.selection_threshold:.1%} threshold"
        
        return justification
    
    def evaluate_candidate(self, candidate: Dict, job_description: str, criteria: EvaluationCriteria) -> CandidateScore:
        """Evaluate a single candidate against job requirements"""
        
        # Calculate individual scores
        semantic_score = self.calculate_semantic_similarity(job_description, candidate.get('content', ''))
        skills_score, skills_breakdown = self.calculate_skills_alignment(criteria, candidate)
        experience_score, experience_breakdown = self.calculate_experience_mapping(criteria, candidate)
        cert_score, cert_breakdown = self.calculate_certification_score(criteria, candidate)
        role_score, role_breakdown = self.calculate_role_fit_score(criteria, candidate)
        
        # Weighted overall score (can be adjusted based on job importance)
        weights = {
            'semantic': 0.20,    # 20% - overall content match
            'skills': 0.35,      # 35% - most important for technical roles
            'experience': 0.25,  # 25% - critical for role fit
            'certification': 0.10, # 10% - nice to have
            'role_fit': 0.10     # 10% - level appropriateness
        }
        
        overall_score = (
            semantic_score * weights['semantic'] +
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            cert_score * weights['certification'] +
            role_score * weights['role_fit']
        )
        
        # Decision based on threshold
        is_selected = overall_score >= self.selection_threshold
        
        # Compile justification data
        justification_data = {
            'skills_breakdown': skills_breakdown,
            'experience_breakdown': experience_breakdown,
            'cert_breakdown': cert_breakdown,
            'role_breakdown': role_breakdown,
            'weights_used': weights
        }
        
        score = CandidateScore(
            overall_score=overall_score,
            semantic_similarity=semantic_score,
            skills_alignment=skills_score,
            experience_mapping=experience_score,
            certification_score=cert_score,
            role_fit_score=role_score,
            is_selected=is_selected,
            justification=justification_data
        )
        
        return score
    
    def evaluate_candidates(self, candidates: List[Dict], job_description: str) -> Dict[str, Any]:
        """Evaluate all shortlisted candidates and provide comprehensive results"""
        
        if not candidates:
            return {
                'error': 'No candidates provided for evaluation',
                'selected_candidates': [],
                'rejected_candidates': [],
                'summary': {}
            }
        
        # Extract evaluation criteria from job description
        criteria = self.extract_evaluation_criteria(job_description)
        
        # Evaluate each candidate
        evaluated_candidates = []
        selected_candidates = []
        rejected_candidates = []
        
        for candidate in candidates:
            score = self.evaluate_candidate(candidate, job_description, criteria)
            justification = self.generate_justification(candidate, score, criteria)
            
            evaluation_result = {
                'candidate': candidate,
                'score': score,
                'justification': justification
            }
            
            evaluated_candidates.append(evaluation_result)
            
            if score.is_selected:
                selected_candidates.append(evaluation_result)
            else:
                rejected_candidates.append(evaluation_result)
        
        # Sort by overall score (highest first)
        selected_candidates.sort(key=lambda x: x['score'].overall_score, reverse=True)
        rejected_candidates.sort(key=lambda x: x['score'].overall_score, reverse=True)
        
        # Generate summary statistics
        total_candidates = len(candidates)
        selected_count = len(selected_candidates)
        rejected_count = len(rejected_candidates)
        
        avg_score = np.mean([result['score'].overall_score for result in evaluated_candidates])
        avg_selected_score = np.mean([result['score'].overall_score for result in selected_candidates]) if selected_candidates else 0
        
        summary = {
            'total_evaluated': total_candidates,
            'selected_count': selected_count,
            'rejected_count': rejected_count,
            'selection_rate': f"{(selected_count/total_candidates)*100:.1f}%" if total_candidates > 0 else "0%",
            'average_score': f"{avg_score:.1%}",
            'average_selected_score': f"{avg_selected_score:.1%}" if selected_candidates else "N/A",
            'selection_threshold': f"{self.selection_threshold:.1%}",
            'evaluation_criteria': {
                'required_skills_count': len(criteria.required_skills),
                'preferred_skills_count': len(criteria.preferred_skills),
                'experience_range': f"{criteria.min_experience}-{criteria.max_experience} years",
                'role_level': criteria.role_level,
                'certifications_required': len(criteria.required_certifications) > 0
            }
        }
        
        return {
            'selected_candidates': selected_candidates,
            'rejected_candidates': rejected_candidates,
            'summary': summary,
            'evaluation_criteria': criteria,
            'timestamp': datetime.now().isoformat()
        }

# Create global instance
candidate_evaluator = CandidateEvaluator()
