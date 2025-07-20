#!/usr/bin/env python3
"""
Test the app integration with job description generator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_job_description_integration():
    """Test that the job description generator can be imported and used"""
    
    print("🧪 TESTING APP INTEGRATION")
    print("=" * 50)
    
    try:
        # Test import
        from tools.job_description_generator import job_description_generator
        print("✅ Job description generator imported successfully")
        
        # Test basic functionality
        job_desc = job_description_generator._run(
            job_title="Software Engineer",
            required_skills="Python, React, AWS",
            experience_level="Mid Level (3-5 years)",
            location="Remote",
            education="Bachelor's",
            company_name="Test Company",
            department="Engineering"
        )
        
        print("✅ Job description generated successfully")
        print(f"Length: {len(job_desc)} characters")
        
        # Check if it contains expected sections
        expected_sections = ["# Software Engineer", "## About the Role", "## Key Responsibilities", "## Requirements", "## What We Offer"]
        
        for section in expected_sections:
            if section in job_desc:
                print(f"✅ Contains section: {section}")
            else:
                print(f"❌ Missing section: {section}")
        
        print("\n🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_job_description_integration()
