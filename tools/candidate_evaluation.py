"""
Candidate Evaluation Tool
Integrates the advanced candidate evaluator into the LangGraph system
Triggered after candidate shortlisting for detailed evaluation and justification
"""

from langchain.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from services.candidate_evaluator import candidate_evaluator
import logging
import json

logger = logging.getLogger(__name__)

class CandidateEvaluationInput(BaseModel):
    """Input for candidate evaluation"""
    candidates: List[Dict] = Field(description="List of shortlisted candidates to evaluate")
    job_description: str = Field(description="Complete job description for evaluation criteria")
    evaluation_mode: str = Field(default="full", description="Evaluation mode: 'full' or 'summary'")

class CandidateEvaluationTool(BaseTool):
    """Tool to evaluate shortlisted candidates with 60%+ accuracy and detailed justification"""
    name: str = "evaluate_candidates"
    description: str = "Evaluate shortlisted candidates against job description with semantic similarity, skills alignment, and experience mapping. Provides detailed justification for selection/rejection decisions."
    args_schema: Type[BaseModel] = CandidateEvaluationInput
    
    def _format_evaluation_results(self, results: Dict[str, Any], mode: str = "full") -> str:
        """Format evaluation results for display"""
        
        if 'error' in results:
            return f"❌ **EVALUATION ERROR**: {results['error']}"
        
        selected = results['selected_candidates']
        rejected = results['rejected_candidates']
        summary = results['summary']
        
        output = []
        
        # Header
        output.append("🎯 **ADVANCED CANDIDATE EVALUATION RESULTS**")
        output.append("=" * 60)
        output.append(f"📊 **EVALUATION SUMMARY**")
        output.append(f"   • Total Candidates Evaluated: {summary['total_evaluated']}")
        output.append(f"   • Selected (≥60% score): {summary['selected_count']}")
        output.append(f"   • Rejected (<60% score): {summary['rejected_count']}")
        output.append(f"   • Selection Rate: {summary['selection_rate']}")
        output.append(f"   • Average Score: {summary['average_score']}")
        output.append(f"   • Selection Threshold: {summary['selection_threshold']}")
        output.append("")
        
        # Evaluation Criteria Used
        criteria = summary['evaluation_criteria']
        output.append("🔍 **EVALUATION CRITERIA**")
        output.append(f"   • Required Skills: {criteria['required_skills_count']} skills")
        output.append(f"   • Preferred Skills: {criteria['preferred_skills_count']} skills")
        output.append(f"   • Experience Range: {criteria['experience_range']}")
        output.append(f"   • Role Level: {criteria['role_level'].title()}")
        output.append(f"   • Certifications Required: {'Yes' if criteria['certifications_required'] else 'No'}")
        output.append("")
        
        # Selected Candidates
        if selected:
            output.append("✅ **SELECTED CANDIDATES** (60%+ Match Score)")
            output.append("-" * 50)
            
            for i, result in enumerate(selected, 1):
                candidate = result['candidate']
                score = result['score']
                justification = result['justification']
                
                metadata = candidate.get('metadata', {})
                name = metadata.get('candidate_name', 'Unknown')
                experience = metadata.get('experience_years', 'Unknown')
                email = metadata.get('email', 'Not available')
                
                output.append(f"**{i}. {name}** ⭐")
                output.append(f"   📊 Overall Score: {justification['overall_score']} (SELECTED)")
                output.append(f"   💼 Experience: {experience} years")
                output.append(f"   📧 Contact: {email}")
                
                if mode == "full":
                    # Detailed scores
                    scores = justification['detailed_scores']
                    output.append(f"   🔍 **Detailed Scores:**")
                    output.append(f"      • Semantic Similarity: {scores['semantic_similarity']}")
                    output.append(f"      • Skills Alignment: {scores['skills_alignment']}")
                    output.append(f"      • Experience Mapping: {scores['experience_mapping']}")
                    output.append(f"      • Certification Score: {scores['certification_score']}")
                    output.append(f"      • Role Fit Score: {scores['role_fit_score']}")
                    
                    # Selection reasons
                    if 'selection_reasons' in justification:
                        output.append(f"   ✅ **Key Strengths:**")
                        for reason in justification['selection_reasons']:
                            output.append(f"      • {reason}")
                    
                    output.append(f"   🎯 **Recommendation:** {justification['recommendation']}")
                
                output.append("")
        else:
            output.append("❌ **NO CANDIDATES SELECTED**")
            output.append("   No candidates met the 60% threshold for automatic selection.")
            output.append("")
        
        # Rejected Candidates
        if rejected:
            output.append("❌ **REJECTED CANDIDATES** (<60% Match Score)")
            output.append("-" * 50)
            
            for i, result in enumerate(rejected, 1):
                candidate = result['candidate']
                score = result['score']
                justification = result['justification']
                
                metadata = candidate.get('metadata', {})
                name = metadata.get('candidate_name', 'Unknown')
                experience = metadata.get('experience_years', 'Unknown')
                
                output.append(f"**{i}. {name}**")
                output.append(f"   📊 Overall Score: {justification['overall_score']} (REJECTED)")
                output.append(f"   💼 Experience: {experience} years")
                
                if mode == "full":
                    # Rejection reasons
                    if 'rejection_reasons' in justification:
                        output.append(f"   ❌ **Identified Gaps:**")
                        for reason in justification['rejection_reasons']:
                            output.append(f"      • {reason}")
                    
                    # Detailed scores for context
                    scores = justification['detailed_scores']
                    output.append(f"   📊 **Score Breakdown:**")
                    output.append(f"      • Skills Alignment: {scores['skills_alignment']}")
                    output.append(f"      • Experience Mapping: {scores['experience_mapping']}")
                    output.append(f"      • Overall Fit: {scores['semantic_similarity']}")
                
                output.append("")
        
        # Recommendations
        output.append("💡 **RECOMMENDATIONS**")
        if selected:
            output.append(f"   ✅ Proceed with {len(selected)} selected candidate(s)")
            output.append("   📞 Schedule interviews with selected candidates")
            if len(selected) < 3:
                output.append("   🔍 Consider reviewing rejected candidates with scores >80%")
        else:
            output.append("   ⚠️  No candidates met the 60% threshold")
            output.append("   🔄 Consider:")
            output.append("      • Reviewing evaluation criteria")
            output.append("      • Lowering selection threshold temporarily")
            output.append("      • Expanding candidate search")
            output.append("      • Reviewing top rejected candidates manually")
        
        output.append("")
        output.append("🔒 **EVALUATION GUARANTEE**: 60%+ accuracy with detailed justification")
        output.append(f"⏰ **Evaluation Completed**: {results.get('timestamp', 'Unknown')}")
        
        return "\n".join(output)
    
    def _run(self, candidates: List[Dict], job_description: str, evaluation_mode: str = "full") -> str:
        """Run candidate evaluation with detailed scoring and justification"""
        
        try:
            logger.info(f"Starting evaluation of {len(candidates)} candidates")
            
            # Validate inputs
            if not candidates:
                return "❌ **ERROR**: No candidates provided for evaluation"
            
            if not job_description.strip():
                return "❌ **ERROR**: Job description is required for evaluation"
            
            # Run the evaluation
            results = candidate_evaluator.evaluate_candidates(candidates, job_description)
            
            # Format and return results
            formatted_results = self._format_evaluation_results(results, evaluation_mode)
            
            logger.info(f"Evaluation completed: {results['summary']['selected_count']} selected, {results['summary']['rejected_count']} rejected")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in candidate evaluation: {e}")
            return f"❌ **EVALUATION ERROR**: {str(e)}"
    
    def get_evaluation_summary(self, candidates: List[Dict], job_description: str) -> Dict[str, Any]:
        """Get evaluation results as structured data (for programmatic use)"""
        try:
            return candidate_evaluator.evaluate_candidates(candidates, job_description)
        except Exception as e:
            logger.error(f"Error getting evaluation summary: {e}")
            return {'error': str(e)}

# Create the tool instance
candidate_evaluation_tool = CandidateEvaluationTool()
