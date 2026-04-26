"""
PDF Processor Module
Extracts and cleans text from PDF files
(FULL UPDATED VERSION WITH SUBFOLDER SUPPORT)
"""

import os
import pdfplumber
import re
from pathlib import Path
from typing import List, Dict


class PDFProcessor:
    """
    Simple PDF text extraction and cleaning
    """
    
    def __init__(self, pdf_folder_path: str):
        """
        Initialize PDF processor with folder path
        
        Args:
            pdf_folder_path: Path to folder containing PDFs
        """
        self.pdf_folder_path = pdf_folder_path
        self.extracted_data = []
    
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a single PDF file
        
        Args:
            pdf_path: Full path to PDF file
            
        Returns:
            Extracted text string
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num} ---\n"
                        text += page_text
            
            return text
        
        except Exception as e:
            print(f"❌ Error reading {pdf_path}: {e}")
            return ""
    
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text from PDFs
        Remove junk, extra spaces, special characters
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special unwanted characters but keep punctuation
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        
        return text.strip()
    
    
    def process_all_pdfs(self) -> List[Dict]:
        """
        🔥 UPDATED:
        - Reads ALL PDFs from folder + subfolders
        - Fix for Diseases folder issue
        """
        print("\n" + "="*70)
        print(f"📂 Scanning folder: {self.pdf_folder_path}")
        print("="*70)

        pdf_files = []

        # 🔥 FULL RECURSIVE SEARCH (FIX)
        for root, dirs, files in os.walk(self.pdf_folder_path):
            print(f"\n📁 Checking Folder: {root}")
            
            for file in files:
                # Case-insensitive check
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(root, file)
                    print(f"✅ FOUND PDF: {full_path}")
                    pdf_files.append(Path(full_path))
        
        if not pdf_files:
            print(f"\n⚠️ No PDF files found in {self.pdf_folder_path}")
            return []
        
        print(f"\n🔥 TOTAL PDFs FOUND: {len(pdf_files)}")
        
        results = []
        for pdf_file in pdf_files:
            print(f"\n📖 Processing: {pdf_file.name}")
            
            # Extract text
            raw_text = self.extract_text_from_pdf(str(pdf_file))
            
            # Clean text
            cleaned_text = self.clean_text(raw_text)
            
            if not cleaned_text:
                print("⚠️ Skipped empty PDF")
                continue
            
            results.append({
                "filename": pdf_file.name,
                "filepath": str(pdf_file),  # 🔥 added for debugging
                "raw_text": raw_text,
                "cleaned_text": cleaned_text
            })
            
            print(f"✅ Extracted {len(cleaned_text)} characters")
        
        self.extracted_data = results
        return results
    
    
    def get_combined_text(self) -> str:
        """
        Get all extracted and cleaned text combined
        
        Returns:
            Combined text from all PDFs
        """
        combined = ""
        for item in self.extracted_data:
            combined += item["cleaned_text"] + "\n\n"
        
        return combined


# Example usage (for testing)
if __name__ == "__main__":
    print("\n🚀 TESTING PDF PROCESSOR\n")

    # 🔥 IMPORTANT: Give MAIN folder (DATA)
    processor = PDFProcessor(r"C:\Bhoomi-RAG-PAH\DATA")

    results = processor.process_all_pdfs()
    
    if results:
        print("\n✅ Processing complete!")
        print(f"Processed {len(results)} file(s)")
    else:
        print("\n❌ No files processed!")