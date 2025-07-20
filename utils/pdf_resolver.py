"""
Smart PDF Resolution Utility
Handles multiple candidates with same name using fuzzy matching and content analysis
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
import hashlib
from services.enhanced_pdf_processor import enhanced_pdf_processor

logger = logging.getLogger(__name__)

class SmartPDFResolver:
    """
    Smart PDF resolver to handle cases where multiple candidates have similar names
    or when we need to find the best matching PDF for a candidate
    """
    
    def __init__(self, sample_resumes_path: str = "sample_resumes"):
        self.sample_resumes_path = Path(sample_resumes_path)
        self._pdf_cache = {}  # Cache for PDF content to avoid re-reading
        
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names"""
        name1_clean = name1.lower().strip().replace('_', ' ')
        name2_clean = name2.lower().strip().replace('_', ' ')
        return SequenceMatcher(None, name1_clean, name2_clean).ratio()
    
    def _extract_name_from_filename(self, filename: str) -> str:
        """Extract candidate name from PDF filename"""
        # Handle different filename patterns
        stem = Path(filename).stem
        
        # Pattern 1: Resume_Software_John_Doe.pdf -> John Doe
        parts = stem.split('_')
        if len(parts) >= 4 and parts[0].lower() == 'resume':
            return f"{parts[2]} {parts[3]}"
        
        # Pattern 2: John_Doe_Resume.pdf -> John Doe
        if len(parts) >= 2:
            # Take first two parts as name if they don't contain common resume words
            resume_words = {'resume', 'cv', 'curriculum', 'vitae'}
            if not any(word in parts[0].lower() for word in resume_words):
                return f"{parts[0]} {parts[1]}"
        
        # Pattern 3: JohnDoe.pdf -> John Doe (camelCase)
        if stem.isalpha() and any(c.isupper() for c in stem[1:]):
            # Split camelCase
            result = []
            current = stem[0]
            for char in stem[1:]:
                if char.isupper():
                    result.append(current)
                    current = char
                else:
                    current += char
            result.append(current)
            return ' '.join(result)
        
        # Default: replace underscores with spaces and title case
        return stem.replace('_', ' ').title()
    
    def _get_pdf_content_hash(self, pdf_path: Path) -> str:
        """Get a hash of PDF content for comparison"""
        if str(pdf_path) in self._pdf_cache:
            return self._pdf_cache[str(pdf_path)]['hash']
        
        try:
            content = enhanced_pdf_processor.extract_resume_content(str(pdf_path))
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            self._pdf_cache[str(pdf_path)] = {
                'content': content,
                'hash': content_hash
            }
            
            return content_hash
        except Exception as e:
            logger.warning(f"Could not extract content from {pdf_path}: {e}")
            return ""
    
    def find_matching_pdfs(self, candidate_name: str, similarity_threshold: float = 0.7) -> List[Dict]:
        """
        Find all PDF files that could match the given candidate name
        Returns list of matches with similarity scores
        """
        if not self.sample_resumes_path.exists():
            logger.warning(f"Sample resumes path does not exist: {self.sample_resumes_path}")
            return []
        
        matches = []
        pdf_files = list(self.sample_resumes_path.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            # Extract name from filename
            extracted_name = self._extract_name_from_filename(pdf_file.name)
            
            # Calculate similarity
            similarity = self._calculate_name_similarity(candidate_name, extracted_name)
            
            if similarity >= similarity_threshold:
                matches.append({
                    'pdf_path': pdf_file,
                    'pdf_filename': pdf_file.name,
                    'extracted_name': extracted_name,
                    'similarity_score': similarity,
                    'file_size': pdf_file.stat().st_size,
                    'content_hash': self._get_pdf_content_hash(pdf_file)
                })
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        logger.info(f"Found {len(matches)} PDF matches for '{candidate_name}'")
        return matches
    
    def resolve_best_pdf(self, candidate_name: str, 
                        additional_context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Find the best matching PDF for a candidate name
        Uses additional context like email, phone, skills if provided
        """
        matches = self.find_matching_pdfs(candidate_name)
        
        if not matches:
            logger.warning(f"No PDF matches found for candidate: {candidate_name}")
            return None
        
        if len(matches) == 1:
            logger.info(f"Single PDF match found for {candidate_name}: {matches[0]['pdf_filename']}")
            return matches[0]
        
        # Multiple matches - use additional context to resolve
        if additional_context:
            best_match = self._resolve_with_context(matches, additional_context)
            if best_match:
                return best_match
        
        # Fallback: return the highest similarity match
        best_match = matches[0]
        logger.info(f"Multiple matches for {candidate_name}, selecting best: {best_match['pdf_filename']} (similarity: {best_match['similarity_score']:.2f})")
        
        return best_match
    
    def _resolve_with_context(self, matches: List[Dict], context: Dict) -> Optional[Dict]:
        """Resolve multiple matches using additional context"""
        
        context_email = context.get('email', '').lower()
        context_phone = context.get('phone', '')
        context_skills = context.get('skills', [])
        
        if isinstance(context_skills, str):
            context_skills = [skill.strip() for skill in context_skills.split(',')]
        
        scored_matches = []
        
        for match in matches:
            score = match['similarity_score']  # Base score from name similarity
            
            # Get PDF content for context matching
            pdf_path = match['pdf_path']
            try:
                if str(pdf_path) in self._pdf_cache:
                    content = self._pdf_cache[str(pdf_path)]['content']
                else:
                    content = enhanced_pdf_processor.extract_resume_content(str(pdf_path))
                    self._pdf_cache[str(pdf_path)] = {
                        'content': content,
                        'hash': hashlib.md5(content.encode()).hexdigest()
                    }
                
                content_lower = content.lower()
                
                # Boost score if email matches
                if context_email and context_email in content_lower:
                    score += 0.3
                    logger.debug(f"Email match boost for {match['pdf_filename']}")
                
                # Boost score if phone matches
                if context_phone and context_phone in content:
                    score += 0.2
                    logger.debug(f"Phone match boost for {match['pdf_filename']}")
                
                # Boost score based on skill matches
                if context_skills:
                    skill_matches = sum(1 for skill in context_skills 
                                      if skill.lower() in content_lower)
                    skill_boost = (skill_matches / len(context_skills)) * 0.2
                    score += skill_boost
                    if skill_boost > 0:
                        logger.debug(f"Skills match boost for {match['pdf_filename']}: {skill_boost:.2f}")
                
            except Exception as e:
                logger.warning(f"Could not analyze content for {match['pdf_filename']}: {e}")
            
            scored_matches.append({
                **match,
                'context_score': score
            })
        
        # Sort by context score
        scored_matches.sort(key=lambda x: x['context_score'], reverse=True)
        
        best_match = scored_matches[0]
        logger.info(f"Context-resolved best match for candidate: {best_match['pdf_filename']} (context score: {best_match['context_score']:.2f})")
        
        return best_match
    
    def detect_duplicate_pdfs(self) -> List[List[Dict]]:
        """
        Detect potential duplicate PDF files based on content similarity
        Returns groups of potentially duplicate files
        """
        if not self.sample_resumes_path.exists():
            return []
        
        pdf_files = list(self.sample_resumes_path.glob("*.pdf"))
        content_groups = {}
        
        # Group PDFs by content hash
        for pdf_file in pdf_files:
            content_hash = self._get_pdf_content_hash(pdf_file)
            if content_hash:
                if content_hash not in content_groups:
                    content_groups[content_hash] = []
                content_groups[content_hash].append({
                    'pdf_path': pdf_file,
                    'pdf_filename': pdf_file.name,
                    'extracted_name': self._extract_name_from_filename(pdf_file.name),
                    'file_size': pdf_file.stat().st_size
                })
        
        # Return groups with more than one file (potential duplicates)
        duplicate_groups = [group for group in content_groups.values() if len(group) > 1]
        
        if duplicate_groups:
            logger.info(f"Found {len(duplicate_groups)} groups of potentially duplicate PDFs")
        
        return duplicate_groups
    
    def get_pdf_info(self, pdf_filename: str) -> Optional[Dict]:
        """Get detailed information about a specific PDF file"""
        pdf_path = self.sample_resumes_path / pdf_filename
        
        if not pdf_path.exists():
            return None
        
        return {
            'pdf_path': pdf_path,
            'pdf_filename': pdf_filename,
            'extracted_name': self._extract_name_from_filename(pdf_filename),
            'file_size': pdf_path.stat().st_size,
            'content_hash': self._get_pdf_content_hash(pdf_path),
            'last_modified': pdf_path.stat().st_mtime
        }

# Global instance
smart_pdf_resolver = SmartPDFResolver()
