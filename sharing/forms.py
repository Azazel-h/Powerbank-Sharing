from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    username = forms.CharField(error_messages={'required': 'Это поле обязательно.'})
    first_name = forms.CharField(max_length=50, required=True, error_messages={'max_length': 'Максимальная длина возможного имени - 50.', 'required': 'Это поле обязательно.'})
    email = forms.EmailField(max_length=254, required=True, error_messages={'max_length': 'Максимальная длина почты - 254.', 'required': 'Это поле обязательно.'})

    error_messages = {
        'required': 'Это поле обязательно.',
        'password_mismatch': "Пароли не совпадают!",
    }

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')


class ChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(ChangeForm, self).__init__(*args, **kwargs)
        for field in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class EmailChangeForm(forms.Form):
    new_email1 = forms.EmailField(
        label=("Нова почта"),
        max_length=254,
        error_messages={'max_length': 'Максимальная длина почты - 254.', 'required': 'Это поле обязательно.'},
        widget=forms.EmailInput,
        required=True,
    )

    new_email2 = forms.EmailField(
        label=("Подтверждение новой почты"),
        max_length=254,
        error_messages={'max_length': 'Максимальная длина почты - 254.', 'required': 'Это поле обязательно.'},
        widget=forms.EmailInput,
        required=True,
    )