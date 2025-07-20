#!/usr/bin/env python3
"""
Test script to verify experience-based sorting functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.candidate_shortlist import CandidateShortlistTool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_experience_sorting():
    """Test the experience-based sorting functionality"""
    
    print("🧪 Testing Experience-Based Sorting")
    print("=" * 50)
    
    # Initialize the shortlist tool
    shortlist_tool = CandidateShortlistTool()
    
    # Test cases
    test_cases = [
        {
            "name": "Entry Level (0-2 years)",
            "job_requirements": "Frontend developer with React experience",
            "min_experience": 0,
            "max_experience": 2,
            "n_candidates": 5
        },
        {
            "name": "Mid Level (3-5 years)",
            "job_requirements": "Frontend developer with React experience",
            "min_experience": 3,
            "max_experience": 5,
            "n_candidates": 5
        },
        {
            "name": "Senior Level (6-10 years)",
            "job_requirements": "Frontend developer with React experience",
            "min_experience": 6,
            "max_experience": 10,
            "n_candidates": 5
        },
        {
            "name": "Expert Level (10+ years)",
            "job_requirements": "Frontend developer with React experience",
            "min_experience": 10,
            "max_experience": 999,
            "n_candidates": 5
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            result = shortlist_tool._run(
                job_requirements=test_case['job_requirements'],
                min_experience=test_case['min_experience'],
                max_experience=test_case['max_experience'],
                n_candidates=test_case['n_candidates']
            )
            
            print(result)
            print("\n" + "="*50)
            
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            continue
    
    print("\n✅ Experience-based sorting tests completed!")

def test_combined_score_calculation():
    """Test the combined score calculation method"""
    
    print("\n🧪 Testing Combined Score Calculation")
    print("=" * 50)
    
    shortlist_tool = CandidateShortlistTool()
    
    # Mock candidate data
    test_candidates = [
        {
            "distance": 0.3,
            "metadata": {
                "experience_years": 2,
                "skills": "React, JavaScript, HTML, CSS"
            },
            "content": "Frontend developer with React and JavaScript experience"
        },
        {
            "distance": 0.4,
            "metadata": {
                "experience_years": 8,
                "skills": "React, TypeScript, Node.js"
            },
            "content": "Senior frontend developer with extensive React experience"
        },
        {
            "distance": 0.5,
            "metadata": {
                "experience_years": 15,
                "skills": "Python, Django, PostgreSQL"
            },
            "content": "Backend developer with Python and database experience"
        }
    ]
    
    # Test different experience ranges
    experience_ranges = [
        (0, 5, "Entry to Mid Level"),
        (5, 10, "Mid to Senior Level"),
        (10, 999, "Senior+ Level")
    ]
    
    for min_exp, max_exp, range_name in experience_ranges:
        print(f"\n📊 Testing range: {range_name} ({min_exp}-{max_exp} years)")
        print("-" * 40)
        
        for i, candidate in enumerate(test_candidates, 1):
            score = shortlist_tool._calculate_combined_score(candidate, min_exp, max_exp)
            exp_years = candidate["metadata"]["experience_years"]
            
            print(f"Candidate {i}: {exp_years} years experience → Combined Score: {score:.3f}")
        
        print()

if __name__ == "__main__":
    try:
        test_combined_score_calculation()
        test_experience_sorting()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
