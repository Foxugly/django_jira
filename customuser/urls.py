from django.urls import path
from .views import RegisterView, ActivateAccountView, CustomUserCreateView, CustomUserUpdateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import EmailVerification

app_name = 'user'


def activate(request, token):
    verification = get_object_or_404(EmailVerification, token=token)
    if verification.is_expired():
        messages.error(request, "Lien expiré.")
    else:
        user = verification.user
        user.is_active = True
        user.save()
        verification.delete()
        messages.success(request, "Votre compte a été activé.")
    return redirect('login')  # ou une page de confirmation


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('add/', CustomUserCreateView.as_view(), name='user_add'),
    path('<int:pk>/update/', CustomUserUpdateView.as_view(), name="user_update"),
    path('activate/<uuid:token>/', activate, name='activate'),
    path('api/activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='api_activate'),
]
