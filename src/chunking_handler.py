"""
Text Chunking Module
Splits large text into smaller, manageable chunks
"""

from typing import List, Dict
import re


class TextChunker:
    """
    Splits text into chunks with optional overlap
    """
    
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        """
        Initialize chunker
        
        Args:
            chunk_size: Characters per chunk (default: 800)
            overlap: Characters to overlap between chunks (default: 100)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    
    def split_into_chunks(self, text: str, source_name: str = "unknown") -> List[Dict]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to split
            source_name: Name of source (PDF name)
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        
        # Split by sentences first (better than arbitrary splits)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            # Add sentence to current chunk
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += " " + sentence
            else:
                # Current chunk is full, save it
                if current_chunk.strip():
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": current_chunk.strip(),
                        "source": source_name,
                        "char_count": len(current_chunk)
                    })
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    current_chunk = current_chunk[-self.overlap:] + " " + sentence
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "source": source_name,
                "char_count": len(current_chunk)
            })
        
        return chunks
    
    
    def chunk_multiple_documents(self, 
                                 documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of docs from PDFProcessor
                      [{"filename": "...", "cleaned_text": "..."}, ...]
            
        Returns:
            Combined list of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            print(f"📦 Chunking: {doc['filename']}")
            
            chunks = self.split_into_chunks(
                doc['cleaned_text'],
                doc['filename']
            )
            
            all_chunks.extend(chunks)
            print(f"   ✅ Created {len(chunks)} chunks")
        
        return all_chunks
    
    
    def print_chunk_stats(self, chunks: List[Dict]):
        """
        Print statistics about chunks
        """
        print(f"\n📊 Chunking Statistics:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Avg chunk size: {sum(c['char_count'] for c in chunks) / len(chunks):.0f} chars")
        print(f"   Min chunk size: {min(c['char_count'] for c in chunks)} chars")
        print(f"   Max chunk size: {max(c['char_count'] for c in chunks)} chars")


# Example usage
if __name__ == "__main__":
    from .pdf_processor import PDFProcessor
    
    # Extract PDFs
    processor = PDFProcessor(r"D:\Pune_Agri_Hackathon\RAG\DATA\RICE\Crop_life_cycle_data")
    extracted_docs = processor.process_all_pdfs()
    
    # Chunk them
    chunker = TextChunker(chunk_size=800, overlap=100)
    chunks = chunker.chunk_multiple_documents(extracted_docs)
    
    # Show stats
    chunker.print_chunk_stats(chunks)
    
    # Show first chunk as example
    if chunks:
        print(f"\n📄 Sample chunk:")
        print(f"   Source: {chunks[0]['source']}")
        print(f"   Text: {chunks[0]['text'][:200]}...")