#!/usr/bin/env python3
"""
Unique Candidate ID System
Generates unique IDs based on content and metadata to resolve duplicate name issues
"""

import hashlib
import os
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CandidateIdentity:
    """Candidate identity information"""
    unique_id: str
    name: str
    email: str
    phone: str
    file_hash: str
    pdf_filename: str

class CandidateIDGenerator:
    """Generates unique candidate IDs to resolve duplicate name conflicts"""
    
    def __init__(self):
        self.id_cache = {}  # Cache to avoid regenerating IDs
    
    def generate_unique_id(self, pdf_content: str, metadata: Dict[str, Any], pdf_filename: str) -> str:
        """
        Generate unique candidate ID based on multiple factors
        Format: candidate_<content_hash>_<meta_hash>
        """
        
        # Primary: Content hash (most reliable)
        content_hash = self._hash_content(pdf_content)
        
        # Secondary: Metadata fingerprint
        meta_hash = self._hash_metadata(metadata)
        
        # Tertiary: File hash (for identical content with different metadata)
        file_hash = self._hash_filename(pdf_filename)
        
        # Combine all hashes for maximum uniqueness
        unique_id = f"candidate_{content_hash}_{meta_hash}_{file_hash}"
        
        return unique_id
    
    def _hash_content(self, content: str) -> str:
        """Generate hash from PDF content"""
        if not content:
            return "empty"
        
        # Normalize content for consistent hashing
        normalized = self._normalize_text(content)
        
        # Use MD5 for speed (not for security)
        content_hash = hashlib.md5(normalized.encode('utf-8')).hexdigest()
        return content_hash[:8]  # First 8 characters
    
    def _hash_metadata(self, metadata: Dict[str, Any]) -> str:
        """Generate hash from candidate metadata"""
        # Extract key identifying information
        email = metadata.get('email', '').lower().strip()
        phone = metadata.get('phone', '').strip()
        name = metadata.get('candidate_name', '').lower().strip()
        
        # Create metadata fingerprint
        meta_string = f"{email}|{phone}|{name}"
        
        if not meta_string.strip('|'):
            return "nometa"
        
        meta_hash = hashlib.md5(meta_string.encode('utf-8')).hexdigest()
        return meta_hash[:4]  # First 4 characters
    
    def _hash_filename(self, filename: str) -> str:
        """Generate hash from filename"""
        if not filename:
            return "nofile"
        
        # Extract meaningful parts from filename
        basename = os.path.basename(filename).lower()
        
        # Remove common prefixes/suffixes
        basename = basename.replace('resume_', '').replace('.pdf', '')
        
        file_hash = hashlib.md5(basename.encode('utf-8')).hexdigest()
        return file_hash[:4]  # First 4 characters
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent hashing"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might vary
        text = re.sub(r'[^\w\s@.-]', '', text)
        
        # Sort lines to handle different PDF extraction orders
        lines = text.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Keep first 50 lines for hashing (enough for uniqueness)
        if len(lines) > 50:
            lines = lines[:50]
        
        return '\n'.join(sorted(lines))
    
    def create_candidate_identity(self, pdf_content: str, metadata: Dict[str, Any], 
                                pdf_filename: str) -> CandidateIdentity:
        """Create complete candidate identity"""
        
        unique_id = self.generate_unique_id(pdf_content, metadata, pdf_filename)
        
        return CandidateIdentity(
            unique_id=unique_id,
            name=metadata.get('candidate_name', 'Unknown'),
            email=metadata.get('email', ''),
            phone=metadata.get('phone', ''),
            file_hash=self._hash_content(pdf_content),
            pdf_filename=pdf_filename
        )
    
    def resolve_duplicate_names(self, candidates_with_same_name: list) -> Dict[str, CandidateIdentity]:
        """
        Resolve multiple candidates with the same name
        Returns mapping of unique_id -> CandidateIdentity
        """
        resolved = {}
        
        for candidate_data in candidates_with_same_name:
            identity = self.create_candidate_identity(
                pdf_content=candidate_data['content'],
                metadata=candidate_data['metadata'],
                pdf_filename=candidate_data['filename']
            )
            
            resolved[identity.unique_id] = identity
        
        return resolved

# Global instance
candidate_id_generator = CandidateIDGenerator()

def generate_candidate_id(pdf_content: str, metadata: Dict[str, Any], pdf_filename: str) -> str:
    """Convenience function to generate unique candidate ID"""
    return candidate_id_generator.generate_unique_id(pdf_content, metadata, pdf_filename)

def create_candidate_identity(pdf_content: str, metadata: Dict[str, Any], 
                            pdf_filename: str) -> CandidateIdentity:
    """Convenience function to create candidate identity"""
    return candidate_id_generator.create_candidate_identity(pdf_content, metadata, pdf_filename)

if __name__ == "__main__":
    # Test the ID generator
    print("🧪 Testing Candidate ID Generator")
    print("=" * 40)
    
    # Test data
    test_cases = [
        {
            'content': 'Li Wei\nli.wei@email.com\n+123-456-7890\nSoftware Engineer\nReact, JavaScript',
            'metadata': {'candidate_name': 'Li Wei', 'email': 'li.wei@email.com', 'phone': '+123-456-7890'},
            'filename': 'resume_221_Li_Wei_Software_Engineering_Professional.pdf'
        },
        {
            'content': 'Li Wei\nli.wei.different@email.com\n+987-654-3210\nData Scientist\nPython, ML',
            'metadata': {'candidate_name': 'Li Wei', 'email': 'li.wei.different@email.com', 'phone': '+987-654-3210'},
            'filename': 'resume_363_Li_Wei_Data_Science_Professional.pdf'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        identity = create_candidate_identity(
            test_case['content'],
            test_case['metadata'],
            test_case['filename']
        )
        
        print(f"\n{i}. {identity.name}")
        print(f"   Unique ID: {identity.unique_id}")
        print(f"   Email: {identity.email}")
        print(f"   File: {identity.pdf_filename}")
    
    print(f"\n✅ Generated {len(test_cases)} unique IDs for candidates with same name")
