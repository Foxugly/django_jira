from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import JiraCredentialForm, JiraCredentialReadOnlyForm
from .models import JiraCredential
from .serializers import JiraCredentialSerializer
import requests
from tools.generic_views import GenericCreateView, GenericUpdateView, GenericDeleteView, GenericDetailView, \
    GenericListView
from django.utils.translation import gettext_lazy as _


# REST API ViewSet
class JiraCredentialViewSet(viewsets.ModelViewSet):
    model = JiraCredential
    serializer_class = JiraCredentialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JiraCredential.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        credential = self.get_object()
        response = requests.get(
            f"{credential.jira_url}/rest/api/3/myself",
            auth=(credential.username, credential.api_token),
            headers={"Accept": "application/json"},
        )
        if response.status_code == 200:
            return Response({'status': 'success', 'data': response.json()})
        return Response({'status': 'failure', 'details': response.text}, status=response.status_code)


# Web interface using Django generic views
class JiraCredentialListView(GenericListView):
    model = JiraCredential
    template_name = 'jira_list.html'
    context_object_name = 'credentials'

    def get_queryset(self):
        return JiraCredential.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(JiraCredentialListView, self).get_context_data(**kwargs)
        context['fields'] = ['id', 'jira_url', 'username', 'project_key', 'board_id', 'connected']
        context['fields_boolean'] = ['connected', ]
        return context


class JiraCredentialCreateView(GenericCreateView):
    model = JiraCredential
    form_class = JiraCredentialForm
    fields = None
    template_name = 'generic_update.html'
    success_url = reverse_lazy('jirapp:jiracredential_list')
    title = _('Create new Jira Account')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class JiraCredentialUpdateView(GenericUpdateView):
    model = JiraCredential
    form_class = JiraCredentialForm
    fields = None
    template_name = 'generic_update.html'
    success_url = reverse_lazy('jirapp:jiracredential_list')
    title = _('Edit Jira Credential')


class JiraCredentialDetailView(GenericDetailView):
    model = JiraCredential
    form_class = JiraCredentialReadOnlyForm
    template_name = 'generic_detail.html'
    success_url = reverse_lazy('jirapp:jiracredential_list')
    title = _('View Jira Credential')

    def get_context_data(self, **kwargs):
        context = super(JiraCredentialDetailView, self).get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context


class JiraCredentialDeleteView(LoginRequiredMixin, GenericDeleteView):
    model = JiraCredential
    template_name = 'generic_delete.html'
    success_url = reverse_lazy('jirapp:jiracredential_list')

    def get_queryset(self):
        return JiraCredential.objects.filter(user=self.request.user)


class JiraDetailView(GenericDetailView):
    model = JiraCredential
    form_class = JiraCredentialReadOnlyForm
    template_name = 'jira_detail.html'
    success_url = reverse_lazy('jirapp:jiracredential_list')
    title = _('View Jira Credential')

    def get_context_data(self, **kwargs):
        context = super(JiraDetailView, self).get_context_data(**kwargs)
        context["jiras"] = self.request.user.jiras.all()
        context["issues"] = self.request.user.current_jira.get_issues_from_active_sprint_json()
        context["workflow"] = self.request.user.current_jira.get_workflow_json
        context["sprint"] = self.request.user.current_jira.get_current_sprint_json()
        return context