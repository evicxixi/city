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

from django.urls import path, re_path
# from api import views
from api.views import version, course, degree_course, shopping_car

urlpatterns = [
    # re_path('^degree_course/$', course.DegreeCourse.as_view()),
    re_path('^version/$', version.Version.as_view()),

    # a.查看所有学位课并打印学位课名称以及授课老师
    re_path('^degree_course/$', degree_course.DegreeCourse.as_view()),


    # b.查看所有学位课并打印学位课名称以及学位课的奖学金 (b和c共用一个url)
    # d. 查看id=1的学位课对应的所有模块名称
    re_path('^degree_course/(?P<key>\w+)/$',
            degree_course.DegreeCourse.as_view()),

    # c.展示所有的专题课
    re_path('^course/$', course.Course.as_view()),

    # e.获取id =
    # 1的专题课，并打印：课程名、级别(中文)、why_study、what_to_study_brief、所有recommend_courses
    re_path('^course/(?P<key>\w+)/$', course.Course.as_view()),


    # f.获取id = 1的专题课，并打印该课程相关的所有常见问题

    # g.获取id = 1的专题课，并打印该课程相关的课程大纲

    # h.获取id = 1的专题课，并打印该课程相关的所有章节




    re_path('^shopping_car/$',
            shopping_car.ShoppingCar.as_view({'get': 'list', 'post': 'create'})),
]
