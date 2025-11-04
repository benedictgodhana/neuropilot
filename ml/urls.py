from django.urls import path
from . import views

app_name = 'ml'

urlpatterns = [
    path('predict/', views.predict_hesitation, name='predict_hesitation'),
    path('status/', views.model_status, name='model_status'),
]
