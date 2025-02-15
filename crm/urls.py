from django.urls import path
from .views import get_leads, get_stages_with_leads

urlpatterns = [
    path('leads/', get_leads, name='all-leads'),
    path('leads/<int:lead_id>/', get_leads, name='lead-detail'),
    path('stages/', get_stages_with_leads, name='stages-with-leads'),
]
