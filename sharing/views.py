from django.shortcuts import render, redirect
from sharing.forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html', {})


# Работа с пользователем
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def account(request):
    return render(request, 'registration/account.html', {'user': request.user})
