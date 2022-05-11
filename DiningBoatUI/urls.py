"""DiningBoatUI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from django.urls import path
from django.urls import include, re_path
from . import views
import re

urlpatterns = [
    path(r'^admin/$', admin.site.urls),#views.login
    #re_path(r'^viewtest/$', viewtest.hello, name='hello'),
    #url(r'^login/', views.login),
    url(r'^DiningBoat/login/$', views.login, name='login'),
    url(r'^DiningBoat/user_mode/$', views.user_mode, name='user_mode'),
    url(r'^DiningBoat/user_mode/stores/$', views.user_stores, name='user_mode_stores'),
    url(r'^DiningBoat/user_mode/stores/goods/$', views.user_store_goods, name='user_mode_store_goods'),
    url(r'^DiningBoat/user_mode/orders/$', views.user_orders, name='user_mode_orders'),
    url(r'^DiningBoat/user_mode/orders/goods/$', views.user_order_goods, name='user_mode_order_goods'),
    #url(r'^DiningBoat/user_mode/goods_recommendation/$', views.user_goodsRecommendation, name='user_mode_goodsRecommendation'),
    url(r'^DiningBoat/user_mode/myInfo/$', views.user_myInfo, name='user_mode_myInfo'),

    url(r'^DiningBoat/store_mode/$', views.store_mode, name='store_mode'),
    url(r'^DiningBoat/store_mode/goods/$', views.store_goods, name='store_mode_goods'),
    url(r'^DiningBoat/store_mode/orders/$', views.store_orders, name='store_mode_orders'),
    url(r'^DiningBoat/store_mode/orders/goods/$', views.store_order_goods, name='store_mode_order_goods'),
    url(r'^DiningBoat/store_mode/myInfo/$', views.store_myInfo, name='store_mode_myInfo')
]
