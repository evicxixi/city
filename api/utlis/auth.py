
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api import models


class CityAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        用户认证
        :param request:
        :return:
        """
        token = request.query_params.get('token')
        token_obj = models.UserToken.objects.filter(token=token).first()
        if not token_obj:    # 认证失败
            raise AuthenticationFailed({'code': 1008, 'error': '认证失败'})
        # 认证成功
        # 认证后返回一个tuple(两个值)(必须是元组 第一个值传给request.user 第二个值传给request.auth)
        return (token_obj.user, token_obj)
