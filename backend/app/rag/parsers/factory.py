"""Parser factory for selecting the appropriate document parser."""

from typing import Optional
import logging
from pathlib import Path

from app.rag.parsers.base import BaseParser
from app.rag.parsers.text_parser import TextParser
from app.rag.parsers.pdf_parser import PDFParser
from app.config import settings

logger = logging.getLogger(__name__)


class ParserFactory:
    """Factory for creating document parsers based on file type."""

    # Map file extensions to parser classes
    PARSER_MAP = {
        # Text formats
        '.txt': TextParser,
        '.md': TextParser,
        '.markdown': TextParser,
        '.rst': TextParser,

        # Code formats
        '.py': TextParser,
        '.js': TextParser,
        '.jsx': TextParser,
        '.ts': TextParser,
        '.tsx': TextParser,
        '.java': TextParser,
        '.cpp': TextParser,
        '.c': TextParser,
        '.h': TextParser,
        '.go': TextParser,
        '.rs': TextParser,
        '.rb': TextParser,
        '.php': TextParser,
        '.swift': TextParser,
        '.kt': TextParser,

        # Config formats
        '.json': TextParser,
        '.yaml': TextParser,
        '.yml': TextParser,
        '.toml': TextParser,
        '.ini': TextParser,
        '.conf': TextParser,
        '.xml': TextParser,

        # Web formats
        '.html': TextParser,
        '.css': TextParser,
        '.scss': TextParser,
        '.less': TextParser,

        # Document formats
        '.pdf': PDFParser,
    }

    @classmethod
    def get_parser(cls, filename: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> Optional[BaseParser]:
        """
        Get the appropriate parser for a file based on its extension.

        Args:
            filename: Name of the file
            chunk_size: Optional chunk size (uses config default if not provided)
            chunk_overlap: Optional chunk overlap (uses config default if not provided)

        Returns:
            Parser instance or None if file type not supported
        """
        # Get file extension
        extension = Path(filename).suffix.lower()

        # Get parser class
        parser_class = cls.PARSER_MAP.get(extension)

        if parser_class is None:
            logger.warning(f"No parser available for file type: {extension}")
            return None

        # Use config defaults if not provided
        chunk_size = chunk_size or settings.rag_chunk_size
        chunk_overlap = chunk_overlap or settings.rag_chunk_overlap

        # Create and return parser instance
        parser = parser_class(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        logger.debug(f"Created {parser_class.__name__} for {filename}")
        return parser

    @classmethod
    def is_supported(cls, filename: str) -> bool:
        """
        Check if a file type is supported.

        Args:
            filename: Name of the file

        Returns:
            True if supported, False otherwise
        """
        extension = Path(filename).suffix.lower()
        return extension in cls.PARSER_MAP

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """
        Get list of all supported file extensions.

        Returns:
            List of supported extensions
        """
        return list(cls.PARSER_MAP.keys())
