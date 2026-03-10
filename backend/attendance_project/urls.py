from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.generic import TemplateView

import os
from django.conf import settings
from attendance_project.settings import BASE_DIR

def api_root(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
        db_ok = True
    except Exception as e:
        db_ok = str(e)
    
    frontend_dist = str(BASE_DIR.parent / 'frontend' / 'dist')
    dist_exists = os.path.exists(frontend_dist)
    dist_files = os.listdir(frontend_dist) if dist_exists else []
    return JsonResponse({
        "status": "success",
        "db_ok": db_ok,
        "dist_exists": dist_exists,
        "dist_files": dist_files,
        "DEBUG": settings.DEBUG,
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('attendance_app.urls')),
    path('api_root/', api_root),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
