"""
Ollama service for LLM interactions.
"""
from typing import AsyncGenerator, List, Dict, Any, Optional
import ollama
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OllamaService:
    """Service for interacting with Ollama API."""

    def __init__(self):
        """Initialize Ollama client."""
        self.client = ollama.AsyncClient(host=settings.ollama_base_url)
        self.default_model = settings.ollama_default_model
        self.embedding_model = settings.ollama_embedding_model

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models from Ollama.

        Returns:
            List of model dictionaries

        Raises:
            Exception: If unable to connect to Ollama
        """
        try:
            response = await self.client.list()
            models = response.get('models', [])
            logger.info("Successfully fetched models from Ollama", count=len(models))
            return models
        except Exception as e:
            logger.error("Failed to fetch models from Ollama", error=str(e))
            raise

    async def check_connection(self) -> bool:
        """
        Check if Ollama is accessible.

        Returns:
            True if connection is successful
        """
        try:
            await self.list_models()
            return True
        except Exception as e:
            logger.error("Ollama connection check failed", error=str(e))
            return False

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AsyncGenerator[str, None] | Dict[str, Any]:
        """
        Send a chat request to Ollama.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to configured default)
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Yields:
            Response chunks if stream=True

        Returns:
            Complete response if stream=False
        """
        model = model or self.default_model

        options = {
            "temperature": temperature,
            "top_p": top_p,
        }
        if max_tokens:
            options["num_predict"] = max_tokens

        try:
            if stream:
                return self._stream_chat(messages, model, options)
            else:
                response = await self.client.chat(
                    model=model,
                    messages=messages,
                    options=options
                )
                logger.info(
                    "Chat completion successful",
                    model=model,
                    message_count=len(messages)
                )
                return response
        except Exception as e:
            logger.error(
                "Chat request failed",
                model=model,
                error=str(e),
                exc_info=True
            )
            raise

    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        options: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Internal method to handle streaming chat.

        Args:
            messages: List of message dictionaries
            model: Model to use
            options: Model options

        Yields:
            Response chunks
        """
        try:
            stream = await self.client.chat(
                model=model,
                messages=messages,
                options=options,
                stream=True
            )

            async for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']

            logger.info(
                "Streaming chat completed",
                model=model,
                message_count=len(messages)
            )
        except Exception as e:
            logger.error(
                "Streaming chat failed",
                model=model,
                error=str(e),
                exc_info=True
            )
            raise

    async def generate_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate embeddings for text.

        Args:
            text: Text to embed
            model: Embedding model to use (defaults to configured model)

        Returns:
            List of embedding values

        Raises:
            Exception: If embedding generation fails
        """
        model = model or self.embedding_model

        try:
            response = await self.client.embeddings(
                model=model,
                prompt=text
            )
            embedding = response.get('embedding', [])
            logger.debug("Generated embedding", model=model, dimension=len(embedding))
            return embedding
        except Exception as e:
            logger.error(
                "Embedding generation failed",
                model=model,
                error=str(e),
                exc_info=True
            )
            raise

    async def pull_model(self, model_name: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Pull a model from Ollama registry.

        Args:
            model_name: Name of the model to pull

        Yields:
            Progress updates
        """
        try:
            stream = await self.client.pull(model_name, stream=True)
            async for chunk in stream:
                yield chunk
            logger.info("Model pull completed", model=model_name)
        except Exception as e:
            logger.error("Model pull failed", model=model_name, error=str(e))
            raise

    async def delete_model(self, model_name: str) -> bool:
        """
        Delete a model from local Ollama.

        Args:
            model_name: Name of the model to delete

        Returns:
            True if deletion was successful

        Raises:
            Exception: If deletion fails
        """
        try:
            await self.client.delete(model_name)
            logger.info("Model deleted successfully", model=model_name)
            return True
        except Exception as e:
            logger.error("Model deletion failed", model=model_name, error=str(e))
            raise


# Global service instance
ollama_service = OllamaService()
