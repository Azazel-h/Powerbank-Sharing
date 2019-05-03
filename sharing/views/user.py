"""
Модули:
    - django:
        - shortcuts
        - contrib.auth:
            - decorators
    - sharing:
        - models
        - views.helpers
        - forms
"""
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from sharing.forms import ChangeFormPassword, SignUpForm, \
     EmailChangeForm, PassportPhotoForm, ChangeNameForm, \
     AvatarPhotoForm
from sharing.models import Share, Profile, Powerbank
from sharing.views.helpers import powerbank_percentage


@login_required
def account(request):
    """
    Профиль пользователя/админа
    :param request:
    :return:
    """
    profile = Profile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'profile': profile,
        'profile_progress':
        Profile.get_progress_complete_account(request.user),
        'free_power_banks': powerbank_percentage(),
        'pb': Powerbank.get_all(),
        'share': Share.get_all()
    }

    if request.method == 'POST' and 'submit-passport' in request.POST:
        form = PassportPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            passport = form.cleaned_data['passport']
            profile.passport = passport
            profile.passport_status = 'checking'
            profile.save()
    else:
        form = PassportPhotoForm()
    context['form'] = form

    if request.method == 'POST' and request.POST.get('name'):
        name = request.POST.get('name')
        profile.name = name
        profile.save()
    return render(request, 'registration/account.html', context)


@login_required
def users_passports(request):
    """
    Страница, на которой админ может
    одобрить фотографию с паспортом или отклонить.
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect('/error/rights')

    context = {
        'passports': Profile.objects.filter(passport_status='checking')[::-1]
    }

    if request.method == 'POST':
        status = request.POST.get('status')
        id_key = request.POST.get('id')
        profile = Profile.objects.get(id=id_key)

        if status == 'approve':
            profile.passport_status = 'success'
            profile.save()
            return HttpResponse('success')
        if status == 'reject':
            profile.passport_status = 'fail'
            profile.save()
            return HttpResponse('fail')
    return render(request, 'registration/passports.html', context)


@login_required
def change_password(request):
    """
    Страница смены пароля
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ChangeFormPassword(request.user, request.POST)
        if form.is_valid():
            current_user = form.save()
            update_session_auth_hash(request, current_user)
            current_user.save()
            context = {
                'form': ChangeFormPassword(request.user),
                'profile': Profile.objects.get(user=request.user),
                'success_text': 'Пароль успешно изменен!'
            }
            return render(request, 'edit_user/change_password.html', context)
    else:
        form = ChangeFormPassword(request.user)
    context = {
        'form': form,
        'profile': Profile.objects.get(user=request.user),
    }
    return render(request, 'edit_user/change_password.html', context)


@login_required
def change_email(request):
    """
    Страница смены электронной почты
    :param request:
    :return:
    """
    if request.method == 'POST':
        current_user = request.user
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_email1'] == \
               form.cleaned_data['new_email2']:
                current_user.email = form.cleaned_data['new_email1']
                current_user.save()
                context = {
                    'form': EmailChangeForm(),
                    'profile': Profile.objects.get(user=request.user),
                    'success_text': 'Ваша почта успешно изменена!'
                }
                return render(request, 'edit_user/change_email.html', context)
    else:
        form = EmailChangeForm()
    context = {
        'form': form,
        'profile': Profile.objects.get(user=request.user)
    }
    return render(request, 'edit_user/change_email.html', context)


@login_required
def change_name(request):
    """
    Страница смены имени пользователя
    :param request:
    :return:
    """
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ChangeNameForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            profile.name = name
            profile.save()
            context = {
                'form': form,
                'profile': profile,
                'success_text': 'Ваше имя успешно изменено!'
            }
            return render(request, 'edit_user/change_name.html', context)
    else:
        form = ChangeNameForm()
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'edit_user/change_name.html', context)


@login_required
def change_photo(request):
    """
    Страница смены фото пользователя
    :param request:
    :return:
    """
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = AvatarPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.cleaned_data['photo']
            profile.photo = photo
            profile.save()
            context = {
                'profile': profile,
                'form': AvatarPhotoForm(),
                'success_text': 'Аватарка успешно изменена!'
            }
            return render(request, 'edit_user/change_photo.html', context)
    else:
        form = AvatarPhotoForm()
    context = {
        'profile': profile,
        'form': form
    }
    return render(request, 'edit_user/change_photo.html', context)


def signup(request):
    """
    Страница регистрации пользователя
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            profile = Profile(user=user)
            profile.save()
            login(request, user)
            return redirect('/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})
