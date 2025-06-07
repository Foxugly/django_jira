from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from jirapp.models import JiraCredential
from oauth2_provider.models import Application
from django.conf import settings
import uuid


def send_verification_email(user):
    token = get_random_string(32)
    EmailVerification.objects.create(user=user, token=token)
    verify_url = reverse('verify-email', args=[token])
    full_url = f"{settings.SITE_URL}{verify_url}"
    subject = 'Verify your email address'
    message = f"Hi,\nPlease verify your email by clicking the link below:\n{full_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], auth_user=settings.DEFAULT_FROM_EMAIL,
              auth_password=settings.DEFAULT_FROM_EMAIL_PASSWORD, )
    print(message)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        send_verification_email(user)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    jiras = models.ManyToManyField(JiraCredential, blank=True, related_name='jiras')
    current_jira = models.ForeignKey(JiraCredential, on_delete=models.PROTECT, related_name='current_jira', null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    # REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:  # Création automatique d'une application OAuth2 lors de la création d'un utilisateur
            Application.objects.create(
                user=self,
                name=f"{settings.APPLICATION_NAME} de {self.full_name}",
                client_type=Application.CLIENT_CONFIDENTIAL,
                authorization_grant_type=Application.GRANT_PASSWORD,
            )

class EmailVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at