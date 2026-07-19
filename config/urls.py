"""
Root URL configuration for the job_portal project.

All API routes are namespaced under /api/. Media files are served
locally in DEBUG mode for convenience during development.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("accounts.urls")),
    path("api/jobs/", include("jobs.urls")),
    path("api/applications/", include("applications.urls")),
    path("api/", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
