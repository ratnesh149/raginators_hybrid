#!/usr/bin/env python3
"""
Test to verify web interface experience filtering behavior
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.candidate_shortlist import CandidateShortlistTool

def test_web_interface_experience_logic():
    """Test the exact logic used in the web interface"""
    
    print("🧪 TESTING WEB INTERFACE EXPERIENCE LOGIC")
    print("=" * 60)
    
    # Simulate the web interface logic
    experience_level = "Mid Level (3-5 years)"  # This is what user selects
    
    # Extract experience requirement (both min and max) - from app.py lines 290-301
    min_exp = 0
    max_exp = 999  # Default to no upper limit
    
    if experience_level != "Any":
        if "0-2" in experience_level:
            min_exp, max_exp = 0, 2
        elif "3-5" in experience_level:
            min_exp, max_exp = 3, 5
        elif "6-10" in experience_level:
            min_exp, max_exp = 6, 10
        elif "10+" in experience_level:
            min_exp, max_exp = 10, 999
    
    print(f"Selected Experience Level: {experience_level}")
    print(f"Parsed Min Experience: {min_exp}")
    print(f"Parsed Max Experience: {max_exp}")
    print()
    
    # Initialize the shortlist tool
    shortlist_tool = CandidateShortlistTool()
    
    # Generate query (simplified version of web interface logic)
    generated_query = "Frontend developer with React experience"
    
    print(f"Generated Query: {generated_query}")
    print(f"Calling shortlist_tool._run with:")
    print(f"  - job_requirements: {generated_query}")
    print(f"  - min_experience: {min_exp}")
    print(f"  - max_experience: {max_exp}")
    print(f"  - n_candidates: 5")
    print()
    
    # Run the actual candidate shortlisting (same as web interface)
    result = shortlist_tool._run(
        job_requirements=generated_query,
        min_experience=min_exp,
        max_experience=max_exp,
        n_candidates=5
    )
    
    print("RESULT:")
    print("=" * 60)
    print(result)

def test_different_experience_levels():
    """Test all experience level options"""
    
    print("\n\n🧪 TESTING ALL EXPERIENCE LEVEL OPTIONS")
    print("=" * 60)
    
    experience_levels = [
        "Any",
        "Entry Level (0-2 years)",
        "Mid Level (3-5 years)", 
        "Senior Level (6-10 years)",
        "Expert Level (10+ years)"
    ]
    
    shortlist_tool = CandidateShortlistTool()
    
    for experience_level in experience_levels:
        print(f"\n🔍 Testing: {experience_level}")
        print("-" * 40)
        
        # Parse experience level (same logic as web interface)
        min_exp = 0
        max_exp = 999
        
        if experience_level != "Any":
            if "0-2" in experience_level:
                min_exp, max_exp = 0, 2
            elif "3-5" in experience_level:
                min_exp, max_exp = 3, 5
            elif "6-10" in experience_level:
                min_exp, max_exp = 6, 10
            elif "10+" in experience_level:
                min_exp, max_exp = 10, 999
        
        print(f"Min/Max Experience: {min_exp}-{max_exp}")
        
        # Run shortlisting
        result = shortlist_tool._run(
            job_requirements="Software developer with React",
            min_experience=min_exp,
            max_experience=max_exp,
            n_candidates=3
        )
        
        # Extract just the candidate names and experience from result
        lines = result.split('\n')
        candidates_found = []
        for i, line in enumerate(lines):
            if line.startswith('**') and '. ' in line:
                name = line.split('**')[1].split('**')[0]
                # Look for experience in next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    if 'Experience:' in lines[j]:
                        exp = lines[j].split('Experience: ')[1].split(' years')[0]
                        candidates_found.append(f"{name} ({exp} years)")
                        break
        
        if candidates_found:
            print("Candidates returned:")
            for candidate in candidates_found:
                print(f"  • {candidate}")
        else:
            print("No candidates found")

if __name__ == "__main__":
    try:
        test_web_interface_experience_logic()
        test_different_experience_levels()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
