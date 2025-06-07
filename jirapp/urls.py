from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'jirapp'

router = DefaultRouter()
router.register(r'credentials', JiraCredentialViewSet, basename='jirapp-credential')

urlpatterns = [
    # REST API
    path('api/', include(router.urls)),
    # Web interface
    path('credentials/', JiraCredentialListView.as_view(), name='jiracredential_list'),
    path('credentials/add/', JiraCredentialCreateView.as_view(), name='jiracredential_add'),
    path('credentials/<int:pk>/edit/', JiraCredentialUpdateView.as_view(), name='jiracredential_update'),
    path('credentials/<int:pk>/', JiraCredentialDetailView.as_view(), name='jiracredential_detail'),
    path('credentials/<int:pk>/delete/', JiraCredentialDeleteView.as_view(), name='jiracredential_delete'),
    path('<int:pk>/', JiraDetailView.as_view(), name='jira_detail'),

]
