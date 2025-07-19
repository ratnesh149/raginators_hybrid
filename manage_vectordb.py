#!/usr/bin/env python3
"""
Vector Database Management CLI
Manage HR documents in the vector database
"""

import argparse
import sys
from pathlib import Path
from services.vector_db import get_vector_db
from tools.document_processor import DocumentProcessor, initialize_sample_data

def add_job_description(args):
    """Add a job description to the vector database"""
    vector_db = get_vector_db()
    
    if args.file:
        processor = DocumentProcessor()
        metadata = {"department": args.department, "level": args.level} if args.department or args.level else None
        processor.add_job_description_from_file(args.file, args.title, metadata)
    else:
        metadata = {"department": args.department, "level": args.level} if args.department or args.level else None
        vector_db.add_job_description(args.title, args.description, metadata)
    
    print(f"✅ Added job description: {args.title}")

def add_resume(args):
    """Add a resume to the vector database"""
    vector_db = get_vector_db()
    
    if args.file:
        processor = DocumentProcessor()
        metadata = {"experience_years": args.experience} if args.experience else None
        processor.add_resume_from_file(args.file, args.name, metadata)
    else:
        metadata = {"experience_years": args.experience} if args.experience else None
        vector_db.add_resume(args.name, args.content, metadata)
    
    print(f"✅ Added resume: {args.name}")

def add_policy(args):
    """Add an HR policy to the vector database"""
    vector_db = get_vector_db()
    
    if args.file:
        processor = DocumentProcessor()
        processor.add_hr_policy_from_file(args.file, args.name)
    else:
        vector_db.add_hr_policy(args.name, args.content)
    
    print(f"✅ Added HR policy: {args.name}")

def search_jobs(args):
    """Search for similar job descriptions"""
    vector_db = get_vector_db()
    results = vector_db.search_similar_jobs(args.query, args.limit)
    
    print(f"🔍 Search results for '{args.query}':")
    print("=" * 50)
    
    if not results:
        print("No results found.")
        return
    
    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        job_title = metadata.get('job_title', 'Unknown')
        department = metadata.get('department', 'Unknown')
        
        print(f"{i}. **{job_title}** ({department})")
        print(f"   {result['content'][:200]}...")
        print(f"   Similarity: {1 - result.get('distance', 1):.2f}")
        print()

def search_candidates(args):
    """Search for candidates matching requirements"""
    vector_db = get_vector_db()
    results = vector_db.search_candidates(args.requirements, args.limit)
    
    print(f"🔍 Candidate search results for '{args.requirements}':")
    print("=" * 50)
    
    if not results:
        print("No candidates found.")
        return
    
    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        candidate_name = metadata.get('candidate_name', 'Unknown')
        
        print(f"{i}. **{candidate_name}**")
        print(f"   {result['content'][:200]}...")
        print(f"   Match Score: {1 - result.get('distance', 1):.2f}")
        print()

def bulk_import(args):
    """Bulk import documents from a directory"""
    processor = DocumentProcessor()
    processor.bulk_process_directory(args.directory, args.type)
    print(f"✅ Bulk import completed from {args.directory}")

def init_sample_data(args):
    """Initialize with sample data"""
    initialize_sample_data()
    print("✅ Sample data initialized")

def main():
    parser = argparse.ArgumentParser(description="Manage HR Vector Database")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add job description
    jd_parser = subparsers.add_parser('add-job', help='Add job description')
    jd_parser.add_argument('title', help='Job title')
    jd_parser.add_argument('--description', help='Job description text')
    jd_parser.add_argument('--file', help='Path to job description file')
    jd_parser.add_argument('--department', help='Department')
    jd_parser.add_argument('--level', help='Job level (Junior/Mid/Senior)')
    jd_parser.set_defaults(func=add_job_description)
    
    # Add resume
    resume_parser = subparsers.add_parser('add-resume', help='Add resume')
    resume_parser.add_argument('name', help='Candidate name')
    resume_parser.add_argument('--content', help='Resume content text')
    resume_parser.add_argument('--file', help='Path to resume file')
    resume_parser.add_argument('--experience', type=int, help='Years of experience')
    resume_parser.set_defaults(func=add_resume)
    
    # Add HR policy
    policy_parser = subparsers.add_parser('add-policy', help='Add HR policy')
    policy_parser.add_argument('name', help='Policy name')
    policy_parser.add_argument('--content', help='Policy content text')
    policy_parser.add_argument('--file', help='Path to policy file')
    policy_parser.set_defaults(func=add_policy)
    
    # Search jobs
    search_jobs_parser = subparsers.add_parser('search-jobs', help='Search job descriptions')
    search_jobs_parser.add_argument('query', help='Search query')
    search_jobs_parser.add_argument('--limit', type=int, default=5, help='Number of results')
    search_jobs_parser.set_defaults(func=search_jobs)
    
    # Search candidates
    search_candidates_parser = subparsers.add_parser('search-candidates', help='Search candidates')
    search_candidates_parser.add_argument('requirements', help='Job requirements')
    search_candidates_parser.add_argument('--limit', type=int, default=10, help='Number of results')
    search_candidates_parser.set_defaults(func=search_candidates)
    
    # Bulk import
    bulk_parser = subparsers.add_parser('bulk-import', help='Bulk import documents')
    bulk_parser.add_argument('directory', help='Directory path')
    bulk_parser.add_argument('--type', choices=['job_descriptions', 'resumes', 'hr_policies', 'auto'], 
                           default='auto', help='Document type')
    bulk_parser.set_defaults(func=bulk_import)
    
    # Initialize sample data
    init_parser = subparsers.add_parser('init-sample', help='Initialize with sample data')
    init_parser.set_defaults(func=init_sample_data)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
