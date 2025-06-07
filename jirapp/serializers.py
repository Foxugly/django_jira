from rest_framework import serializers
from .models import JiraCredential

class JiraCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraCredential
        fields = ['id', 'jira_url', 'username', 'api_token', 'created_at']
        extra_kwargs = {
            'api_token': {'write_only': True},
        }
