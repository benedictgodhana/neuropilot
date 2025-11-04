import torch
import json
import os
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    model = None
    current_version = None
    
    @classmethod
    def load_model(cls, version='current'):
        """Load model into memory"""
        try:
            print(f"Attempting to load model version: {version}")
            
            if version == 'current':
                model_path = settings.BASE_DIR / 'trained_models/current_model.pth'
                # Resolve symlink to get actual version
                if model_path.is_symlink():
                    actual_path = model_path.resolve()
                    version = actual_path.stem.replace('_model', '')
                    print(f"Resolved current to version: {version}")
            else:
                model_path = settings.BASE_DIR / f'trained_models/{version}_model.pth'
            
            print(f"Model path: {model_path}")
            print(f"Path exists: {model_path.exists()}")
            
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                return False
            
            # Import here to avoid circular imports
            from ml.ml_models.neuropilot_model import create_model
            
            # Create model instance
            cls.model = create_model(num_commands=20, input_size=4)
            print("Model architecture created")
            
            # Load the trained weights
            state_dict = torch.load(model_path, map_location=torch.device('cpu'))
            print("State dict loaded successfully")
            
            cls.model.load_state_dict(state_dict)
            cls.model.eval()  # Call eval on the model, not the state_dict!
            
            cls.current_version = version
            
            print(f"Model {version} loaded successfully!")
            logger.info(f"Model {version} loaded successfully")
            return True
            
        except Exception as e:
            print(f"ERROR loading model: {e}")
            logger.error(f"Error loading model: {e}")
            return False
    
    @classmethod
    def save_model(cls, model, version):
        """Save trained model"""
        try:
            model_dir = settings.BASE_DIR / 'trained_models'
            model_dir.mkdir(exist_ok=True)
            
            model_path = model_dir / f'{version}_model.pth'
            
            # Save only the state dict (recommended)
            torch.save(model.state_dict(), model_path)
            print(f"Model saved to: {model_path}")
            
            # Create/update current symlink
            current_path = model_dir / 'current_model.pth'
            if current_path.exists():
                current_path.unlink()
            
            # Create symlink to the current version
            os.symlink(f'{version}_model.pth', current_path)
            print(f"Created symlink: {current_path} -> {version}_model.pth")
            
            logger.info(f"Model saved as version {version}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    @classmethod
    def get_model(cls):
        """Get the current loaded model"""
        return cls.model
    
    @classmethod
    def is_model_loaded(cls):
        """Check if model is loaded"""
        return cls.model is not None
