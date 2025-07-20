#!/usr/bin/env python3
"""
Debug script to test the specific experience filtering issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.candidate_shortlist import CandidateShortlistTool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_experience_filter():
    """Debug the specific experience filtering issue"""
    
    print("🔍 DEBUGGING EXPERIENCE FILTER ISSUE")
    print("=" * 60)
    
    # Initialize the shortlist tool
    shortlist_tool = CandidateShortlistTool()
    
    # Test the specific case: "3 to 5" years experience
    print("\n🧪 Testing: Frontend developer with React, 3-5 years experience")
    print("-" * 60)
    
    try:
        # This should only return candidates with 3-5 years experience
        result = shortlist_tool._run(
            job_requirements="Frontend developer with React experience",
            min_experience=3,
            max_experience=5,
            n_candidates=10
        )
        
        print(result)
        
        # Let's also check what candidates are in the database
        print("\n" + "="*60)
        print("🔍 CHECKING ALL CANDIDATES IN DATABASE")
        print("="*60)
        
        # Get all candidates without filtering
        all_candidates_result = shortlist_tool._run(
            job_requirements="Frontend developer with React experience",
            min_experience=0,
            max_experience=999,
            n_candidates=20
        )
        
        print(all_candidates_result)
        
    except Exception as e:
        print(f"❌ Error in debug test: {e}")
        import traceback
        traceback.print_exc()

def check_database_experience_distribution():
    """Check the experience distribution in the database"""
    
    print("\n🔍 CHECKING EXPERIENCE DISTRIBUTION IN DATABASE")
    print("=" * 60)
    
    from services.vector_db import get_vector_db
    
    try:
        vector_db = get_vector_db()
        
        # Get all candidates
        all_results = vector_db.search_candidates("software developer", 50)
        
        experience_counts = {}
        for result in all_results:
            metadata = result.get('metadata', {})
            exp = metadata.get('experience_years', 0)
            exp_range = f"{int(exp)}" if exp < 20 else "20+"
            experience_counts[exp_range] = experience_counts.get(exp_range, 0) + 1
        
        print("📊 Experience Distribution:")
        for exp, count in sorted(experience_counts.items(), key=lambda x: float(x[0]) if x[0] != "20+" else 999):
            print(f"   {exp} years: {count} candidates")
            
        # Specifically check for 3-5 year candidates
        candidates_3_to_5 = []
        for result in all_results:
            metadata = result.get('metadata', {})
            exp = metadata.get('experience_years', 0)
            if 3 <= exp <= 5:
                name = metadata.get('candidate_name', 'Unknown')
                candidates_3_to_5.append(f"{name} ({exp} years)")
        
        print(f"\n🎯 Candidates with 3-5 years experience ({len(candidates_3_to_5)}):")
        for candidate in candidates_3_to_5:
            print(f"   • {candidate}")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    try:
        check_database_experience_distribution()
        debug_experience_filter()
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
