"""ML model loader with singleton pattern for caching loaded models."""

import logging
import time
from typing import Any, Optional

from transformers import pipeline
import torch
from PIL import Image
import io

from ..core.config import get_settings


logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Singleton class for loading and caching ML models.
    
    Ensures model is loaded only once and reused across requests.
    Uses Hugging Face Transformers pipeline for object detection.
    """

    _instance: Optional["ModelLoader"] = None
    _model: Optional[Any] = None
    _model_loaded: bool = False

    def __new__(cls) -> "ModelLoader":
        """
        Implement singleton pattern.
        
        Returns:
            Single instance of ModelLoader
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("ModelLoader instance created")
        return cls._instance

    def load_model(self) -> None:
        """
        Load the object detection model from Hugging Face.
        
        Downloads model if needed and caches it locally.
        Only loads once - subsequent calls return immediately.
        
        Raises:
            RuntimeError: If model fails to load
        """
        if self._model_loaded and self._model is not None:
            logger.debug("Model already loaded, skipping")
            return

        try:
            settings = get_settings()
            logger.info(f"Loading model: {settings.MODEL_NAME}")
            start_time = time.time()

            # Determine device
            device = 0 if torch.cuda.is_available() else -1
            device_name = "GPU" if device == 0 else "CPU"
            logger.info(f"Using device: {device_name}")

            # Load model pipeline
            self._model = pipeline(
                task="object-detection",
                model=settings.MODEL_NAME,
                device=device,
                model_kwargs={"cache_dir": str(settings.model_cache_path)},
            )

            load_time = time.time() - start_time
            self._model_loaded = True
            
            logger.info(
                f"Model loaded successfully in {load_time:.2f}s "
                f"(device: {device_name})"
            )

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._model = None
            self._model_loaded = False
            raise RuntimeError(f"Could not load ML model: {e}") from e

    def get_model(self) -> Any:
        """
        Get the loaded model instance.
        
        Loads model if not already loaded.
        
        Returns:
            Hugging Face pipeline object for object detection
            
        Raises:
            RuntimeError: If model fails to load
        """
        if not self._model_loaded:
            self.load_model()
        
        if self._model is None:
            raise RuntimeError("Model failed to load")
        
        return self._model

    def warmup(self) -> None:
        """
        Warm up model by running dummy inference.
        
        Helps reduce latency on first real request by pre-loading
        model weights into memory and initializing inference pipeline.
        """
        try:
            logger.info("Warming up model with dummy inference...")
            start_time = time.time()

            # Create a small dummy RGB image (100x100 pixels, white)
            dummy_image = Image.new("RGB", (100, 100), color="white")
            
            # Run inference
            model = self.get_model()
            _ = model(dummy_image)
            
            warmup_time = time.time() - start_time
            logger.info(f"Model warmup completed in {warmup_time:.2f}s")

        except Exception as e:
            logger.warning(f"Model warmup failed: {e}")
            # Don't raise - warmup is optional optimization

    def is_loaded(self) -> bool:
        """
        Check if model is currently loaded.
        
        Returns:
            True if model is loaded and ready, False otherwise
        """
        return self._model_loaded and self._model is not None

    def unload_model(self) -> None:
        """
        Unload model from memory.
        
        Useful for testing or freeing memory.
        In production, model should stay loaded.
        """
        if self._model is not None:
            logger.info("Unloading model from memory")
            self._model = None
            self._model_loaded = False
            
            # Force garbage collection to free memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
