"""
Chat API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, Message
from app.services.ollama_service import ollama_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Pydantic models for request/response
class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model."""
    conversation_id: Optional[int] = Field(None, description="Conversation ID (null for new)")
    message: str = Field(..., description="User message")
    model: Optional[str] = Field(None, description="Model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")
    stream: bool = Field(True, description="Stream the response")
    system_prompt: Optional[str] = Field(None, description="System prompt")


class ConversationCreate(BaseModel):
    """Create conversation model."""
    title: Optional[str] = Field("New Conversation", description="Conversation title")
    model: str = Field(..., description="Model to use")
    system_prompt: Optional[str] = Field(None, description="System prompt")


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: int
    title: str
    model: str
    created_at: str
    updated_at: str
    message_count: int

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Message response model."""
    id: int
    role: str
    content: str
    created_at: str
    token_count: int

    class Config:
        from_attributes = True


@router.get("/models")
async def get_models():
    """
    Get available Ollama models.

    Returns:
        List of available models
    """
    try:
        models = await ollama_service.list_models()
        return {"models": models}
    except Exception as e:
        logger.error("Failed to fetch models", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch models from Ollama")


@router.get("/health")
async def check_ollama_health():
    """
    Check Ollama connection health.

    Returns:
        Health status
    """
    is_healthy = await ollama_service.check_connection()
    if is_healthy:
        return {"status": "healthy", "ollama": "connected"}
    else:
        raise HTTPException(status_code=503, detail="Ollama is not accessible")


@router.post("/conversations")
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.

    Args:
        conversation: Conversation details
        db: Database session

    Returns:
        Created conversation
    """
    try:
        db_conversation = Conversation(
            title=conversation.title,
            model=conversation.model,
            system_prompt=conversation.system_prompt
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)

        logger.info("Created conversation", conversation_id=db_conversation.id)

        return {
            "id": db_conversation.id,
            "title": db_conversation.title,
            "model": db_conversation.model,
            "created_at": db_conversation.created_at.isoformat(),
            "updated_at": db_conversation.updated_at.isoformat(),
            "message_count": 0
        }
    except Exception as e:
        logger.error("Failed to create conversation", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/conversations")
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List all conversations.

    Args:
        skip: Number of conversations to skip
        limit: Maximum conversations to return
        db: Database session

    Returns:
        List of conversations
    """
    try:
        conversations = db.query(Conversation).filter(
            Conversation.is_archived == False
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

        return {
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "model": conv.model,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": len(conv.messages)
                }
                for conv in conversations
            ]
        }
    except Exception as e:
        logger.error("Failed to list conversations", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list conversations")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all messages in a conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        List of messages
    """
    try:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()

        return {
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "token_count": msg.token_count
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get messages", conversation_id=conversation_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get messages")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        Success message
    """
    try:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        db.delete(conversation)
        db.commit()

        logger.info("Deleted conversation", conversation_id=conversation_id)
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete conversation", conversation_id=conversation_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Send a chat message and get response.

    Args:
        request: Chat request
        db: Database session

    Returns:
        Chat response (streamed or complete)
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == request.conversation_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                model=request.model or ollama_service.default_model,
                system_prompt=request.system_prompt
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()

        # Build messages for Ollama
        messages = []
        if conversation.system_prompt or request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt or conversation.system_prompt
            })

        # Get conversation history
        history = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.asc()).all()

        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Get response from Ollama
        if request.stream:
            async def generate():
                full_response = ""
                try:
                    async for chunk in await ollama_service.chat(
                        messages=messages,
                        model=request.model or conversation.model,
                        temperature=request.temperature,
                        top_p=request.top_p,
                        max_tokens=request.max_tokens,
                        stream=True
                    ):
                        full_response += chunk
                        yield chunk

                    # Save assistant message
                    assistant_message = Message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=full_response,
                        temperature=request.temperature,
                        top_p=request.top_p,
                        max_tokens=request.max_tokens
                    )
                    db.add(assistant_message)
                    db.commit()
                except Exception as e:
                    logger.error("Streaming error", error=str(e))
                    yield f"\n\nError: {str(e)}"

            return StreamingResponse(generate(), media_type="text/plain")
        else:
            response = await ollama_service.chat(
                messages=messages,
                model=request.model or conversation.model,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens,
                stream=False
            )

            assistant_content = response['message']['content']

            # Save assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=assistant_content,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens
            )
            db.add(assistant_message)
            db.commit()

            return {
                "conversation_id": conversation.id,
                "message": assistant_content,
                "model": request.model or conversation.model
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Chat request failed", error=str(e), exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat request failed: {str(e)}")
