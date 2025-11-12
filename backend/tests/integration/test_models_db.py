"""Integration tests for database models."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from src.models.image import Image
from src.models.detection import Detection
from src.db.session import get_session_local


@pytest.mark.asyncio
async def test_create_image_in_database():
    """Test creating an Image record in the database."""
    async_session = get_session_local()
    
    async with async_session() as session:
        # Create image
        image = Image(
            filename="test_image.jpg",
            storage_path="2025/11/12/test_image.jpg",
            file_size=1024,
            status="pending",
            upload_timestamp=datetime.now(timezone.utc),
        )
        session.add(image)
        await session.commit()
        await session.refresh(image)
        
        # Verify it was saved
        assert image.id is not None
        assert image.filename == "test_image.jpg"
        assert image.created_at is not None
        
        # Clean up
        await session.delete(image)
        await session.commit()


@pytest.mark.asyncio
async def test_create_detection_with_image():
    """Test creating a Detection linked to an Image."""
    async_session = get_session_local()
    
    async with async_session() as session:
        # Create image
        image = Image(
            filename="test_detection.jpg",
            storage_path="2025/11/12/test_detection.jpg",
            file_size=2048,
            status="completed",
            upload_timestamp=datetime.now(timezone.utc),
        )
        session.add(image)
        await session.commit()
        await session.refresh(image)
        
        # Create detection
        detection = Detection(
            image_id=image.id,
            label="cat",
            confidence_score=0.95,
            bbox_xmin=10,
            bbox_ymin=20,
            bbox_xmax=100,
            bbox_ymax=200,
        )
        session.add(detection)
        await session.commit()
        await session.refresh(detection)
        
        # Verify detection
        assert detection.id is not None
        assert detection.image_id == image.id
        assert detection.label == "cat"
        assert detection.confidence_score == 0.95
        
        # Clean up
        await session.delete(detection)
        await session.delete(image)
        await session.commit()


@pytest.mark.asyncio
async def test_image_detection_relationship():
    """Test that Image-Detection relationship works."""
    async_session = get_session_local()
    
    async with async_session() as session:
        # Create image
        image = Image(
            filename="relationship_test.jpg",
            storage_path="2025/11/12/relationship_test.jpg",
            file_size=3072,
            status="completed",
            upload_timestamp=datetime.now(timezone.utc),
        )
        session.add(image)
        await session.commit()
        await session.refresh(image)
        
        # Create multiple detections
        detection1 = Detection(
            image_id=image.id,
            label="dog",
            confidence_score=0.90,
            bbox_xmin=0,
            bbox_ymin=0,
            bbox_xmax=50,
            bbox_ymax=50,
        )
        detection2 = Detection(
            image_id=image.id,
            label="cat",
            confidence_score=0.85,
            bbox_xmin=60,
            bbox_ymin=60,
            bbox_xmax=110,
            bbox_ymax=110,
        )
        session.add_all([detection1, detection2])
        await session.commit()
        
        # Query image with detections
        result = await session.execute(
            select(Image).where(Image.id == image.id)
        )
        loaded_image = result.scalar_one()
        
        # Access detections through relationship
        await session.refresh(loaded_image, ["detections"])
        assert len(loaded_image.detections) == 2
        assert {d.label for d in loaded_image.detections} == {"dog", "cat"}
        
        # Clean up
        for detection in loaded_image.detections:
            await session.delete(detection)
        await session.delete(loaded_image)
        await session.commit()


@pytest.mark.asyncio
async def test_cascade_delete():
    """Test that deleting image cascades to detections."""
    async_session = get_session_local()
    
    async with async_session() as session:
        # Create image with detection
        image = Image(
            filename="cascade_test.jpg",
            storage_path="2025/11/12/cascade_test.jpg",
            file_size=4096,
            status="completed",
            upload_timestamp=datetime.now(timezone.utc),
        )
        session.add(image)
        await session.commit()
        await session.refresh(image)
        
        detection = Detection(
            image_id=image.id,
            label="bird",
            confidence_score=0.88,
            bbox_xmin=20,
            bbox_ymin=30,
            bbox_xmax=80,
            bbox_ymax=90,
        )
        session.add(detection)
        await session.commit()
        detection_id = detection.id
        
        # Delete image
        await session.delete(image)
        await session.commit()
        
        # Verify detection was also deleted (cascade)
        result = await session.execute(
            select(Detection).where(Detection.id == detection_id)
        )
        assert result.scalar_one_or_none() is None
