from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import ModelForm
from .models import CustomUser


class CustomUserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        # instance = getattr(self, 'instance', None)
        # if instance and instance.pk:
        #    self.fields['is_superuser'].widget.attrs['readonly'] = True
        #    self.fields['is_superuser'].widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = CustomUser
        fields = ['email', ]


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', ]

    # def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    self.fields['categories'].widget.attrs.update({'class': 'select2', 'style':"width: 100%"})


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', ]


class CustomUserFullForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'full_name',]