from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from tools.generic_views import GenericCreateView, GenericUpdateView
from .forms import CustomUserCreationForm, CustomUserFullForm
from .serializers import RegisterSerializer
from .models import CustomUser, send_verification_email
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class ActivateAccountView(generics.GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated'}, status=status.HTTP_200_OK)
        return Response({'message': 'Activation link is invalid'}, status=status.HTTP_400_BAD_REQUEST)


class CustomUserLoginView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')  # redirige vers la vue nommée 'home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["new_user_form"] = CustomUserCreationForm
        context["login_tab"] = True
        return context

    def get_success_url(self):
        if "next" in self.request.GET:
            return self.request.GET["next"]
        else:
            return self.success_url


class ConfirmUserView(View):
    model = CustomUser
    template_name = 'registration/login_confirm.html'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class CustomUserCreateView(GenericCreateView):
    model = CustomUser
    fields = None
    form_class = CustomUserCreationForm
    template_name = 'generic_update.html'
    success_message = 'Success: new user created.'
    success_url = reverse_lazy('home')
    title = "New User"

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        context["title"] = self.title
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        send_verification_email(user)
        return super().form_valid(form)

class CustomUserUpdateView(GenericUpdateView):
    model = CustomUser
    fields = None
    form_class = CustomUserFullForm
    template_name = 'generic_update.html'
    success_url = reverse_lazy('home')
    success_message = _('Changes saved.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model
        context["title"] = _("Update Profile")
        return context

    def get_success_url(self):
        return self.success_url

