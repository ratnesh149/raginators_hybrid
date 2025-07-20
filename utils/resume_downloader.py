"""
Resume Download Utility
Handles downloading individual and bulk resume files for shortlisted candidates
"""

import os
import zipfile
import tempfile
import logging
import csv
import io
from pathlib import Path
from typing import List, Dict, Optional
import streamlit as st

logger = logging.getLogger(__name__)

class ResumeDownloader:
    """Utility class for handling resume downloads"""
    
    def __init__(self, sample_resumes_dir: str = "sample_resumes"):
        self.sample_resumes_dir = Path(sample_resumes_dir)
        
    def get_resume_file_path(self, candidate_info: Dict) -> Optional[str]:
        """Get the file path for a candidate's resume"""
        try:
            # Method 1: Use stored pdf_file_path from metadata
            if 'pdf_file_path' in candidate_info and candidate_info['pdf_file_path']:
                file_path = candidate_info['pdf_file_path']
                if os.path.exists(file_path):
                    return file_path
            
            # Method 2: Use stored pdf_filename from metadata
            if 'pdf_filename' in candidate_info and candidate_info['pdf_filename']:
                file_path = self.sample_resumes_dir / candidate_info['pdf_filename']
                if file_path.exists():
                    return str(file_path)
            
            # Method 3: Search by candidate name
            candidate_name = candidate_info.get('name', '').replace(' ', '_')
            if candidate_name:
                # Try exact match first
                for pdf_file in self.sample_resumes_dir.glob("*.pdf"):
                    if candidate_name.lower() in pdf_file.name.lower():
                        return str(pdf_file)
                
                # Try partial match
                name_parts = candidate_name.split('_')
                for pdf_file in self.sample_resumes_dir.glob("*.pdf"):
                    if any(part.lower() in pdf_file.name.lower() for part in name_parts if len(part) > 2):
                        return str(pdf_file)
            
            logger.warning(f"Resume file not found for candidate: {candidate_info.get('name', 'Unknown')}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting resume file path: {e}")
            return None
    
    def create_candidates_csv(self, candidates: List[Dict]) -> str:
        """Create a CSV file with candidate information"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = [
                'Rank', 'Name', 'Match Score', 'Email', 'Phone', 'Experience', 
                'Skills', 'Location', 'Education', 'Unique ID', 'Resume Available'
            ]
            writer.writerow(headers)
            
            # Write candidate data
            for i, candidate in enumerate(candidates, 1):
                file_path = self.get_resume_file_path(candidate)
                resume_available = "Yes" if (file_path and os.path.exists(file_path)) else "No"
                
                row = [
                    i,
                    candidate.get('name', 'Unknown'),
                    candidate.get('match_score', 'N/A'),
                    candidate.get('email', 'Not provided'),
                    candidate.get('phone', 'Not provided'),
                    candidate.get('experience', 'N/A'),
                    candidate.get('skills', 'Not specified')[:200],  # Truncate long skills
                    candidate.get('location', 'Not specified'),
                    candidate.get('education', 'Not specified'),
                    candidate.get('unique_id', 'N/A'),
                    resume_available
                ]
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating CSV: {e}")
            return ""
    
    def create_bulk_download_zip(self, candidates: List[Dict], zip_filename: str = "shortlisted_candidates_resumes.zip") -> Optional[str]:
        """Create a ZIP file containing all candidate resumes"""
        try:
            # Create temporary directory for ZIP file
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, zip_filename)
            
            successful_files = 0
            failed_files = []
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add candidate CSV file
                csv_content = self.create_candidates_csv(candidates)
                if csv_content:
                    zipf.writestr("candidates_list.csv", csv_content)
                
                # Add resume files
                for i, candidate in enumerate(candidates):
                    file_path = self.get_resume_file_path(candidate)
                    candidate_name = candidate.get('name', f'candidate_{i+1}')
                    
                    if file_path and os.path.exists(file_path):
                        try:
                            # Create a clean filename for the ZIP
                            clean_name = candidate_name.replace(' ', '_').replace('/', '_')
                            match_score = candidate.get('match_score', '0%').replace('%', '')
                            zip_filename_entry = f"{i+1:02d}_{clean_name}_match_{match_score}%_resume.pdf"
                            
                            zipf.write(file_path, zip_filename_entry)
                            successful_files += 1
                            logger.info(f"Added to ZIP: {candidate_name}")
                            
                        except Exception as e:
                            logger.error(f"Error adding {candidate_name} to ZIP: {e}")
                            failed_files.append(candidate_name)
                    else:
                        failed_files.append(candidate_name)
                        logger.warning(f"Resume file not found for: {candidate_name}")
                
                # Add a summary file to the ZIP
                summary_content = self._create_summary_content(candidates, successful_files, failed_files)
                zipf.writestr("SHORTLIST_SUMMARY.txt", summary_content)
            
            if successful_files > 0 or csv_content:  # Success if we have resumes OR CSV
                logger.info(f"ZIP created successfully with {successful_files} resumes and candidate list")
                return zip_path
            else:
                logger.error("No content was added to ZIP file")
                return None
                
        except Exception as e:
            logger.error(f"Error creating bulk download ZIP: {e}")
            return None
    
    def _create_summary_content(self, candidates: List[Dict], successful_files: int, failed_files: List[str]) -> str:
        """Create a summary content for the ZIP file"""
        summary = []
        summary.append("SHORTLISTED CANDIDATES SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Generated on: {st.session_state.get('search_timestamp', 'Unknown')}")
        summary.append(f"Total candidates: {len(candidates)}")
        summary.append(f"Resumes included: {successful_files}")
        summary.append(f"Resumes not found: {len(failed_files)}")
        summary.append("")
        
        summary.append("FILES INCLUDED:")
        summary.append("-" * 20)
        summary.append("• candidates_list.csv - Complete candidate information in spreadsheet format")
        summary.append("• Individual PDF resume files (when available)")
        summary.append("• This summary file")
        summary.append("")
        
        summary.append("CANDIDATE DETAILS:")
        summary.append("-" * 30)
        for i, candidate in enumerate(candidates, 1):
            summary.append(f"{i}. {candidate.get('name', 'Unknown')}")
            summary.append(f"   Match Score: {candidate.get('match_score', 'N/A')}")
            summary.append(f"   Experience: {candidate.get('experience', 'N/A')}")
            summary.append(f"   Email: {candidate.get('email', 'N/A')}")
            summary.append(f"   Phone: {candidate.get('phone', 'N/A')}")
            summary.append(f"   Skills: {candidate.get('skills', 'N/A')[:100]}...")
            summary.append("")
        
        if failed_files:
            summary.append("RESUMES NOT FOUND:")
            summary.append("-" * 25)
            for name in failed_files:
                summary.append(f"• {name}")
            summary.append("")
        
        summary.append("USAGE INSTRUCTIONS:")
        summary.append("-" * 25)
        summary.append("1. Open candidates_list.csv in Excel or Google Sheets for easy viewing")
        summary.append("2. Individual resume PDFs are numbered and named for easy identification")
        summary.append("3. Match scores indicate how well each candidate fits your requirements")
        summary.append("4. Contact candidates directly using the provided email/phone information")
        summary.append("")
        summary.append("NOTE: This package was automatically generated by the Resume Selection Assistant.")
        summary.append("All candidates have been deduplicated to ensure uniqueness.")
        
        return "\n".join(summary)
    
    def get_download_stats(self, candidates: List[Dict]) -> Dict:
        """Get statistics about downloadable resumes"""
        total_candidates = len(candidates)
        available_resumes = 0
        missing_resumes = []
        
        for candidate in candidates:
            file_path = self.get_resume_file_path(candidate)
            if file_path and os.path.exists(file_path):
                available_resumes += 1
            else:
                missing_resumes.append(candidate.get('name', 'Unknown'))
        
        return {
            'total_candidates': total_candidates,
            'available_resumes': available_resumes,
            'missing_resumes': missing_resumes,
            'availability_rate': (available_resumes / total_candidates * 100) if total_candidates > 0 else 0
        }

# Create global instance
resume_downloader = ResumeDownloader()
