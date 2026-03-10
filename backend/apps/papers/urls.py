from django.urls import path
from .views import PaperGenerateView, PaperListView, PaperDetailView, PaperDownloadView, DashboardStatsView, CurriculumOptionsView

urlpatterns = [
    path('generate/', PaperGenerateView.as_view(), name='paper-generate'),
    path('curriculum-options/', CurriculumOptionsView.as_view(), name='curriculum-options'),
    path('', PaperListView.as_view(), name='paper-list'),
    path('<int:pk>/', PaperDetailView.as_view(), name='paper-detail'),
    path('<int:pk>/download/', PaperDownloadView.as_view(), name='paper-download'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
