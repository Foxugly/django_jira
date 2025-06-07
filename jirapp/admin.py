from django.contrib import admin

from jirapp.models import JiraCredential


# Register your models here.
@admin.register(JiraCredential)
class JiraCredentialAdmin(admin.ModelAdmin):
    pass