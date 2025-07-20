#!/usr/bin/env python3
"""
Test the enhanced skills filtering system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.skills_matcher import skills_matcher
from tools.candidate_shortlist import CandidateShortlistTool

def test_skills_matcher():
    """Test the skills matcher functionality"""
    
    print("🧪 TESTING SKILLS MATCHER")
    print("=" * 60)
    
    # Test 1: Skill normalization
    print("\n🔍 Test 1: Skill Normalization")
    test_skills = ["JavaScript", "React.js", "Node.js", "Python3", "AWS"]
    for skill in test_skills:
        normalized = skills_matcher.normalize_skill(skill)
        print(f"'{skill}' → '{normalized}'")
    
    # Test 2: Skills extraction from text
    print("\n🔍 Test 2: Skills Extraction from Text")
    sample_text = """
    Experienced software developer with expertise in JavaScript, React, and Node.js.
    Proficient in Python programming and AWS cloud services. 
    Strong background in SQL databases and Docker containerization.
    """
    
    extracted_skills = skills_matcher.extract_skills_from_text(sample_text)
    print(f"Extracted skills: {sorted(extracted_skills)}")
    
    # Test 3: Skills matching score calculation
    print("\n🔍 Test 3: Skills Matching Score")
    
    required_skills = ["Python", "React", "AWS", "SQL"]
    candidate_skills = {"python", "react", "javascript", "docker"}
    
    match_result = skills_matcher.calculate_skills_match_score(
        required_skills, candidate_skills, sample_text
    )
    
    print(f"Required: {required_skills}")
    print(f"Candidate has: {sorted(candidate_skills)}")
    print(f"Match Score: {match_result['match_score']:.2f}")
    print(f"Matched Skills: {match_result['matched_skills']}")
    print(f"Missing Skills: {match_result['missing_skills']}")
    print(f"Bonus Skills: {match_result['bonus_skills']}")
    
    # Test 4: Skills recommendations
    print("\n🔍 Test 4: Skills Recommendations")
    
    job_titles = [
        "Frontend Developer",
        "Backend Engineer", 
        "Full Stack Developer",
        "Data Scientist",
        "DevOps Engineer"
    ]
    
    for job_title in job_titles:
        recommendations = skills_matcher.get_skills_recommendations(job_title)
        print(f"{job_title}: {recommendations}")
    
    print("\n✅ Skills matcher tests completed!")

def test_enhanced_candidate_filtering():
    """Test the enhanced candidate filtering with skills"""
    
    print("\n🧪 TESTING ENHANCED CANDIDATE FILTERING")
    print("=" * 60)
    
    # Initialize the shortlist tool
    shortlist_tool = CandidateShortlistTool()
    
    # Test cases with different skill requirements
    test_cases = [
        {
            "name": "Frontend Developer with React",
            "job_requirements": """Job Title: Frontend Developer
Required Skills: React, JavaScript, HTML, CSS
Experience: Mid Level (3-5 years)
Number of candidates needed: 5""",
            "min_experience": 3,
            "max_experience": 5,
            "n_candidates": 5
        },
        {
            "name": "Python Backend Developer",
            "job_requirements": """Job Title: Backend Developer
Required Skills: Python, Django, PostgreSQL, AWS
Experience: Senior Level (6-10 years)
Number of candidates needed: 3""",
            "min_experience": 6,
            "max_experience": 10,
            "n_candidates": 3
        },
        {
            "name": "Data Scientist",
            "job_requirements": """Job Title: Data Scientist
Required Skills: Python, Machine Learning, Pandas, SQL
Experience: Any
Number of candidates needed: 4""",
            "min_experience": 0,
            "max_experience": 999,
            "n_candidates": 4
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            result = shortlist_tool._run(
                job_requirements=test_case['job_requirements'],
                min_experience=test_case['min_experience'],
                max_experience=test_case['max_experience'],
                n_candidates=test_case['n_candidates']
            )
            
            print(result)
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            continue
    
    print("\n✅ Enhanced candidate filtering tests completed!")

def test_skills_filtering_edge_cases():
    """Test edge cases for skills filtering"""
    
    print("\n🧪 TESTING SKILLS FILTERING EDGE CASES")
    print("=" * 60)
    
    # Test 1: No skills required
    print("\n🔍 Test 1: No Skills Required")
    no_skills_result = skills_matcher.calculate_skills_match_score(
        [], {"python", "react"}, "Some content"
    )
    print(f"No skills required - Match Score: {no_skills_result['match_score']}")
    
    # Test 2: Candidate has no skills
    print("\n🔍 Test 2: Candidate Has No Skills")
    no_candidate_skills = skills_matcher.calculate_skills_match_score(
        ["Python", "React"], set(), ""
    )
    print(f"Candidate has no skills - Match Score: {no_candidate_skills['match_score']}")
    print(f"Missing Skills: {no_candidate_skills['missing_skills']}")
    
    # Test 3: Partial skill matches
    print("\n🔍 Test 3: Partial Skill Matches")
    partial_match = skills_matcher.calculate_skills_match_score(
        ["React", "Vue", "Angular"], {"react", "javascript", "html"}, ""
    )
    print(f"Partial matches - Match Score: {partial_match['match_score']}")
    print(f"Matched: {partial_match['matched_skills']}")
    print(f"Missing: {partial_match['missing_skills']}")
    
    # Test 4: Skill synonyms
    print("\n🔍 Test 4: Skill Synonyms")
    synonym_match = skills_matcher.calculate_skills_match_score(
        ["JavaScript", "Node.js"], {"js", "nodejs"}, ""
    )
    print(f"Synonym matches - Match Score: {synonym_match['match_score']}")
    print(f"Matched: {synonym_match['matched_skills']}")
    
    print("\n✅ Edge case tests completed!")

if __name__ == "__main__":
    try:
        test_skills_matcher()
        test_enhanced_candidate_filtering()
        test_skills_filtering_edge_cases()
        
        print("\n🎉 ALL SKILLS FILTERING TESTS COMPLETED!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
