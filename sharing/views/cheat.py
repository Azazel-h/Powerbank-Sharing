from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sharing.models import Share, Profile, Order, PaymentPlan
from sharing.views.helpers import get_profile, reset_sessions_and_orders,
seed_pbs, seed_points


@login_required
def make_verified(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    profile = Profile.objects.get(user=request.user)
    profile.passport_status = 'success'
    profile.session_status = 'inactive'
    profile.active_mail = True
    profile.name = 'Sbeve Sbeve'
    profile.save()
    return redirect('/')


@login_required
def display_points(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    points = Share.get_all()
    ctx = {'pts': points}
    return render(request, 'debug/display.html', ctx)


@login_required
def display_orders(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    orders = Order.objects.filter(profile=get_profile(request.user))
    ctx = {'orders': orders}
    return render(request, 'debug/orders.html', ctx)


@login_required
def display_plans(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    plans = PaymentPlan.objects.all()
    ctx = {'plans': plans}
    return render(request, 'debug/plans.html', ctx)


@login_required
def reset_orders(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    reset_sessions_and_orders()
    return redirect('/')


@login_required
def seed(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    seed_points()
    seed_pbs()
    return redirect('/')
