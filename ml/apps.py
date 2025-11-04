from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class MlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml'
    verbose_name = 'Machine Learning'
    
    def ready(self):
        # Import here to avoid circular imports
        try:
            from ml.services.model_manager import ModelManager
            # Try to load model, but don't crash if it doesn't exist yet
            success = ModelManager.load_model()
            if not success:
                logger.info("No pre-trained model found. Train a model using: python manage.py train_model --model-version v1.0")
        except Exception as e:
            logger.warning(f"Could not load ML model on startup: {e}")
