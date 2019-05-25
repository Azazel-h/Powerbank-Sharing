"""
Модули:
    - django:
        - shortcuts
    - sharing:
        - models
        - helpers
"""
from django.shortcuts import render
from sharing.models import Share, Profile, Powerbank
from sharing.views.helpers import check_reservations, get_last_order, \
    get_profile, remaining_min, fail_order, auto_email


def index(request):
    """
    Главная страница
    :param request:
    :return:
    """
    free_counted = False
    remaining_started = False
    rem = 0
    pending_notification = False
    session_notification = False
    if not free_counted:
        # recount_free()
        free_counted = True
    if not remaining_started:
        check_reservations()
        remaining_started = True
    if request.user.is_authenticated:
        if not Profile.objects.filter(user=request.user).exists():
            new_profile = Profile(user=request.user)
            new_profile.save()
        auto_email(request.user)
        order = get_last_order(get_profile(request.user))
        if order.progress == 'created':
            pending_notification = True
            rem = remaining_min(order)
            if rem < 0:
                fail_order(order)
                pending_notification = False
            else:
                rem = int(rem)
        elif order.progress == 'applied':
            session_notification = True

    context = {
        'sharings': Share.get_all(),
        'pb': Powerbank.get_all(),
        'pending_notification': pending_notification,
        'session_notification': session_notification,
        'remaining': rem
    }

    return render(request, 'index.html', context)


def contacts(request):
    """
    Страница о нас
    :param request:
    :return:
    """
    return render(request, 'contacts.html', {})


def error_rights(request):
    """
    Ограничение прав
    :param request:
    :return:
    """
    return render(request, 'error_rights.html')


def not_found(request):
    """
    Отсутствие страницы
    :param request:
    :return:
    """
    return render(request, '404.html')
