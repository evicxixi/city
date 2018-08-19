import uuid

from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.response import Response

from api import models
from api.utlis.response import BaseResponse


class AuthView(ViewSetMixin, APIView):
    """
    用户登陆认证
    :param request:
    :param args:
    :param kwargs:
    :return:
    """

    authentication_classes = []  # drf的认证组件已设置全局后 此字段设置空 意味此视图类不走认证模块

    def login(self, request, *args, **kwargs):
        data = BaseResponse()

        username = request.data.get('username')
        password = request.data.get('password')

        user_obj = models.Account.objects.filter(
            username=username, password=password).first()

        # 如果用户未登录
        if not user_obj:
            data.code = -1
            data.error = '登录失败！'
            return Response(data.dict)

        # 如果用户已登录 存库UserToken并返回token
        else:
            uid = str(uuid.uuid4())
            models.UserToken.objects.update_or_create(
                user=user_obj, defaults={'token': uid})
            data.code = 1
            data.data = uid
            return Response(data.dict)
