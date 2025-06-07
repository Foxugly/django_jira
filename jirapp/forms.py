from django import forms
from .models import JiraCredential

class JiraCredentialForm(forms.ModelForm):
    class Meta:
        model = JiraCredential
        fields = ['name', 'jira_url', 'username', 'api_token', 'project_key', 'board_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_url': forms.URLInput(attrs={'class': 'form-control'}),
            'username': forms.EmailInput(attrs={'class': 'form-control'}),
            'api_token': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'project_key': forms.TextInput(attrs={'class': 'form-control'}),
            'board_id': forms.TextInput(attrs={'class': 'form-control'}),
        }


class JiraCredentialReadOnlyForm(forms.ModelForm):

    class Meta:
        model = JiraCredential
        fields = ['name', 'jira_url', 'username', 'api_token', 'project_key', 'board_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'jira_url': forms.URLInput(attrs={'class': 'form-control'}),
            'username': forms.EmailInput(attrs={'class': 'form-control'}),
            'api_token': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'project_key': forms.TextInput(attrs={'class': 'form-control'}),
            'board_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(JiraCredentialReadOnlyForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].disabled = True
