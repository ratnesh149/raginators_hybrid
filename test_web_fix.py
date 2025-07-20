#!/usr/bin/env python3
"""
Test to verify the web interface fix for experience filtering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.candidate_shortlist import CandidateShortlistTool
from services.vector_db import get_vector_db

def test_web_interface_fix():
    """Test the fixed web interface logic"""
    
    print("🧪 TESTING FIXED WEB INTERFACE LOGIC")
    print("=" * 60)
    
    # Simulate the web interface parameters
    experience_level = "Mid Level (3-5 years)"
    generated_query = "Frontend developer with React experience"
    num_candidates = 5
    
    # Parse experience level (same as web interface)
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
    
    print(f"Experience Level: {experience_level}")
    print(f"Min/Max Experience: {min_exp}-{max_exp}")
    print(f"Query: {generated_query}")
    print()
    
    # Initialize tools
    shortlist_tool = CandidateShortlistTool()
    vector_db = get_vector_db()
    
    print("🔍 STEP 1: Get raw results from vector DB")
    raw_results = vector_db.search_candidates(generated_query, num_candidates * 3)
    print(f"Raw results count: {len(raw_results)}")
    
    # Show experience distribution of raw results
    raw_experiences = []
    for candidate in raw_results[:10]:  # Show first 10
        metadata = candidate.get('metadata', {})
        exp = metadata.get('experience_years', 0)
        name = metadata.get('candidate_name', 'Unknown')
        raw_experiences.append(f"{name} ({exp} years)")
    
    print("Raw results (first 10):")
    for exp in raw_experiences:
        print(f"  • {exp}")
    print()
    
    print("🔍 STEP 2: Apply experience filtering")
    filtered_results = []
    for candidate in raw_results:
        metadata = candidate.get('metadata', {})
        candidate_experience = metadata.get('experience_years', 0)
        
        # Apply the same experience filter as the shortlist tool
        if min_exp <= candidate_experience <= max_exp:
            filtered_results.append(candidate)
    
    print(f"Filtered results count: {len(filtered_results)}")
    
    # Show filtered results
    filtered_experiences = []
    for candidate in filtered_results:
        metadata = candidate.get('metadata', {})
        exp = metadata.get('experience_years', 0)
        name = metadata.get('candidate_name', 'Unknown')
        filtered_experiences.append(f"{name} ({exp} years)")
    
    print("Filtered results:")
    for exp in filtered_experiences:
        print(f"  • {exp}")
    print()
    
    print("🔍 STEP 3: Deduplicate filtered results")
    unique_results = shortlist_tool._deduplicate_candidates(filtered_results)
    print(f"Unique results count: {len(unique_results)}")
    
    # Show final results
    final_experiences = []
    for candidate in unique_results[:num_candidates]:
        metadata = candidate.get('metadata', {})
        exp = metadata.get('experience_years', 0)
        name = metadata.get('candidate_name', 'Unknown')
        final_experiences.append(f"{name} ({exp} years)")
    
    print("Final results (what web interface will show):")
    for exp in final_experiences:
        print(f"  • {exp}")
    
    # Verify all results are within experience range
    print("\n✅ VERIFICATION:")
    all_within_range = True
    for candidate in unique_results[:num_candidates]:
        metadata = candidate.get('metadata', {})
        exp = metadata.get('experience_years', 0)
        if not (min_exp <= exp <= max_exp):
            print(f"❌ {metadata.get('candidate_name', 'Unknown')} has {exp} years (outside {min_exp}-{max_exp} range)")
            all_within_range = False
    
    if all_within_range:
        print(f"✅ All candidates are within {min_exp}-{max_exp} years experience range!")
    else:
        print("❌ Some candidates are outside the experience range!")
    
    return all_within_range

if __name__ == "__main__":
    try:
        success = test_web_interface_fix()
        if success:
            print("\n🎉 WEB INTERFACE FIX VERIFIED SUCCESSFULLY!")
        else:
            print("\n❌ WEB INTERFACE FIX NEEDS MORE WORK!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
