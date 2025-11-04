from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from ml.services.prediction_engine import PredictionEngine

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def predict_hesitation(request):
    """API endpoint for hesitation prediction"""
    try:
        data = json.loads(request.body)
        
        prediction_engine = PredictionEngine.get_instance()
        result = prediction_engine.predict_hesitation(data)
        
        return JsonResponse({
            'success': True,
            'prediction': result,
            'model_loaded': prediction_engine.is_loaded
        })
        
    except Exception as e:
        logger.error(f"Prediction API error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_http_methods(["GET"])
def model_status(request):
    """Check model status"""
    prediction_engine = PredictionEngine.get_instance()
    
    return JsonResponse({
        'model_loaded': prediction_engine.is_loaded,
        'predictions_processed': len(prediction_engine.prediction_buffer)
    })
