import json

from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.shortcuts import render

from dev import views as dev_views

import requests


def intro(request):
    return render(request, 'intro.html')


def get_qrcode(request):
    data = {'status': True, 'data': None}

    access_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo&state={state}#wechat_redirect"
    url = access_url.format(
        appid='wx45351926e9ed39ac',
        # redirect_uri="http://127.0.0.1:8000/get_wx_id/",  # 跳转回我的网站
        redirect_uri="http://118.24.111.198:8000/get_wx_id/",  # 跳转回我的网站
        # state=request.session['user_info']['id']  # 用户ID
        state=1  # 用户ID
    )
    data['data'] = url
    return JsonResponse(data)


def get_wx_id(request):
    print('get_wx_id')
    code = request.GET.get("code")
    state = request.GET.get("state")
    print('code', code)
    print('state', state)

    # 获取该用户openId(用户唯一，用于给用户发送消息)
    r1 = requests.get(
        url="https://api.weixin.qq.com/sns/oauth2/access_token",
        params={
            "appid": 'wx65d37317efb972e0',
            "secret": 'f59dc1e2f5e3641145a213027fb122cc',
            "code": code,
            "grant_type": 'authorization_code',
        }
    ).json()
    open_id = r1.get("openid")  # 能够获取到openid表示用户授权成功
    if not open_id:
        return HttpResponse('授权失败！')
    # 假设用户已存在 并存库
    # user = models.UserInfo.objects.filter(id=state).first()
    # if not user.open_id:
    #     user.wx_id = open_id
    #     user.save()

    return HttpResponse('授权成功！当前授权用户的openid：' + open_id)
