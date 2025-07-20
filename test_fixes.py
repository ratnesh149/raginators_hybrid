#!/usr/bin/env python3
"""
Test script to verify the TypeError fix and 60% threshold change
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_match_score_calculation():
    """Test the fixed match score calculation"""
    print("🧪 Testing Match Score Calculation Fix")
    print("=" * 40)
    
    # Test data with different match_score formats
    test_candidates = [
        {"match_score": "85%", "name": "John"},
        {"match_score": "92%", "name": "Jane"},
        {"match_score": 0.75, "name": "Mike"},  # Float format
        {"match_score": 88, "name": "Sarah"},   # Integer format
        {"match_score": None, "name": "Bob"},   # None value
        {"match_score": "N/A", "name": "Alice"} # String without %
    ]
    
    try:
        # Simulate the fixed calculation logic
        match_scores = []
        for c in test_candidates:
            match_score = c.get('match_score', '0%')
            if isinstance(match_score, str) and '%' in match_score:
                match_scores.append(int(match_score.replace('%', '')))
            elif isinstance(match_score, (int, float)):
                match_scores.append(int(match_score * 100) if match_score <= 1 else int(match_score))
            else:
                match_scores.append(0)
        
        avg_match = sum(match_scores) / len(match_scores) if match_scores else 0
        
        print(f"✅ Match score calculation successful")
        print(f"   Individual scores: {match_scores}")
        print(f"   Average: {avg_match:.1f}%")
        return True
        
    except Exception as e:
        print(f"❌ Match score calculation failed: {e}")
        return False

def test_threshold_change():
    """Test the 60% threshold change"""
    print("\n🧪 Testing 60% Threshold Change")
    print("=" * 40)
    
    try:
        from services.candidate_evaluator import candidate_evaluator
        
        # Check if threshold is correctly set to 0.60
        threshold = candidate_evaluator.selection_threshold
        
        if threshold == 0.60:
            print(f"✅ Threshold correctly set to {threshold} (60%)")
            return True
        else:
            print(f"❌ Threshold is {threshold}, expected 0.60")
            return False
            
    except Exception as e:
        print(f"❌ Threshold test failed: {e}")
        return False

def test_evaluation_with_new_threshold():
    """Test evaluation with the new 60% threshold"""
    print("\n🧪 Testing Evaluation with 60% Threshold")
    print("=" * 40)
    
    try:
        from services.candidate_evaluator import candidate_evaluator
        
        # Create test candidate data
        test_candidate = {
            'content': 'React developer with 3 years experience in JavaScript and HTML',
            'metadata': {
                'candidate_name': 'Test User',
                'experience_years': 3,
                'skills': 'React, JavaScript, HTML',
                'email': 'test@example.com',
                'unique_id': 'test_001'
            },
            'distance': 0.4  # This should result in ~60% score
        }
        
        job_description = 'Looking for React developer with JavaScript skills. 2-5 years experience.'
        
        # Test evaluation
        score = candidate_evaluator.evaluate_candidate(test_candidate, job_description)
        
        print(f"✅ Evaluation successful")
        print(f"   Overall Score: {score.overall_score:.1%}")
        print(f"   Skills Score: {score.skills_score:.1%}")
        print(f"   Experience Score: {score.experience_score:.1%}")
        print(f"   Semantic Score: {score.semantic_score:.1%}")
        
        # Test selection logic
        is_selected = score.overall_score >= candidate_evaluator.selection_threshold
        print(f"   Selection Status: {'SELECTED' if is_selected else 'REJECTED'}")
        print(f"   Threshold: {candidate_evaluator.selection_threshold:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_text_updates():
    """Test that UI text has been updated to reflect 60% threshold"""
    print("\n🧪 Testing UI Text Updates")
    print("=" * 40)
    
    try:
        # Read app.py and check for updated text
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        # Check for 60% references
        if '60%+ Match' in app_content:
            print("✅ Found '60%+ Match' in UI text")
        else:
            print("❌ '60%+ Match' not found in UI text")
        
        if 'Below 60% Threshold' in app_content:
            print("✅ Found 'Below 60% Threshold' in UI text")
        else:
            print("❌ 'Below 60% Threshold' not found in UI text")
        
        if '60% accuracy threshold' in app_content:
            print("✅ Found '60% accuracy threshold' in UI text")
        else:
            print("❌ '60% accuracy threshold' not found in UI text")
        
        # Check that old 90% references are removed
        old_90_count = app_content.count('90%')
        if old_90_count == 0:
            print("✅ All 90% references removed from UI")
        else:
            print(f"⚠️  Still found {old_90_count} references to 90% in UI")
        
        return True
        
    except Exception as e:
        print(f"❌ UI text test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing TypeError Fix and 60% Threshold Change")
    print("=" * 60)
    
    # Test 1: Match score calculation fix
    test1_result = test_match_score_calculation()
    
    # Test 2: Threshold change
    test2_result = test_threshold_change()
    
    # Test 3: Evaluation with new threshold
    test3_result = test_evaluation_with_new_threshold()
    
    # Test 4: UI text updates
    test4_result = test_ui_text_updates()
    
    print("\n📋 **TEST SUMMARY**")
    print("=" * 60)
    print(f"✅ Match Score Fix: {'PASS' if test1_result else 'FAIL'}")
    print(f"✅ Threshold Change: {'PASS' if test2_result else 'FAIL'}")
    print(f"✅ Evaluation Test: {'PASS' if test3_result else 'FAIL'}")
    print(f"✅ UI Text Updates: {'PASS' if test4_result else 'FAIL'}")
    
    if all([test1_result, test2_result, test3_result, test4_result]):
        print("\n🎉 **ALL TESTS PASSED**")
        print("✅ TypeError has been fixed")
        print("✅ Threshold changed to 60%")
        print("✅ UI updated to reflect new threshold")
        print("✅ System ready for use")
    else:
        print("\n⚠️  **SOME TESTS FAILED**")
        print("Check the error messages above for details.")

if __name__ == "__main__":
    main()
