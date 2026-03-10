from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.generic import TemplateView

import os
from django.conf import settings
from attendance_project.settings import BASE_DIR

# Force redeploy: 2026-03-10 21:32
def api_root(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM django_migrations WHERE app = 'attendance_app'")
            applied_migrations = [row[0] for row in cursor.fetchall()]
        db_ok = True
    except Exception as e:
        db_ok = str(e)
        indexes = []
        applied_migrations = []
    
    frontend_dist = str(BASE_DIR.parent / 'frontend' / 'dist')
    dist_exists = os.path.exists(frontend_dist)
    dist_files = os.listdir(frontend_dist) if dist_exists else []
    # Ultimate truth: read our own file content
    try:
        with open(__file__, 'r') as f:
            code_content = f.read()
    except:
        code_content = "Could not read file"

    return JsonResponse({
        "status": "success",
        "db_ok": db_ok,
        "indexes": indexes,
        "dist_exists": dist_exists,
        "dist_files": dist_files,
        "DEBUG": settings.DEBUG,
        "code_snippet": code_content[-200:] # Last 200 chars to verify
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('attendance_app.urls')),
    path('api_root/', api_root),
    path('api_root_v2/', lambda r: JsonResponse({"version": "v2", "msg": "If you see this, code is updated"})),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
