"""
Модули:
    - django:
        - shortcuts
        - contrib.auth.decorators
    - sharing:
        - models
        - views.helpers
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sharing.models import Share, Profile, Order, PaymentPlan
from sharing.views.helpers import get_profile, reset_sessions_and_orders


@login_required
def make_verified(request):
    """
    Проверка статуса для получения доступа
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect('/error/rights')
    profile = Profile.objects.get(user=request.user)
    profile.passport_status = 'success'
    profile.active_mail = True
    profile.name = 'Sbeve Sbeve'
    profile.save()
    return redirect('/')


@login_required
def display_points(request):
    """
    Страница отображения всех станций
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect('/error/rights')
    points = Share.get_all()
    ctx = {'pts': points}
    return render(request, 'debug/display.html', ctx)


@login_required
def display_orders(request):
    """
    Страница заказов пользователя
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect('/error/rights')
    orders = Order.objects.filter(profile=get_profile(request.user))
    ctx = {'orders': orders}
    return render(request, 'debug/orders.html', ctx)


@login_required
def display_plans(request):
    """
    Страница всех тарифных планов
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect('/error/rights')
    plans = PaymentPlan.objects.all()
    ctx = {'plans': plans}
    return render(request, 'debug/plans.html', ctx)


@login_required
def reset_orders(request):
    """
    Сброс заказа
    :param request:
    :return:
    """
    if not request.user.is_superuser:
        return redirect('/error/rights')
    reset_sessions_and_orders()
    return redirect('/')
