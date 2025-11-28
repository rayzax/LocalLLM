"""
Settings API endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AppSettings
from app.config import settings as app_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SettingUpdate(BaseModel):
    """Setting update model."""
    key: str
    value: Any
    description: str = None


@router.get("")
async def get_all_settings(db: Session = Depends(get_db)):
    """
    Get all application settings.

    Returns:
        Dictionary of all settings
    """
    try:
        db_settings = db.query(AppSettings).all()

        # Combine with default config settings
        all_settings = {
            "ollama_base_url": app_settings.ollama_base_url,
            "ollama_default_model": app_settings.ollama_default_model,
            "ollama_embedding_model": app_settings.ollama_embedding_model,
            "rag_chunk_size": app_settings.rag_chunk_size,
            "rag_chunk_overlap": app_settings.rag_chunk_overlap,
            "rag_max_file_size_mb": app_settings.rag_max_file_size_mb,
            "rag_top_k_results": app_settings.rag_top_k_results,
            "indexed_directories": app_settings.indexed_directories_list,
            "excluded_patterns": app_settings.excluded_patterns_list,
            "duckduckgo_enabled": app_settings.duckduckgo_enabled,
            "max_search_results": app_settings.max_search_results,
        }

        # Override with database settings
        for setting in db_settings:
            all_settings[setting.key] = setting.value

        return {"settings": all_settings}
    except Exception as e:
        logger.error("Failed to get settings", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get settings")


@router.get("/{key}")
async def get_setting(key: str, db: Session = Depends(get_db)):
    """
    Get a specific setting by key.

    Args:
        key: Setting key
        db: Database session

    Returns:
        Setting value
    """
    try:
        setting = db.query(AppSettings).filter(AppSettings.key == key).first()
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")

        return {
            "key": setting.key,
            "value": setting.value,
            "description": setting.description,
            "updated_at": setting.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get setting", key=key, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get setting")


@router.post("")
async def update_setting(
    setting: SettingUpdate,
    db: Session = Depends(get_db)
):
    """
    Update or create a setting.

    Args:
        setting: Setting data
        db: Database session

    Returns:
        Updated setting
    """
    try:
        db_setting = db.query(AppSettings).filter(AppSettings.key == setting.key).first()

        if db_setting:
            db_setting.value = setting.value
            if setting.description:
                db_setting.description = setting.description
        else:
            db_setting = AppSettings(
                key=setting.key,
                value=setting.value,
                description=setting.description
            )
            db.add(db_setting)

        db.commit()
        db.refresh(db_setting)

        logger.info("Updated setting", key=setting.key)

        return {
            "key": db_setting.key,
            "value": db_setting.value,
            "description": db_setting.description,
            "updated_at": db_setting.updated_at.isoformat()
        }
    except Exception as e:
        logger.error("Failed to update setting", key=setting.key, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update setting")


@router.delete("/{key}")
async def delete_setting(key: str, db: Session = Depends(get_db)):
    """
    Delete a setting.

    Args:
        key: Setting key
        db: Database session

    Returns:
        Success message
    """
    try:
        setting = db.query(AppSettings).filter(AppSettings.key == key).first()
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")

        db.delete(setting)
        db.commit()

        logger.info("Deleted setting", key=key)
        return {"message": f"Setting '{key}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete setting", key=key, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete setting")
