#!/usr/bin/env python3
"""
Hybrid Vector Database Rebuild Script
Rebuilds the vector database with the new hybrid system:
- No chunking (whole resumes)
- Unique candidate IDs
- Enhanced deduplication
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vector_db import get_vector_db
from utils.pdf_resolver import smart_pdf_resolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clear_existing_database():
    """Clear existing ChromaDB database"""
    db_paths = [
        "./chroma_db",
        "./hybrid_chroma_db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            logger.info(f"🗑️  Clearing existing database: {db_path}")
            shutil.rmtree(db_path)
        else:
            logger.info(f"📁 Database path does not exist: {db_path}")

def analyze_pdf_files():
    """Analyze PDF files before processing"""
    logger.info("📊 Analyzing PDF files...")
    
    # Check for duplicate PDFs
    duplicate_groups = smart_pdf_resolver.detect_duplicate_pdfs()
    
    if duplicate_groups:
        logger.warning(f"⚠️  Found {len(duplicate_groups)} groups of potentially duplicate PDFs:")
        for i, group in enumerate(duplicate_groups, 1):
            logger.warning(f"   Group {i}:")
            for pdf_info in group:
                logger.warning(f"     - {pdf_info['pdf_filename']} ({pdf_info['extracted_name']})")
    else:
        logger.info("✅ No duplicate PDFs detected")
    
    # Count total PDFs
    sample_path = Path("sample_resumes")
    if sample_path.exists():
        pdf_count = len(list(sample_path.glob("*.pdf")))
        logger.info(f"📄 Total PDF files to process: {pdf_count}")
    else:
        logger.error("❌ sample_resumes folder not found!")
        return False
    
    return True

def rebuild_database():
    """Rebuild the vector database with hybrid system"""
    logger.info("🚀 Starting hybrid vector database rebuild...")
    
    try:
        # Step 1: Clear existing database
        clear_existing_database()
        
        # Step 2: Analyze PDF files
        if not analyze_pdf_files():
            return False
        
        # Step 3: Initialize hybrid vector database
        logger.info("🔧 Initializing hybrid vector database...")
        vector_db = get_vector_db()
        
        # Step 4: Add sample data with hybrid processing
        logger.info("📚 Processing PDF files with hybrid system...")
        vector_db.add_sample_data()
        
        # Step 5: Verify database contents
        logger.info("🔍 Verifying database contents...")
        
        # Test search to verify everything works
        test_results = vector_db.search_candidates("React JavaScript", n_results=5)
        logger.info(f"✅ Test search returned {len(test_results)} candidates")
        
        # Check for unique IDs
        unique_ids = set()
        for result in test_results:
            unique_id = result.get('metadata', {}).get('unique_id')
            if unique_id:
                unique_ids.add(unique_id)
        
        logger.info(f"🆔 Unique candidate IDs in test results: {len(unique_ids)}")
        
        if len(unique_ids) == len(test_results):
            logger.info("✅ All test results have unique IDs - deduplication working!")
        else:
            logger.warning("⚠️  Some results may not have unique IDs")
        
        logger.info("🎉 Hybrid vector database rebuild completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error rebuilding database: {e}")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("🔄 HYBRID VECTOR DATABASE REBUILD")
    print("=" * 70)
    print()
    
    success = rebuild_database()
    
    print()
    print("=" * 70)
    if success:
        print("✅ REBUILD COMPLETED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("1. Test the hybrid system: python test_hybrid_system.py")
        print("2. Start the web app: python start_web_app.py")
        print("3. Test deduplication: Search for 'React, experience 4, top 5'")
    else:
        print("❌ REBUILD FAILED!")
        print("Check the logs above for error details.")
    print("=" * 70)

if __name__ == "__main__":
    main()
