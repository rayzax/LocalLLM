"""Parser for plain text files (.txt, .md, .py, .js, etc.)."""

from typing import List
import aiofiles
import logging

from app.rag.parsers.base import BaseParser, DocumentChunk

logger = logging.getLogger(__name__)


class TextParser(BaseParser):
    """Parser for plain text files."""

    async def parse(self, file_path: str, file_id: int, filename: str) -> List[DocumentChunk]:
        """
        Parse a text file into chunks.

        Args:
            file_path: Path to the text file
            file_id: Database ID of the file
            filename: Original filename

        Returns:
            List of DocumentChunk objects
        """
        try:
            # Read file content
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = await f.read()

            # Chunk the text
            chunks = self.chunk_text(text, file_id, filename)

            logger.info(f"Parsed text file '{filename}' into {len(chunks)} chunks")
            return chunks

        except Exception as e:
            logger.error(f"Error parsing text file '{filename}': {e}")
            raise
