#!/usr/bin/env python3
"""
Test the training system functionality
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.training_system import CandidateTrainingSystem

def test_training_system():
    """Test the training system with sample data"""
    
    print("🧪 TESTING TRAINING SYSTEM")
    print("=" * 60)
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize training system with temp directory
        training_system = CandidateTrainingSystem(temp_dir)
        
        print("✅ Training system initialized")
        
        # Test 1: Record search interactions
        print("\n🔍 Test 1: Recording Search Interactions")
        
        # Sample search data
        search_data_1 = {
            "job_title": "Software Engineer",
            "required_skills": "Python, React, AWS",
            "experience_level": "Mid Level (3-5 years)",
            "location": "Remote",
            "education": "Bachelor's",
            "num_candidates": 5
        }
        
        # Sample results
        results_1 = [
            {"name": "John Doe", "experience": "4 years", "match_score": "85%", "skills": "Python, React, JavaScript"},
            {"name": "Jane Smith", "experience": "3 years", "match_score": "78%", "skills": "Python, AWS, Docker"},
            {"name": "Bob Johnson", "experience": "5 years", "match_score": "92%", "skills": "React, Node.js, AWS"}
        ]
        
        training_system.record_search_interaction(search_data_1, results_1, "Good results")
        print("✅ Recorded first search interaction")
        
        # Record another interaction
        search_data_2 = {
            "job_title": "Data Scientist",
            "required_skills": "Python, Machine Learning, SQL",
            "experience_level": "Senior Level (6-10 years)",
            "location": "New York",
            "education": "Master's",
            "num_candidates": 3
        }
        
        results_2 = [
            {"name": "Alice Brown", "experience": "7 years", "match_score": "88%", "skills": "Python, ML, Pandas"},
            {"name": "Charlie Davis", "experience": "8 years", "match_score": "91%", "skills": "Python, SQL, TensorFlow"}
        ]
        
        training_system.record_search_interaction(search_data_2, results_2, "Excellent matches")
        print("✅ Recorded second search interaction")
        
        # Test 2: Get skill recommendations
        print("\n💡 Test 2: Skill Recommendations")
        
        software_skills = training_system.get_skill_recommendations("Software Engineer")
        print(f"Software Engineer recommendations: {software_skills}")
        
        data_skills = training_system.get_skill_recommendations("Data Scientist")
        print(f"Data Scientist recommendations: {data_skills}")
        
        # Test 3: Experience insights
        print("\n📊 Test 3: Experience Insights")
        
        mid_level_insights = training_system.get_experience_insights("Mid Level (3-5 years)")
        print(f"Mid Level insights: {mid_level_insights}")
        
        senior_level_insights = training_system.get_experience_insights("Senior Level (6-10 years)")
        print(f"Senior Level insights: {senior_level_insights}")
        
        # Test 4: Training summary
        print("\n📈 Test 4: Training Summary")
        
        summary = training_system.get_training_summary()
        print(f"Total searches: {summary['total_searches']}")
        print(f"Success rate: {summary['overall_success_rate']:.1f}%")
        print(f"Field effectiveness: {summary['field_effectiveness']}")
        
        # Test 5: Popular combinations
        print("\n🏆 Test 5: Popular Combinations")
        
        popular = training_system.get_popular_combinations()
        for i, combo in enumerate(popular, 1):
            print(f"{i}. {combo['job_title']} - {combo['experience_level']} - Success: {combo['success_score']}")
        
        print("\n✅ All training system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Training system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_training_persistence():
    """Test that training data persists across sessions"""
    
    print("\n🧪 TESTING TRAINING PERSISTENCE")
    print("=" * 60)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create first training system instance
        training1 = CandidateTrainingSystem(temp_dir)
        
        # Add some data
        search_data = {
            "job_title": "Frontend Developer",
            "required_skills": "React, JavaScript, CSS",
            "experience_level": "Entry Level (0-2 years)",
            "location": "San Francisco",
            "education": "Bachelor's",
            "num_candidates": 4
        }
        
        results = [
            {"name": "Test User", "experience": "1 year", "match_score": "75%", "skills": "React, CSS"}
        ]
        
        training1.record_search_interaction(search_data, results)
        
        # Create second training system instance (simulating app restart)
        training2 = CandidateTrainingSystem(temp_dir)
        
        # Check if data persisted
        summary = training2.get_training_summary()
        
        if summary["total_searches"] > 0:
            print("✅ Training data persisted across sessions")
            print(f"Found {summary['total_searches']} searches in reloaded system")
            return True
        else:
            print("❌ Training data did not persist")
            return False
            
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        return False
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    try:
        success1 = test_training_system()
        success2 = test_training_persistence()
        
        if success1 and success2:
            print("\n🎉 ALL TRAINING SYSTEM TESTS PASSED!")
        else:
            print("\n❌ SOME TESTS FAILED!")
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
