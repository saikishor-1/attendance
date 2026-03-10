from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db import connection

def api_diag(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename, indexname, indexdef FROM pg_indexes WHERE schemaname = 'public'")
            indexes = [{"table": row[0], "name": row[1], "def": row[2]} for row in cursor.fetchall()]
            
            cursor.execute("SELECT name FROM django_migrations WHERE app = 'attendance_app'")
            migrations = [row[0] for row in cursor.fetchall()]
            
        return JsonResponse({
            "status": "success",
            "indexes": indexes,
            "migrations": migrations
        })
    except Exception as e:
        return JsonResponse({"status": "error", "msg": str(e)})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('attendance_app.urls')),
    path('api_diag/', api_diag),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
