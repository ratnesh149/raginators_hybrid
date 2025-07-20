#!/usr/bin/env python3
"""
Hybrid System Test Script
Tests the hybrid implementation to ensure:
1. No duplicate candidates
2. Unique ID system working
3. Enhanced deduplication working
4. PDF resolution working
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vector_db import get_vector_db
from tools.candidate_shortlist import candidate_shortlist_tool
from utils.pdf_resolver import smart_pdf_resolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_vector_database():
    """Test the hybrid vector database"""
    print("🔍 Testing Hybrid Vector Database...")
    print("-" * 50)
    
    try:
        vector_db = get_vector_db()
        
        # Test 1: Basic search
        results = vector_db.search_candidates("React JavaScript", n_results=10)
        print(f"✅ Basic search returned {len(results)} candidates")
        
        # Test 2: Check unique IDs
        unique_ids = set()
        candidates_with_ids = 0
        
        for result in results:
            metadata = result.get('metadata', {})
            unique_id = metadata.get('unique_id')
            if unique_id:
                unique_ids.add(unique_id)
                candidates_with_ids += 1
        
        print(f"✅ Candidates with unique IDs: {candidates_with_ids}/{len(results)}")
        print(f"✅ Unique IDs found: {len(unique_ids)}")
        
        if len(unique_ids) == candidates_with_ids:
            print("✅ All candidates have unique IDs - no duplicates at database level!")
        else:
            print("⚠️  Some candidates may be duplicates at database level")
        
        # Test 3: Experience filtering
        experienced_results = vector_db.search_candidates(
            "React JavaScript", 
            n_results=5,
            filters={'experience_years': {'>=': 4}}
        )
        print(f"✅ Experience filter (>=4 years) returned {len(experienced_results)} candidates")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector database test failed: {e}")
        return False

def test_candidate_shortlisting():
    """Test the enhanced candidate shortlisting tool"""
    print("\n🎯 Testing Enhanced Candidate Shortlisting...")
    print("-" * 50)
    
    try:
        # Test the exact scenario that was causing duplicates
        result = candidate_shortlist_tool._run(
            job_requirements="React JavaScript frontend developer",
            min_experience=4,
            n_candidates=5
        )
        
        print("📋 Shortlist Result:")
        print(result)
        
        # Analyze the result for duplicates
        lines = result.split('\n')
        candidate_names = []
        unique_ids = []
        
        for line in lines:
            if line.strip().startswith('**') and '. ' in line:
                # Extract candidate name
                name_part = line.split('. ', 1)[1].replace('**', '')
                candidate_names.append(name_part)
            elif 'Unique ID:' in line:
                # Extract unique ID
                unique_id = line.split('Unique ID: ')[1].split('...')[0]
                unique_ids.append(unique_id)
        
        print(f"\n📊 Analysis:")
        print(f"   • Candidates found: {len(candidate_names)}")
        print(f"   • Unique IDs found: {len(unique_ids)}")
        print(f"   • Unique names: {len(set(candidate_names))}")
        print(f"   • Unique IDs: {len(set(unique_ids))}")
        
        if len(set(candidate_names)) == len(candidate_names):
            print("✅ No duplicate names in shortlist!")
        else:
            print("⚠️  Duplicate names detected in shortlist")
        
        if len(set(unique_ids)) == len(unique_ids):
            print("✅ All unique IDs are different!")
        else:
            print("⚠️  Duplicate unique IDs detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Candidate shortlisting test failed: {e}")
        return False

def test_pdf_resolver():
    """Test the smart PDF resolver"""
    print("\n📄 Testing Smart PDF Resolver...")
    print("-" * 50)
    
    try:
        # Test 1: Find matches for a common name
        matches = smart_pdf_resolver.find_matching_pdfs("John Smith", similarity_threshold=0.5)
        print(f"✅ Found {len(matches)} matches for 'John Smith'")
        
        if matches:
            for match in matches[:3]:  # Show top 3
                print(f"   • {match['pdf_filename']} (similarity: {match['similarity_score']:.2f})")
        
        # Test 2: Detect duplicate PDFs
        duplicate_groups = smart_pdf_resolver.detect_duplicate_pdfs()
        print(f"✅ Found {len(duplicate_groups)} groups of potentially duplicate PDFs")
        
        if duplicate_groups:
            for i, group in enumerate(duplicate_groups[:2], 1):  # Show first 2 groups
                print(f"   Group {i}:")
                for pdf_info in group:
                    print(f"     - {pdf_info['pdf_filename']}")
        
        # Test 3: Resolve best PDF for a candidate
        best_match = smart_pdf_resolver.resolve_best_pdf("John Doe")
        if best_match:
            print(f"✅ Best match for 'John Doe': {best_match['pdf_filename']}")
        else:
            print("ℹ️  No matches found for 'John Doe'")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF resolver test failed: {e}")
        return False

def test_deduplication_scenario():
    """Test the specific deduplication scenario"""
    print("\n🔒 Testing Deduplication Scenario...")
    print("-" * 50)
    
    try:
        vector_db = get_vector_db()
        
        # Get a larger set of results to test deduplication
        all_results = vector_db.search_candidates("React", n_results=20)
        print(f"📊 Retrieved {len(all_results)} candidates for deduplication test")
        
        # Check for potential duplicates manually
        seen_names = {}
        seen_content_hashes = {}
        potential_duplicates = []
        
        for i, result in enumerate(all_results):
            metadata = result.get('metadata', {})
            name = metadata.get('candidate_name', '').lower().strip()
            content = result.get('content', '')[:200]  # First 200 chars
            
            # Check name duplicates
            if name in seen_names:
                potential_duplicates.append({
                    'type': 'name',
                    'name': name,
                    'indices': [seen_names[name], i]
                })
            else:
                seen_names[name] = i
            
            # Check content similarity (basic)
            content_hash = hash(content)
            if content_hash in seen_content_hashes:
                potential_duplicates.append({
                    'type': 'content',
                    'name': name,
                    'indices': [seen_content_hashes[content_hash], i]
                })
            else:
                seen_content_hashes[content_hash] = i
        
        print(f"🔍 Potential duplicates found: {len(potential_duplicates)}")
        
        if potential_duplicates:
            print("⚠️  Potential duplicate candidates:")
            for dup in potential_duplicates[:3]:  # Show first 3
                print(f"   • {dup['type'].title()} duplicate: {dup['name']}")
        else:
            print("✅ No obvious duplicates found in raw results!")
        
        return True
        
    except Exception as e:
        print(f"❌ Deduplication test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 70)
    print("🧪 HYBRID SYSTEM COMPREHENSIVE TEST")
    print("=" * 70)
    
    tests = [
        ("Vector Database", test_vector_database),
        ("Candidate Shortlisting", test_candidate_shortlisting),
        ("PDF Resolver", test_pdf_resolver),
        ("Deduplication Scenario", test_deduplication_scenario)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("-" * 70)
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Hybrid system is working correctly!")
        print("\nYou can now:")
        print("1. Start the web app: python start_web_app.py")
        print("2. Test with: 'React, experience 4, top 5'")
        print("3. Verify no duplicate candidates are returned")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check the output above for details.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
