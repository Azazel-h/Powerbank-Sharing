"""PowerBank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from sharing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('sharing/add', views.add_powerbank_sharing, name='add_sharing'),
    path('sharing/add_pb', views.add_pb, name='add_power_bank'),
    url(r'^share/(?P<key>\d+)/$', views.share_page, name='share_page'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup', views.signup, name='reg'),
    path('account/', views.account, name='account'),
    path('account/passports', views.users_passports, name='users_passports'),

    path('change/pass', views.change_password, name='change_password'),
    path('change/email', views.change_email, name='change_email'),
    path('change/name', views.change_name, name='change_name'),
    path('change/photo', views.change_photo, name='change_photo'),

    path('contacts/', views.contacts, name='contacts'),
    path('error/rights', views.error_rights, name='error_rights'),

    path('scan', views.scan, name='scan'),
    path('session', views.session, name='session'),

    path('cheat', views.make_verified, name='cheat'),
    url(r'^order/(?P<key>\d+)/$', views.ordering, name='ordering'),
    path('pending', views.pending, name='pending'),
    path('cancelled', views.cancelled, name='cancelled'),
    path('debug/make_verified', views.make_verified, name='make_verified'),
    path('debug/display_points', views.display_points, name='display_points'),
    path('debug/display_orders', views.display_orders, name='display_orders'),
    path('debug/seed', views.seed, name='seed'),
    path('debug/display_plans', views.display_plans, name='display_plans'),
    path('debug/reset_orders', views.reset_orders, name='reset_orders'),

    path('payment/add_payment_plan',
         views.add_payment_plan, name='add_payment_plan'),
    path('payment/add_wallet',
         views.add_wallet, name='add_wallet')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
