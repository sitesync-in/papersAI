from django.urls import path
from .views import StudentClassListCreateView, StudentListCreateView, StudentDetailView

urlpatterns = [
    path('classes/', StudentClassListCreateView.as_view(), name='class-list'),
    path('', StudentListCreateView.as_view(), name='student-list'),
    path('<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
]
