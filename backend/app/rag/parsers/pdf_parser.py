"""Parser for PDF files."""

from typing import List
import logging

from app.rag.parsers.base import BaseParser, DocumentChunk

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """Parser for PDF files using pypdf."""

    async def parse(self, file_path: str, file_id: int, filename: str) -> List[DocumentChunk]:
        """
        Parse a PDF file into chunks.

        Args:
            file_path: Path to the PDF file
            file_id: Database ID of the file
            filename: Original filename

        Returns:
            List of DocumentChunk objects
        """
        try:
            import pypdf

            # Read PDF
            with open(file_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)

                # Extract text from all pages
                text_parts = []
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)

                full_text = '\n\n'.join(text_parts)

            # Chunk the text
            chunks = self.chunk_text(full_text, file_id, filename)

            logger.info(f"Parsed PDF '{filename}' ({len(pdf_reader.pages)} pages) into {len(chunks)} chunks")
            return chunks

        except ImportError:
            logger.error("pypdf not installed. Install with: pip install pypdf")
            raise

        except Exception as e:
            logger.error(f"Error parsing PDF file '{filename}': {e}")
            raise
