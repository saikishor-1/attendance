from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentViewSet, AttendanceViewSet, api_diag, drop_unique_index

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)

urlpatterns = [
    path('diag/', api_diag),
    path('drop-unique-index/', drop_unique_index),
    path('', include(router.urls)),
]
