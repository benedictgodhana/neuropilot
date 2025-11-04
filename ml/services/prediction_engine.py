import torch
import numpy as np
import logging
from collections import deque
from django.conf import settings
from ml.services.model_manager import ModelManager

logger = logging.getLogger(__name__)

class PredictionEngine:
    _instance = None
    
    def __init__(self):
        self.model = None
        self.is_loaded = False
        self.prediction_buffer = deque(maxlen=15)
        print("PredictionEngine initialized - attempting to load model...")
        self._try_load_model()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            print("Creating new PredictionEngine instance...")
            cls._instance = PredictionEngine()
        else:
            print("Returning existing PredictionEngine instance")
        return cls._instance
    
    def _try_load_model(self):
        """Try to load model on initialization"""
        try:
            print("Attempting to load model in PredictionEngine...")
            self.is_loaded = ModelManager.load_model('current')
            if self.is_loaded:
                self.model = ModelManager.get_model()
                print(f"✅ Model loaded in PredictionEngine: {self.model is not None}")
                logger.info("Neuropilot model loaded successfully in PredictionEngine")
            else:
                print("❌ Model failed to load in PredictionEngine")
        except Exception as e:
            print(f"❌ ERROR in PredictionEngine model loading: {e}")
            logger.error(f"Failed to load model in PredictionEngine: {e}")
            self.is_loaded = False
    
    def predict_hesitation(self, interaction_data):
        """Predict if user is hesitating"""
        print(f"📊 Prediction called - Model loaded: {self.is_loaded}")
        print(f"📊 ModelManager model: {ModelManager.get_model() is not None}")
        
        if not self.is_loaded:
            print("🔄 Model not loaded, attempting to load...")
            self._try_load_model()
            if not self.is_loaded:
                print("❌ Still no model available, returning defaults")
                return {'hesitation': False, 'confidence': 0.0, 'suggested_commands': []}
        
        try:
            print("🔍 Extracting features...")
            features = self._extract_features(interaction_data)
            print(f"📈 Features shape: {features.shape}")
            
            with torch.no_grad():
                print("🧠 Running model prediction...")
                prediction = self.model(features)
                print(f"📊 Raw prediction: {prediction}")
            
            formatted = self._format_prediction(prediction)
            print(f"🎯 Formatted prediction: {formatted}")
            return formatted
            
        except Exception as e:
            print(f"💥 Prediction error: {e}")
            logger.error(f"Prediction failed: {e}")
            return {'hesitation': False, 'confidence': 0.0, 'suggested_commands': []}
    
    def _extract_features(self, data):
        """Extract features from interaction data"""
        print("🔧 Extracting features from:", data)
        features = {
            'time_since_last_action': data.get('inactivity_time', 0),
            'current_tool': data.get('tool_id', 0),
            'cursor_velocity': data.get('cursor_velocity', 0),
            'click_frequency': data.get('click_frequency', 0),
            'session_duration': data.get('session_duration', 0),
            'recent_commands': data.get('recent_commands', [])
        }
        return self._vectorize(features)
    
    def _vectorize(self, features):
        """Convert features to tensor"""
        # Use only the numerical features for now
        vector = np.array([
            features['time_since_last_action'],
            features['cursor_velocity'], 
            features['click_frequency'],
            features['session_duration']
        ], dtype=np.float32)
        print(f"📐 Vectorized features: {vector}")
        return torch.from_numpy(vector).unsqueeze(0)
    
    def _format_prediction(self, prediction):
        """Format model output for the frontend"""
        print(f"🎨 Formatting prediction: {prediction}")
        
        try:
            if isinstance(prediction, dict):
                # Extract values from tensors
                hesitation_tensor = prediction.get('hesitation', torch.tensor([[0.0]]))
                confidence_tensor = prediction.get('confidence', torch.tensor([[0.0]]))
                commands_tensor = prediction.get('suggested_commands', torch.tensor([[0.0]]))
                
                hesitation = bool(hesitation_tensor[0][0].item() > 0.5)
                confidence = float(confidence_tensor[0][0].item())
                
                # Get top suggested commands
                suggested_commands = []
                if commands_tensor is not None and len(commands_tensor.shape) > 1:
                    top_commands = torch.topk(commands_tensor[0], min(3, commands_tensor.shape[1]))
                    suggested_commands = top_commands.indices.tolist()
                
                result = {
                    'hesitation': hesitation,
                    'confidence': confidence,
                    'suggested_commands': suggested_commands
                }
                print(f"✅ Final prediction: {result}")
                return result
            else:
                print("❌ Prediction is not a dictionary")
                return {'hesitation': False, 'confidence': 0.0, 'suggested_commands': []}
                
        except Exception as e:
            print(f"❌ Error formatting prediction: {e}")
            return {'hesitation': False, 'confidence': 0.0, 'suggested_commands': []}
