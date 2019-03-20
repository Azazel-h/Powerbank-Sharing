from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    username = forms.CharField(error_messages={'required': 'Это поле обязательно.'})
    email = forms.EmailField(max_length=254, required=True, error_messages={'max_length': 'Максимальная длина почты - 254.', 'required': 'Это поле обязательно.'})

    error_messages = {
        'required': 'Это поле обязательно.',
        'password_mismatch': "Пароли не совпадают!",
    }

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')