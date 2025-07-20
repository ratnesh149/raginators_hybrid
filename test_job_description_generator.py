#!/usr/bin/env python3
"""
Test the job description generator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.job_description_generator import job_description_generator

def test_job_description_generator():
    """Test the job description generator with different inputs"""
    
    print("🧪 TESTING JOB DESCRIPTION GENERATOR")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "Software Engineer - Full Stack",
            "job_title": "Senior Software Engineer",
            "required_skills": "React, Node.js, Python, AWS, PostgreSQL",
            "experience_level": "Senior Level (6-10 years)",
            "location": "Remote",
            "education": "Bachelor's"
        },
        {
            "name": "Data Scientist - Entry Level",
            "job_title": "Data Scientist",
            "required_skills": "Python, Machine Learning, SQL, Pandas, Scikit-learn",
            "experience_level": "Entry Level (0-2 years)",
            "location": "New York, NY",
            "education": "Master's"
        },
        {
            "name": "Frontend Developer - Mid Level",
            "job_title": "Frontend Developer",
            "required_skills": "React, JavaScript, CSS, HTML, TypeScript",
            "experience_level": "Mid Level (3-5 years)",
            "location": "San Francisco, CA",
            "education": "Bachelor's"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            job_desc = job_description_generator._run(
                job_title=test_case['job_title'],
                required_skills=test_case['required_skills'],
                experience_level=test_case['experience_level'],
                location=test_case['location'],
                education=test_case['education'],
                company_name="TechCorp Inc.",
                department="Engineering"
            )
            
            print(job_desc)
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
            continue
    
    print("\n✅ Job description generator tests completed!")

if __name__ == "__main__":
    try:
        test_job_description_generator()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
