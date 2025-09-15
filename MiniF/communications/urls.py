from django.urls import path, include

urlpatterns = [
    path('api/', include('communications.api_urls')),
    # Інші URL
]