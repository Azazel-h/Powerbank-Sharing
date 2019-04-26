from sharing.models import Powerbank, Profile, Share, Order
import datetime
from random import randint


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
    deadline = when_ordered + \
        datetime.timedelta(minutes=order.reservation_time)
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


def check_reservations():
    profiles = Profile.objects.all()
    for pr in profiles:
        rem = remaining_min(get_last_order(pr))
        if rem is not None:
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
        share = Share(title='seed', address='seed',
                      crds_lot=float(randint(10, 110)),
                      crds_lat=float(randint(10, 110)),
                      qrcode='777777', free_pbs=0)
        share.save()


def seed_pbs():
    for i in range(120):
        kw = {}
        kw['capacity'] = randint(1, 99999)
        kw['location'] = randint(1, 69)
        kw['status'] = 'free'
        kw['code'] = 'wtf is that'
        pb = Powerbank(capacity=randint(1, 99999),
                       location=randint(1, 69),
                       status='free',
                       code='wtf is that')
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
