"""city URL Configuration

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
from django.urls import path, re_path
from django.urls import include

from api import urls as api_urls
from dev import urls as dev_urls
from dev.views import get_wx_id
from dev.views import index
from api.views import auth

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^$', index.index),
    # url(r'auth/$',auth.AuthView.as_view({'post':'login'})),
    re_path('login/', auth.AuthView.as_view({'post': 'login'})),
    re_path('api/(?P<version>\w+)/', include(api_urls)),
    re_path('dev/(?P<version>\w+)/', include(dev_urls)),
    re_path('intro/', get_wx_id.intro),
    re_path('get_qrcode/', get_wx_id.get_qrcode),
    re_path('get_wx_id/', get_wx_id.get_wx_id),
    # re_path('^$',views.DegreeCourse.as_view()),
    # re_path('^$',views.DegreeCourse.as_view()),
]
# TypeError: view must be a callable or a list / tuple in the case of
# include().
