"""RAG (Retrieval Augmented Generation) API endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
import logging
from pathlib import Path

from app.database import get_db
from app.models import File as FileModel
from app.services.vector_service import vector_service
from app.rag.parsers.factory import ParserFactory
from app.config import settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])

# Upload directory
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Request/Response models
class SearchRequest(BaseModel):
    """RAG search request."""
    query: str
    n_results: int = 5
    file_ids: Optional[List[int]] = None


class SearchResult(BaseModel):
    """Single search result."""
    content: str
    filename: str
    chunk_id: int
    distance: Optional[float]


class FileInfo(BaseModel):
    """File information response."""
    id: int
    filename: str
    file_type: str
    file_size: int
    chunks_count: int
    uploaded_at: str


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and index a file for RAG.

    Supports: PDF, TXT, MD, code files, and more.
    """
    try:
        # Validate file size
        max_size = settings.max_upload_size_mb * 1024 * 1024
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start

        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_upload_size_mb} MB"
            )

        # Check if file type is supported
        if not ParserFactory.is_supported(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Supported: {', '.join(ParserFactory.get_supported_extensions())}"
            )

        # Save file to disk
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create database record
        db_file = FileModel(
            filename=file.filename,
            file_type=Path(file.filename).suffix.lower(),
            file_size=file_size,
            file_path=str(file_path),
            indexed=False
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        # Parse and chunk document
        parser = ParserFactory.get_parser(file.filename)
        chunks = await parser.parse(str(file_path), db_file.id, file.filename)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract text from file"
            )

        # Prepare data for vector store
        texts = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # Add to vector store
        result = await vector_service.add_documents(texts, metadatas, db_file.id)

        # Update database record
        db_file.indexed = True
        db_file.chunks_count = len(chunks)
        db.commit()

        logger.info(f"Successfully indexed file: {file.filename} with {len(chunks)} chunks")

        return {
            "id": db_file.id,
            "filename": file.filename,
            "file_size": file_size,
            "chunks": len(chunks),
            "indexed": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    """
    Search indexed documents using vector similarity.

    Returns relevant chunks from uploaded documents.
    """
    try:
        # Search vector store
        results = await vector_service.search(
            query=request.query,
            n_results=request.n_results,
            file_ids=request.file_ids
        )

        # Format results
        formatted_results = [
            SearchResult(
                content=r['content'],
                filename=r['metadata'].get('filename', 'unknown'),
                chunk_id=r['metadata'].get('chunk_id', 0),
                distance=r.get('distance')
            )
            for r in results
        ]

        return formatted_results

    except Exception as e:
        logger.error(f"Error searching documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files", response_model=List[FileInfo])
async def list_files(db: Session = Depends(get_db)):
    """List all uploaded and indexed files."""
    try:
        files = db.query(FileModel).order_by(FileModel.uploaded_at.desc()).all()

        return [
            FileInfo(
                id=f.id,
                filename=f.filename,
                file_type=f.file_type,
                file_size=f.file_size,
                chunks_count=f.chunks_count or 0,
                uploaded_at=f.uploaded_at.isoformat() if f.uploaded_at else ""
            )
            for f in files
        ]

    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Delete a file and its vector embeddings."""
    try:
        # Get file from database
        db_file = db.query(FileModel).filter(FileModel.id == file_id).first()

        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")

        # Delete from vector store
        vector_service.delete_file_chunks(file_id)

        # Delete physical file
        if os.path.exists(db_file.file_path):
            os.remove(db_file.file_path)

        # Delete from database
        db.delete(db_file)
        db.commit()

        logger.info(f"Deleted file: {db_file.filename} (id={file_id})")

        return {"message": "File deleted successfully", "id": file_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get RAG system statistics."""
    try:
        # Database stats
        total_files = db.query(FileModel).count()
        indexed_files = db.query(FileModel).filter(FileModel.indexed == True).count()
        total_size = db.query(FileModel).with_entities(
            db.func.sum(FileModel.file_size)
        ).scalar() or 0

        # Vector store stats
        vector_stats = vector_service.get_collection_stats()

        return {
            "files": {
                "total": total_files,
                "indexed": indexed_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            },
            "vector_store": vector_stats,
            "supported_formats": ParserFactory.get_supported_extensions()
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
