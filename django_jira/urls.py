from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path, include, reverse
from django.contrib.auth.views import *
from customuser.views import CustomUserLoginView
from oauth2_provider import urls as oauth2_urls


def home(request):
    c = {}
    if request.user.is_authenticated:
        if request.user.current_jira:
            return redirect("jirapp:jira_detail", pk= request.user.current_jira.id)
        else:
            return redirect("jirapp:jiracredential_list")
    else:
        return redirect('login')
    return render(request, "index.html", c)


urlpatterns = [
    path('', home, name='home'),
    path('user/', include('customuser.urls', namespace='user')),
    path('jira/', include('jirapp.urls', namespace='jira')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('o/', include(oauth2_urls)),

    path('login/', CustomUserLoginView.as_view(), name='login'),
    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path("password_reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done", ),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm", ),
    path("reset/done/", PasswordResetCompleteView.as_view(), name="password_reset_complete", ),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    path('admin/', admin.site.urls),
]
