"""
Training System for Candidate Matching
Learns from user interactions and field data to improve recommendations
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class CandidateTrainingSystem:
    """System to train and improve candidate matching based on user interactions"""
    
    def __init__(self, training_data_path: str = "./training_data"):
        self.training_data_path = training_data_path
        self.interactions_file = os.path.join(training_data_path, "user_interactions.json")
        self.field_patterns_file = os.path.join(training_data_path, "field_patterns.json")
        self.success_metrics_file = os.path.join(training_data_path, "success_metrics.json")
        
        # Create training data directory if it doesn't exist
        os.makedirs(training_data_path, exist_ok=True)
        
        # Initialize data structures
        self.interactions = self._load_interactions()
        self.field_patterns = self._load_field_patterns()
        self.success_metrics = self._load_success_metrics()
    
    def _load_interactions(self) -> List[Dict]:
        """Load user interaction data"""
        try:
            if os.path.exists(self.interactions_file):
                with open(self.interactions_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading interactions: {e}")
            return []
    
    def _load_field_patterns(self) -> Dict:
        """Load field pattern data"""
        try:
            if os.path.exists(self.field_patterns_file):
                with open(self.field_patterns_file, 'r') as f:
                    return json.load(f)
            return {
                "job_title_skills": defaultdict(list),
                "experience_success": defaultdict(list),
                "location_preferences": defaultdict(int),
                "education_correlations": defaultdict(list)
            }
        except Exception as e:
            logger.error(f"Error loading field patterns: {e}")
            return {}
    
    def _load_success_metrics(self) -> Dict:
        """Load success metrics data"""
        try:
            if os.path.exists(self.success_metrics_file):
                with open(self.success_metrics_file, 'r') as f:
                    return json.load(f)
            return {
                "total_searches": 0,
                "successful_matches": 0,
                "field_effectiveness": {},
                "popular_combinations": []
            }
        except Exception as e:
            logger.error(f"Error loading success metrics: {e}")
            return {}
    
    def record_search_interaction(self, search_data: Dict[str, Any], results: List[Dict], 
                                user_feedback: Optional[str] = None) -> None:
        """Record a user search interaction for training"""
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "search_criteria": {
                "job_title": search_data.get("job_title", ""),
                "required_skills": search_data.get("required_skills", ""),
                "experience_level": search_data.get("experience_level", "Any"),
                "location": search_data.get("location", ""),
                "education": search_data.get("education", "Any"),
                "num_candidates": search_data.get("num_candidates", 5)
            },
            "results_count": len(results),
            "results_summary": [
                {
                    "name": result.get("name", ""),
                    "experience": result.get("experience", ""),
                    "match_score": result.get("match_score", ""),
                    "skills": result.get("skills", "")
                } for result in results[:5]  # Store top 5 results
            ],
            "user_feedback": user_feedback,
            "success_indicators": {
                "found_candidates": len(results) > 0,
                "good_match_count": len([r for r in results if "%" in str(r.get("match_score", "")) and 
                                       int(r.get("match_score", "0%").replace("%", "")) > 70])
            }
        }
        
        self.interactions.append(interaction)
        self._save_interactions()
        
        # Update patterns and metrics
        self._update_field_patterns(interaction)
        self._update_success_metrics(interaction)
        
        logger.info(f"Recorded search interaction: {search_data.get('job_title', 'Unknown')} - {len(results)} results")
    
    def _update_field_patterns(self, interaction: Dict) -> None:
        """Update field patterns based on interaction"""
        
        criteria = interaction["search_criteria"]
        results = interaction["results_summary"]
        success = interaction["success_indicators"]
        
        # Job title to skills correlation
        job_title = criteria["job_title"].lower()
        skills = criteria["required_skills"].lower().split(",") if criteria["required_skills"] else []
        
        if job_title and skills:
            if job_title not in self.field_patterns["job_title_skills"]:
                self.field_patterns["job_title_skills"][job_title] = []
            self.field_patterns["job_title_skills"][job_title].extend([s.strip() for s in skills])
        
        # Experience level success tracking
        exp_level = criteria["experience_level"]
        if exp_level != "Any":
            if exp_level not in self.field_patterns["experience_success"]:
                self.field_patterns["experience_success"][exp_level] = []
            self.field_patterns["experience_success"][exp_level].append({
                "results_count": len(results),
                "good_matches": success["good_match_count"],
                "timestamp": interaction["timestamp"]
            })
        
        # Location preferences
        location = criteria["location"]
        if location:
            self.field_patterns["location_preferences"][location.lower()] += 1
        
        # Education correlations
        education = criteria["education"]
        if education != "Any" and results:
            if education not in self.field_patterns["education_correlations"]:
                self.field_patterns["education_correlations"][education] = []
            self.field_patterns["education_correlations"][education].append({
                "job_title": job_title,
                "success_rate": success["good_match_count"] / max(len(results), 1)
            })
        
        self._save_field_patterns()
    
    def _update_success_metrics(self, interaction: Dict) -> None:
        """Update overall success metrics"""
        
        self.success_metrics["total_searches"] += 1
        
        if interaction["success_indicators"]["found_candidates"]:
            self.success_metrics["successful_matches"] += 1
        
        # Track field effectiveness
        criteria = interaction["search_criteria"]
        for field, value in criteria.items():
            if value and value != "Any":
                if field not in self.success_metrics["field_effectiveness"]:
                    self.success_metrics["field_effectiveness"][field] = {"uses": 0, "successes": 0}
                
                self.success_metrics["field_effectiveness"][field]["uses"] += 1
                if interaction["success_indicators"]["good_match_count"] > 0:
                    self.success_metrics["field_effectiveness"][field]["successes"] += 1
        
        self._save_success_metrics()
    
    def get_skill_recommendations(self, job_title: str) -> List[str]:
        """Get skill recommendations based on training data"""
        
        job_title_lower = job_title.lower()
        
        # Get skills from training data
        recommended_skills = []
        
        if job_title_lower in self.field_patterns["job_title_skills"]:
            skill_counts = Counter(self.field_patterns["job_title_skills"][job_title_lower])
            # Get top 10 most common skills
            recommended_skills = [skill for skill, count in skill_counts.most_common(10)]
        
        # Add default recommendations based on job title patterns
        if "software" in job_title_lower or "developer" in job_title_lower:
            default_skills = ["Python", "JavaScript", "React", "SQL", "Git", "AWS"]
            recommended_skills.extend([s for s in default_skills if s.lower() not in [r.lower() for r in recommended_skills]])
        
        elif "data" in job_title_lower:
            default_skills = ["Python", "SQL", "Pandas", "Machine Learning", "Tableau", "R"]
            recommended_skills.extend([s for s in default_skills if s.lower() not in [r.lower() for r in recommended_skills]])
        
        return recommended_skills[:8]  # Return top 8 recommendations
    
    def get_experience_insights(self, experience_level: str) -> Dict[str, Any]:
        """Get insights about experience level effectiveness"""
        
        if experience_level in self.field_patterns["experience_success"]:
            data = self.field_patterns["experience_success"][experience_level]
            
            if data:
                avg_results = sum(d["results_count"] for d in data) / len(data)
                avg_good_matches = sum(d["good_matches"] for d in data) / len(data)
                success_rate = avg_good_matches / max(avg_results, 1)
                
                return {
                    "average_results": round(avg_results, 1),
                    "average_good_matches": round(avg_good_matches, 1),
                    "success_rate": round(success_rate * 100, 1),
                    "total_searches": len(data),
                    "recommendation": self._get_experience_recommendation(success_rate)
                }
        
        return {
            "average_results": 0,
            "average_good_matches": 0,
            "success_rate": 0,
            "total_searches": 0,
            "recommendation": "No data available yet"
        }
    
    def _get_experience_recommendation(self, success_rate: float) -> str:
        """Get recommendation based on success rate"""
        if success_rate > 0.7:
            return "Excellent filtering - this experience level typically yields great results"
        elif success_rate > 0.5:
            return "Good filtering - this experience level usually finds relevant candidates"
        elif success_rate > 0.3:
            return "Moderate success - consider broadening search criteria"
        else:
            return "Low success rate - try adjusting experience requirements or other filters"
    
    def get_popular_combinations(self) -> List[Dict[str, Any]]:
        """Get popular field combinations that work well"""
        
        # Analyze successful combinations from interactions
        successful_combinations = []
        
        for interaction in self.interactions:
            if interaction["success_indicators"]["good_match_count"] > 0:
                criteria = interaction["search_criteria"]
                combination = {
                    "job_title": criteria["job_title"],
                    "experience_level": criteria["experience_level"],
                    "key_skills": criteria["required_skills"][:50] + "..." if len(criteria["required_skills"]) > 50 else criteria["required_skills"],
                    "success_score": interaction["success_indicators"]["good_match_count"],
                    "results_count": interaction["results_count"]
                }
                successful_combinations.append(combination)
        
        # Sort by success score and return top combinations
        successful_combinations.sort(key=lambda x: x["success_score"], reverse=True)
        return successful_combinations[:5]
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get summary of training data and insights"""
        
        total_searches = self.success_metrics["total_searches"]
        successful_matches = self.success_metrics["successful_matches"]
        success_rate = (successful_matches / max(total_searches, 1)) * 100
        
        # Field effectiveness analysis
        field_effectiveness = {}
        for field, data in self.success_metrics["field_effectiveness"].items():
            if data["uses"] > 0:
                effectiveness = (data["successes"] / data["uses"]) * 100
                field_effectiveness[field] = {
                    "effectiveness_percentage": round(effectiveness, 1),
                    "total_uses": data["uses"],
                    "successful_uses": data["successes"]
                }
        
        return {
            "total_searches": total_searches,
            "successful_matches": successful_matches,
            "overall_success_rate": round(success_rate, 1),
            "field_effectiveness": field_effectiveness,
            "popular_locations": dict(Counter(self.field_patterns["location_preferences"]).most_common(5)),
            "training_data_size": len(self.interactions),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_interactions(self) -> None:
        """Save interactions to file"""
        try:
            with open(self.interactions_file, 'w') as f:
                json.dump(self.interactions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving interactions: {e}")
    
    def _save_field_patterns(self) -> None:
        """Save field patterns to file"""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            patterns_dict = {
                "job_title_skills": dict(self.field_patterns["job_title_skills"]),
                "experience_success": dict(self.field_patterns["experience_success"]),
                "location_preferences": dict(self.field_patterns["location_preferences"]),
                "education_correlations": dict(self.field_patterns["education_correlations"])
            }
            with open(self.field_patterns_file, 'w') as f:
                json.dump(patterns_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving field patterns: {e}")
    
    def _save_success_metrics(self) -> None:
        """Save success metrics to file"""
        try:
            with open(self.success_metrics_file, 'w') as f:
                json.dump(self.success_metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving success metrics: {e}")

# Global training system instance
training_system = CandidateTrainingSystem()
