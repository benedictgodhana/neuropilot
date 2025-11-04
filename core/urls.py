from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('design.urls')),  # Your design app
    path('ml/', include('ml.urls')),   # ← ADD THIS LINE for ML app
]