import json
import datetime
import ast

from django.http import JsonResponse
from django.shortcuts import HttpResponse, render
from django.conf import settings

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
# from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
# from rest_framework.renderers import JSONRenderer

import redis
from django_redis import get_redis_connection

from api import models
from api.utlis.response import BaseResponse
from api.serializers import srl

# Create your views here.


# 全局模式设置获取redis
CONN = get_redis_connection("default")
# CONN.flushall()

# "payment_1_1": {
#     "id": "1",
#     "name": "Pyhton入门 10分钟快速预览",
#     "price_id": "1",
#     "price_dict": "{'1': {'id': 1, 'price': 11.0, 'valid_period': 1, 'valid_period_display': '1天'}, '5': {'id': 5, 'price': 33.0, 'valid_period': 3, 'valid_period_display': '3天'}}",
#     "coupon_id": "0",
#     "coupon_dict": {
#         "0": "请选择优惠券",
#         "8": "课程1立减50"
#     }
# },
# "payment_1_2": {
#     "id": "2",
#     "name": "Python发展史",
#     "price_id": "11",
#     "price_dict": "{'3': {'id': 3, 'price': 22.0, 'valid_period': 1, 'valid_period_display': '1天'}, '11': {'id': 11, 'price': 33.0, 'valid_period': 3, 'valid_period_display': '3天'}, '10': {'id': 10, 'price': 77.0, 'valid_period': 7, 'valid_period_display': '1周'}}",
#     "coupon_id": "0",
#     "coupon_dict": {
#         "0": "请选择优惠券",
#         "9": "课程2立减100"
#     }
# },
# "global_coupon_1": {
#     "0": "请选择通用优惠券",
#     "3": "全局双十一满100减10",
#     "5": "全局优惠券"
# }


class Settlement(GenericViewSet, ViewSetMixin):
    serializer_class = srl.CouponSer

    def list(self, request, *args, **kwargs):
        """
        查看当前用户的订单 get
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = BaseResponse()
        data.data = {}

        # 格式为 shopping_car_1_1
        # 设置drf认证组件后 通过request.user获取当前用户信息
        key = settings.PAYMENT % (request.user.id, '*')
        lis = CONN.keys(key)    # 按照key模糊查询redis中的数据（匹配用户id的所有课程）
        print('lis', type(lis), lis)

        # 如果购物车为空
        if not lis:
            return Response('购物车为空！', headers={'Access-Control-Allow-Origin': '*'})

        # 如果购物车不为空
        payment_item = {}
        for x in lis:
            key = x.decode('utf-8')   # payment_1_1
            print('key', type(key), key)

            # payment_dict = {
            #     'id': '1',
            #     'name': 'Pyhton入门 10分钟快速预览',
            #     'img': 'https://www.baidu.com/img/bd_logo1.png',
            #     'price_id': '5',
            #     'price_dict': {
            #         '1': {'id': 1, 'price': 11.0, 'valid_period': 1, 'valid_period_display': '1天'},
            #         '5': {'id': 5, 'price': 33.0, 'valid_period': 3, 'valid_period_display': '3天'}
            #     },
            #     'coupon_id': 0,
            #     'coupon_dict': {0: '请选择优惠券', 7: '课程1立减50'}
            # }
            # print(payment_dict)

            # ret = CONN.hgetall(key)
            # print('ret', ret)
            # price_dict = CONN.hget(key, 'price_dict'),
            # print('price_dict', price_dict)
            # ret = CONN.hget(key, 'coupon_dict')
            # ret = ret.decode('utf-8')
            # # ret = json.loads(ret)
            # ret = ast.literal_eval(ret)
            # print('ret', type(ret), ret)
            payment_item[key] = {    # 将 redis 中的若干商品dict 构造到内存中
                'id': CONN.hget(key, 'id').decode('utf-8'),
                'name': CONN.hget(key, 'name').decode('utf-8'),
                'price_id': CONN.hget(key, 'price_id').decode('utf-8'),
                'price_dict': CONN.hget(key, 'price_dict'),
                'coupon_id': CONN.hget(key, 'coupon_id'),
                'coupon_dict': ast.literal_eval(CONN.hget(key, 'coupon_dict').decode('utf-8')),
            }

        # 将redis中的一个全局优惠券dict构造到内存中
        key = settings.GLOBAL_COUPON % (request.user.id)

        print('key', type(key), key)
        coupon_dict = CONN.hget(key, 'coupon_dict')
        payment_item[key] = json.loads(coupon_dict)
        data.data = payment_item
        return Response(data.data, headers={'Access-Control-Allow-Origin': '*'})
        # return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        提交结算中心以生成订单 post
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = BaseResponse()
        data.data = {}

        # 设置drf认证组件后 通过request.user获取当前用户信息
        user_id = request.user.id

        # 如果当前用户有尚未付款订单
        order_obj = models.Order.objects.filter(account_id=user_id).first()
        if order_obj:
            return Response('您还有未付款的订单待处理！')

        # 获取当前用户结算中心的待结算payment_key_list
        payment_key = settings.PAYMENT % (user_id, '*')
        payment_key_list = CONN.keys(payment_key)
        print('payment_key_list###############', type(
            payment_key_list), payment_key_list)

        if not payment_key_list:
            return Response('您的购物车为空哦！')

        # 若购物车不为空 便计算当前订单应付金额
        for payment_key in payment_key_list:
            payment_key = payment_key.decode('utf-8')
            # print('payment_key', type(payment_key), payment_key.decode('utf-8'))

            # 循环获取当前用户结算中心的商品id
            course_id = CONN.hget(payment_key, 'id').decode('utf-8')
            print('course_id', type(course_id), course_id,)
            # 写到这里了

        # 生成订单
        order_obj = models.Order.objects.create()

        # 同时构造每个商品的数据并存库

        return Response({'code': 1, 'data': '结算成功！'})
