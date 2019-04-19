from django.shortcuts import render, redirect, HttpResponse, render_to_response
from sharing.forms import ChangeFormPassword, SignUpForm, EmailChangeForm, PassportPhotoForm, ChangeNameForm, \
    AvatarPhotoForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import json
from sharing.models import Share, Profile, Powerbank, Order, PaymentPlan, Wallet
from django.template import RequestContext
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
#from background_task import background
from random import random, randint
import datetime
import requests

free_counted = False
remaining_started = False

def powerbank_percentage():
    free = len(Powerbank.objects.filter(status='free'))
    total = len(Powerbank.get_all())
    if total == 0:
        return 0
    return free * 100 // total


def get_profile(user):
    return Profile.objects.get(user=user)


def recount_free():
    shares = Share.get_all()
    for sh in shares:
        sh.free_pbs = 0
        sh.save()
    pbs = Powerbank.objects.filter(status='free')
    for item in pbs:
        share = Share.objects.get(id=item.location)
        share.free_pbs += 1
        share.save()


def get_last_order(profile):
    orders = Order.objects.filter(profile=profile)
    if len(orders) == 0:
        return Order(progress='failed')
    return orders[len(orders) - 1]


def remaining_min(order):
    if order.progress != 'created':
        return None
    when_ordered = order.timestamp
    deadline = when_ordered + datetime.timedelta(minutes=order.reservation_time)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (deadline - now).total_seconds() / 60.0


def fail_order(order):
    order.progress = 'failed'
    pb = order.pb
    share = order.share
    share.free_pbs += 1
    pb.status = 'free'
    share.save()
    pb.save()
    order.save()


#@background(schedule=60)
def check_reservations():
    profiles = Profile.objects.all()
    for pr in profiles:
        rem = remaining_min(get_last_order(pr))
        if rem != None:
            if rem <= 0:
                fail_order(get_last_order(pr))


def seed_points():
    for i in range(120):
        kw = {}
        kw['title'] = 'seed'
        kw['address'] = 'seed'
        kw['crds_lot'] = float(randint(10, 110))
        kw['crds_lat'] = float(randint(10, 110))
        kw['qrcode'] = '777777'
        kw['free_pbs'] = 0
        share = Share(title='seed', address='seed', crds_lot=float(randint(10, 110)), crds_lat=float(randint(10, 110)), qrcode='777777', free_pbs=0)
        share.save()


def seed_pbs():
    for i in range(120):
        kw = {}
        kw['capacity'] = randint(1, 99999)
        kw['location'] = randint(1, 69)
        kw['status'] = 'free'
        kw['code'] = 'wtf is that'
        pb = Powerbank(capacity=randint(1, 99999), location=randint(1, 69), status='free', code='wtf is that')
        pb.save()


def reset_sessions_and_orders():
    active_sessions = Order.objects.filter(progress='applied')
    for session in active_sessions:
        fail_order(session)


def count_profit(order):
    if order.progress != 'applied':
        return None
    when_ordered = order.timestamp
    now = datetime.datetime.now(datetime.timezone.utc)
    cost = order.payment_plan.cost
    return int((now - when_ordered).total_seconds() / 60.0 * cost)


def index(request):
    rem = 0
    pending_notification = False
    session_notification = False
    global free_counted, remaining_started
    if not free_counted:
        #recount_free()
        free_counted = True
    if not remaining_started:
        check_reservations()
        remaining_started = True
    if request.user.is_authenticated:
        if not Profile.objects.filter(user=request.user).exists():
            new_profile = Profile(user=request.user)
            new_profile.save()
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
    return render(request, 'index.html', {'sharings': Share.get_all(), 'pb': Powerbank.get_all(), 'pending_notification': pending_notification, 'session_notification': session_notification, 'remaining': rem})


@login_required
def add_powerbank_sharing(request):
    if request.user.is_superuser is False:
        return redirect('/')

    if request.method == 'POST':
        title = request.POST.get('title')
        address = request.POST.get('address')
        qrcode = request.POST.get('qrcode')
        ip = request.POST.get('ip')
        crds = json.loads(request.POST.get('crds'))
        new_sharing = Share(title=title, address=address, crds_lot=crds[0], crds_lat=crds[1], qrcode=qrcode, ip=ip)
        new_sharing.save()
        return HttpResponse('Новая точка выдачи успешно добавлена!')
    context = {}
    return render(request, 'sharing/add.html', context)

@login_required
def add_pb(request):
    if not request.user.is_superuser:
        return redirect('/')

    if request.method == 'POST':
        code = random()
        location = request.POST.get('location')
        capacity = request.POST.get('capacity')
        new_pb = Powerbank(code=code, location=location, capacity=capacity, status='free')
        share = Share.objects.get(id=location)
        share.free_pbs += 1
        share.save()
        new_pb.save()
        return HttpResponse('Новый powerbank успешно добавлен!')
    return render(request, 'sharing/add_pb.html')

@login_required
def share_page(request, pk):
    pbs = Powerbank.objects.filter(location=pk, status='free')
    pb_size = len(pbs)
    if pb_size == 0:
        min_cap = max_cap = 0
    elif pb_size == 1:
        min_cap = max_cap = pbs[0].capacity
    else:
        min_cap = pbs[0].capacity
        max_cap = pbs[1].capacity
        for pb in pbs:
            if pb.capacity > max_cap:
                max_cap = pb.capacity
            if pb.capacity < min_cap:
                min_cap = pb.capacity
    context = {
        'share': Share.objects.get(id=pk),
        'min_cap' : min_cap,
        'max_cap' : max_cap,
        'amt' : pb_size
    }
    return render(request, 'sharing/share_page.html', context)


"""
Работа с пользователем
"""


@login_required
def account(request):
    profile = Profile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'profile': profile,
        'profile_progress': Profile.get_progress_complete_account(request.user),
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
    Страница, на которой админ может одобрить фотографию с паспортом или отклонить.
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
        id = request.POST.get('id')
        profile = Profile.objects.get(id=id)

        if status == 'approve':
            profile.passport_status = 'success'
            profile.save()
            return HttpResponse('success')

        elif status == 'reject':
            profile.passport_status = 'fail'
            profile.save()
            return HttpResponse('fail')
    return render(request, 'registration/passports.html', context)


@login_required
def change_password(request):
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
    if request.method == 'POST':
        current_user = request.user
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['new_email1'] == form.cleaned_data['new_email2']:
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

"""
Добавление тарифа и метода оплаты
"""

@login_required
def add_payment_plan(request):
    if not request.user.is_superuser:
        return redirect('/')    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        payment_type = request.POST.get('payment_type')
        cost = request.POST.get('cost')
        payment_plan = PaymentPlan(name=name, description=description, payment_type=payment_type, cost=cost)
        payment_plan.save()
        return HttpResponse('Новый тариф успешно добавлен!')
    return render(request, 'payment/add_payment_plan.html')


@login_required
def add_wallet(request):   
    if request.method == 'POST':
        name = request.POST.get('name')
        payment_method = request.POST.get('payment_method')
        balance = request.POST.get('balance')
        wallet = Wallet(name=name, payment_method=payment_method, status='active', balance=balance)
        profile = get_profile(request.user)
        wallet.save()
        wallet_str = profile.wallets
        new_wallet_str = wallet_str + str(wallet.id) + ' '
        profile.wallets = new_wallet_str
        profile.save()
        return HttpResponse('Новый кошелёк успешно добавлен!')
    return render(request, 'payment/add_wallet.html')


"""
Сканирование кода
"""

@login_required
def scan(request):
    profile = get_profile(request.user)
    order = get_last_order(profile)
    if not profile.active_mail or profile.passport_status != 'success':
        return unverified(request)
    if order.progress != 'created':
        return redirect('/')
    if request.method == 'POST':
        scanned_code = request.POST.get('qrcode')
        if order.progress == 'created': # Если пользователь заказал зараннее
            if order.share.qrcode == scanned_code:
                order.progress = 'applied'
                order.save()
                return render(request, 'scan/session.html')
        else:
            '''
                energo Pro - мнговенный заказ пб без бронирования
            '''
            pass
    else:
        return render(request, 'scan/scan.html')


def unverified(request):
    profile = Profile.objects.get(user=request.user)
    reasons = []
    if not profile.active_mail:
        reasons.append('Не активирован почтовый адрес')
    if not profile.passport_status == 'success':
        reasons.append('Не подтверждён паспорт')
    return render(request, 'scan/unverified.html', { 'reasons' : reasons })


@login_required
def session(request):
    profile = Profile.objects.get(user=request.user)
    order = get_last_order(profile)
    pb = order.pb
    ctx = {}
    if not order.progress == 'applied':
        return redirect('/')
    """
        Обработка начала/конца сессии -- выдача пб, валидация сессии, прочее
    """
    if pb.status == 'ordered':
        ejreq = requests.get('http://' + order.share.ip + '/')
        # Начать оплату
        pb.status = 'occupied'
    elif pb.status == 'returning':
        ejreq = requests.get('http://' + order.share.ip + '/')
        # Конец оплаты
        pb.status = 'charging'
    elif pb.status == 'occupied':
        ctx['to_pay'] = count_profit(order)
        ctx['capacity'] = pb.capacity
        ctx['timestamp'] = order.timestamp
        ctx['payment_plan'] = order.payment_plan.name
        ctx['wallet'] = order.wallet.name
    pb.save()
    # Текущая оплата...
    return render(request, 'scan/session.html', ctx)


"""
Заказ PB
"""

@login_required
def ordering(request, pk):
    profile = get_profile(request.user)
    if not profile.active_mail or profile.passport_status != 'success':
        return unverified(request)
    if get_last_order(profile).progress == 'applied':
        return redirect('/session')
    share = Share.objects.get(id=pk)
    ctx = { "location" : share.address }
    ctx["small"] = False
    ctx["medium"] = False
    ctx["large"] = False
    for pb in Powerbank.objects.filter(location=share.id, status='free'):
        if pb.capacity <= 4000:
            ctx["small"] = True
        if 4001 <= pb.capacity <= 10000:
            ctx["medium"] = True
        if pb.capacity >= 10001:
            ctx["large"] = True
    ctx["pk"] = pk
    wallets_id = list(map(int, profile.wallets.split()))
    wallets = []
    for wid in wallets_id:
        wallets.append(Wallet.objects.filter(id=wid)[0])
    ctx["plans"] = PaymentPlan.objects.all()
    ctx["wallets"] = wallets

    if request.method == 'POST':
        order_type = request.POST.get('order_type')
        pb_capacity = request.POST.get('pb_capacity')
        payment_plan_id = request.POST.get('payment_plan')
        wallet_id = request.POST.get('wallet')
        payment_plan = PaymentPlan.objects.filter(id=payment_plan_id)[0]
        wallet = Wallet.objects.filter(id=wallet_id)[0]
        if order_type != None and pb_capacity != None:
            cands = Powerbank.objects.all().filter(location=pk, status='free')
            cand = None
            if pb_capacity == 'small': # находим максимальный до 4000
                mx_cand = 0
                for pb in cands:
                    if pb.capacity > mx_cand and pb.capacity <= 4000:
                        mx_cand = pb.capacity
                        cand = pb
            elif pb_capacity == 'medium': # находим максимальный от 4001 до 10000
                mx_cand = 0
                for pb in cands:
                    if pb.capacity > mx_cand and 4001 <= pb.capacity <= 10000:
                        mx_cand = pb.capacity
                        cand = pb
            elif pb_capacity == 'large': # находим самый максимальный
                mx_cand = 0
                for pb in cands:
                    if pb.capacity > mx_cand:
                        mx_cand = pb.capacity
                        cand = pb
            else:
                pass
            if cand != None:
                if order_type == 'N':
                    order = Order(wallet=wallet, payment_plan=payment_plan, order_type='immediate', pb=cand, share=share, profile=get_profile(request.user), reservation_time=2)
                else:
                    order = Order(wallet=wallet, payment_plan=payment_plan, order_type='hold', pb=cand, share=share, profile=get_profile(request.user))
                order.save()
                cand.status = 'ordered'
                # когда юзер отсканит, тогда cand.status = 'occupied'
                share.free_pbs -= 1
                share.save()
                cand.save()
                ctx['order_status'] = 'succeess'
            else:
                ctx['order_status'] = 'fail'
                # не найдено (но такого не будет)
    return render(request, 'sharing/order.html', context=ctx)


@login_required
def pending(request):
    profile = get_profile(request.user)
    if not profile.active_mail or profile.passport_status != 'success':
        return unverified(request)
    order = get_last_order(get_profile(request.user))
    rem = remaining_min(order)
    if rem != None:
        if rem <= 0:
            fail_order(order)
    if order.progress != 'created':
        return redirect('/')
    ctx = {}
    ctx['capacity'] = str(order.pb.capacity)
    ctx['timestamp'] = str(order.timestamp)
    ctx['remaining'] = int(remaining_min(order))
    ctx['address'] = order.share.address
    ctx['plan'] = order.payment_plan.name
    ctx['wallet'] = order.wallet.name
    return render(request, 'scan/pending.html', context=ctx)
        
        
@login_required
def cancelled(request):
    orders = Order.objects.filter(profile=get_profile(request.user))
    last = len(orders) - 1
    order = orders[last]
    if order.progress != 'created':
        return redirect('/')
    pb = order.pb
    share = order.share
    pb.status = 'free'
    pb.save()
    order.progress = 'cancelled'
    order.save()
    share.free_pbs += 1
    share.save()
    return render(request, 'scan/cancelled.html')

"""
Шаманство с правами пользователя
"""

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
    ctx = { 'pts': points }
    return render(request, 'debug/display.html', ctx)


@login_required
def display_orders(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    orders = Order.objects.filter(profile=get_profile(request.user))
    ctx = { 'orders': orders }
    return render(request, 'debug/orders.html', ctx)


@login_required
def display_plans(request):
    if not request.user.is_superuser:
        return redirect('/error/rights')
    plans = PaymentPlan.objects.all()
    ctx = { 'plans': plans }
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


def contacts(request):
    return render(request, 'contacts.html', {})


def error_rights(request):
    return render(request, 'error_rights.html')

# def handler404(request, exception, template_name="404.html"):
#     response = render_to_response("404.html")
#     response.status_code = 404
#     return response
