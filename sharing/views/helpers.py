"""
Модули:
    - sharing.models
    - datetime
    - random
"""
import datetime
from random import randint
from sharing.models import Powerbank, Profile, Share, Order


def powerbank_percentage():
    """
    Процент доступных powerbank'ов
    :return:
    """
    free = len(Powerbank.objects.filter(status='free'))
    total = len(Powerbank.get_all())
    if total == 0:
        return 0
    return free * 100 // total


def get_profile(user):
    """
    Получить профиль по пользователю
    :param user:
    :return:
    """
    return Profile.objects.get(user=user)


def recount_free():
    """
    Пересчет доступных powerbank'ов
    :return:
    """
    shares = Share.get_all()
    for share in shares:
        share.free_pbs = 0
        share.save()
    pbs = Powerbank.objects.filter(status='free')
    for item in pbs:
        share = Share.objects.get(id=item.location)
        share.free_pbs += 1
        share.save()


def get_last_order(profile):
    """

    :param profile:
    :return:
    """
    orders = Order.objects.filter(profile=profile)
    if not orders:
        return Order(progress='failed')
    return orders[len(orders) - 1]


def remaining_min(order):
    """
    Функция подчета остатка времени бронирования
    :param order:
    :return:
    """
    if order.progress != 'created':
        return None
    when_ordered = order.timestamp
    deadline = when_ordered + \
        datetime.timedelta(minutes=order.reservation_time)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (deadline - now).total_seconds() / 60.0


def fail_order(order):
    """

    :param order:
    :return:
    """
    order.progress = 'failed'
    order.end_timestamp = datetime.datetime.now(datetime.timezone.utc)
    order.end_share = order.share
    power = order.pb
    share = order.share
    share.free_pbs += 1
    power.status = 'free'
    share.save()
    power.save()
    order.save()


def end_order(order, end_share):
    """
    Закончить заказ
    :param order, end_share:
    :return:
    """
    order.progress = 'ended'
    order.end_timestamp = datetime.datetime.now(datetime.timezone.utc)
    order.end_share = end_share
    power = order.pb
    power.status = 'charging'
    # requests.get('http://' + order.end_share.ip + '/')
    order.save()
    power.save()


def order_duration(order):
    """
    Длительность заказа в минутах
    :param order:
    :return:
    """
    start = order.timestamp
    end = order.end_timestamp
    return int((end - start).total_seconds() / 60.0)


def check_reservations():
    """

    :return:
    """
    profiles = Profile.objects.all()
    for profile in profiles:
        remain = remaining_min(get_last_order(profile))
        if remain is not None:
            if remain <= 0:
                fail_order(get_last_order(profile))


def seed_points():
    """

    :return:
    """
    i = 0
    while i < 120:
        kiwi = {}
        kiwi['title'] = 'seed'
        kiwi['address'] = 'seed'
        kiwi['crds_lot'] = float(randint(10, 110))
        kiwi['crds_lat'] = float(randint(10, 110))
        kiwi['qrcode'] = '777777'
        kiwi['free_pbs'] = 0
        share = Share(title='seed', address='seed',
                      crds_lot=float(randint(10, 110)),
                      crds_lat=float(randint(10, 110)),
                      qrcode='777777', free_pbs=0)
        share.save()

def reset_sessions_and_orders():
    """

    :return:
    """
    active_sessions = Order.objects.filter(progress='applied')
    for session in active_sessions:
        fail_order(session)


def count_profit(order):
    """
    Подсчет прибыли (DEPRECATED)
    :param order:
    :return:
    """
    if order.progress != 'applied' and order.progress != 'ended':
        return None
    when_ordered = order.timestamp
    now = datetime.datetime.now(datetime.timezone.utc)
    cost = order.payment_plan.cost
    return int((now - when_ordered).total_seconds() / 60.0 * cost)


def has_active_subscription(profile):
    """
    Проверка наличия активированной подписки
    :param profile:
    :return:
    """
    if profile.payment_plan is None:
        return False
    when_ordered = profile.payment_plan_activation_time
    deadline = when_ordered + \
        datetime.timedelta(days=profile.payment_plan.duration)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (deadline - now).total_seconds() > 0
