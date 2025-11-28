"""Vector database service using ChromaDB for document embeddings and search."""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import hashlib
import logging

from app.config import get_settings
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorService:
    """Service for managing vector embeddings and similarity search using ChromaDB."""

    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.Client(Settings(
            persist_directory=settings.chromadb_path,
            anonymized_telemetry=False
        ))
        self.ollama_service = OllamaService()
        self.collection_name = "documents"

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for RAG"}
            )
            logger.info(f"Created new collection: {self.collection_name}")

    def _generate_id(self, text: str, metadata: Dict[str, Any]) -> str:
        """Generate a unique ID for a document chunk."""
        # Use hash of content + file_id to create unique ID
        content_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        file_id = metadata.get('file_id', 'unknown')
        chunk_id = metadata.get('chunk_id', 0)
        return f"{file_id}_{chunk_id}_{content_hash}"

    async def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        file_id: int
    ) -> Dict[str, Any]:
        """
        Add document chunks to the vector store with embeddings.

        Args:
            texts: List of text chunks to embed
            metadatas: List of metadata dicts for each chunk
            file_id: Database ID of the file

        Returns:
            Dict with count of added documents
        """
        try:
            # Generate embeddings using Ollama
            embeddings = []
            for text in texts:
                embedding = await self.ollama_service.generate_embedding(text)
                embeddings.append(embedding)

            # Generate unique IDs for each chunk
            ids = [self._generate_id(text, meta) for text, meta in zip(texts, metadatas)]

            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(texts)} chunks for file_id={file_id} to vector store")

            return {
                "added": len(texts),
                "file_id": file_id,
                "chunks": len(texts)
            }

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    async def search(
        self,
        query: str,
        n_results: int = 5,
        file_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity.

        Args:
            query: Search query text
            n_results: Number of results to return
            file_ids: Optional list of file IDs to filter by

        Returns:
            List of dicts with 'content', 'metadata', and 'distance'
        """
        try:
            # Generate embedding for query
            query_embedding = await self.ollama_service.generate_embedding(query)

            # Build where clause for filtering
            where_clause = None
            if file_ids:
                where_clause = {"file_id": {"$in": file_ids}}

            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause
            )

            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })

            logger.info(f"Vector search for '{query[:50]}...' returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise

    def delete_file_chunks(self, file_id: int) -> Dict[str, Any]:
        """
        Delete all chunks associated with a file.

        Args:
            file_id: Database ID of the file

        Returns:
            Dict with deletion status
        """
        try:
            # Query for all chunks with this file_id
            results = self.collection.get(
                where={"file_id": file_id}
            )

            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for file_id={file_id}")
                return {"deleted": len(results['ids']), "file_id": file_id}
            else:
                logger.info(f"No chunks found for file_id={file_id}")
                return {"deleted": 0, "file_id": file_id}

        except Exception as e:
            logger.error(f"Error deleting file chunks: {e}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection."""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            raise


# Singleton instance
vector_service = VectorService()
