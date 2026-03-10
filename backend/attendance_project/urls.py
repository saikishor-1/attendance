from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.generic import TemplateView

def api_root(request):
    return JsonResponse({"status": "success", "message": "Attendly API is running securely on Render!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('attendance_app.urls')),
    path('api_root/', api_root),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
