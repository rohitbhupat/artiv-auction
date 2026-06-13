from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from dashboard import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("art.urls", namespace="art")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("registration/", include("registration.urls")),
    path('confirm_purchase/<int:artwork_id>/', views.confirm_purchase, name='confirm_purchase'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)