"""Base document parser interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document."""
    text: str
    metadata: Dict[str, Any]
    chunk_id: int


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize parser with chunking parameters.

        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    async def parse(self, file_path: str, file_id: int, filename: str) -> List[DocumentChunk]:
        """
        Parse a document into chunks.

        Args:
            file_path: Path to the file
            file_id: Database ID of the file
            filename: Original filename

        Returns:
            List of DocumentChunk objects
        """
        pass

    def chunk_text(self, text: str, file_id: int, filename: str) -> List[DocumentChunk]:
        """
        Split text into chunks with overlap.

        Args:
            text: Full text to chunk
            file_id: Database ID of the file
            filename: Original filename

        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # Try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence end
                last_period = chunk_text.rfind('.')
                last_question = chunk_text.rfind('?')
                last_exclamation = chunk_text.rfind('!')
                sentence_end = max(last_period, last_question, last_exclamation)

                if sentence_end > self.chunk_size * 0.5:  # At least 50% through
                    chunk_text = chunk_text[:sentence_end + 1]
                else:
                    # Fall back to word boundary
                    last_space = chunk_text.rfind(' ')
                    if last_space > 0:
                        chunk_text = chunk_text[:last_space]

            chunk = DocumentChunk(
                text=chunk_text.strip(),
                metadata={
                    'file_id': file_id,
                    'filename': filename,
                    'chunk_id': chunk_id,
                    'start': start,
                    'end': start + len(chunk_text)
                },
                chunk_id=chunk_id
            )
            chunks.append(chunk)

            # Move to next chunk with overlap
            start += len(chunk_text) - self.chunk_overlap
            chunk_id += 1

        return chunks
