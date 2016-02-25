"""phople URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import SimpleRouter

import apiserver.views.account as ac
import apiserver.views.datepost as datepost
from apiserver.views import misc

urlpatterns = []
router = SimpleRouter(trailing_slash=False)

if getattr(settings, 'DEBUG', False):
    urlpatterns += [
        url(r'^requestinfo$', misc.requestinfo),
    ]

urlpatterns += [
    # Account
    url(r'^login$', ac.login),
    url(r'^login_facebook$', ac.login_facebook),
    url(r'^me', ac.me),
    url(r'^logout$', ac.logout),
    url(r'^signup$', ac.signup),
    url(r'^signdown$', ac.signdown),
    url(r'^user/(?P<username>\w+)/exists', ac.user_exists),
]
router.register(r'couple', ac.CoupleViewSet)
router.register(r'datepost', datepost.DatePostViewSet)
urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
]
