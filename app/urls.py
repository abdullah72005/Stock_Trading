"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from finance.views import index_view, login_view, logout_view, register_view, buy_view, history_view, quote_view, sell_view, balance_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('register/', register_view),
    path('buy/', buy_view),
    path('history/', history_view),
    path('quote/', quote_view),
    path('sell/', sell_view),
    path('balance/', balance_view),
]
