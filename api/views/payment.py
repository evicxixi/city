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

# 购物车 = {
#     "shopping_car_1_1": {
#         "id": "1",
#         "name": "Pyhton入门 10分钟快速预览",
#         "img": "https://www.baidu.com/img/bd_logo1.png",
#         "price_id": "5",
#         "price_dict": {
#             "5": {
#                 "id": 5,
#                 "price": 33,
#                 "valid_period": 3,
#                 "valid_period_display": "3天"
#             }
#         }
#     }
# }
# 结算中心 = {
#     'payment_1_3':{
#         id:3,
#         mame:Django框架学习,
#         price_id:1,
#         price_priod:30,
#         price:199,
#         defaul_coupon_id:0,
#         coupon_dict: {              ----> 绑定了课程3的优惠券
#             0: '请选择课程优惠券',
#             1:'xxx',
#         }
#     },
#         glocal_coupon_1:{
#         2：。。。。
#         2：。。。。
#     }
# }


class Payment(GenericViewSet, ViewSetMixin):
    serializer_class = srl.CouponSer

    def list(self, request, *args, **kwargs):
        """
        查看结算中心 get
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
        将购物车内商品提交到结算中心 post
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = BaseResponse()
        data.data = {}

        # 设置drf认证组件后 通过request.user获取当前用户信息
        user_id = request.user.id

        # 清空当前用户之前结算中心的未结算信息
        payment_key = settings.PAYMENT % (user_id, '*')
        payment_key_list = CONN.keys(payment_key)
        for key in payment_key_list:
            CONN.delete(key)

        # 过滤出购物车中当前user_id的所有商品
        key = settings.SHAPPING_CAR % (user_id, '*')    # 格式为 shopping_car_1_*
        shopping_car_lis = CONN.keys(key)

        # 如果购物车为空
        if not shopping_car_lis:
            return Response('购物车为空无法结算！', headers={'Access-Control-Allow-Origin': '*'})

        # 优惠券
        # 方案一 构造全局优惠券（glocal_coupon_1）
        # global_coupon = models.CouponRecord.objects.filter(
        #     account_id=user_id, coupon__content_type__isnull=True).values('coupon_id', 'coupon__name')
        # # [{"coupon_id": 1, "coupon__name": "双十一立减100"}]

        # 方案二 构造优惠券（包含：通用 & 不通用）
        today = datetime.date.today()
        coupon_record_list = models.CouponRecord.objects.filter(
            account_id=user_id, status=0, coupon__valid_begin_date__lte=today, coupon__valid_end_date__gte=today)

        # 构造当前user_id优惠券字段（不通用封装到coupon_dict）（通用封装到coupon_global_dict）
        coupon_dict = {}    # 格式如下
        # coupon_dict = {
        #     0: {  # 课程id
        #         0: '请选择优惠券',
        #         1: '优惠券1',
        #     }
        # }
        global_coupon_dict = {0: '请选择通用优惠券'}
        for coupon_record in coupon_record_list:
            if coupon_record.coupon.object_id:
                coupon_dict[coupon_record.coupon.object_id] = {
                    0: '请选择优惠券',
                    coupon_record.id: coupon_record.coupon.name,
                }
            else:
                global_coupon_dict[
                    coupon_record.id] = coupon_record.coupon.name

        # 存库redis：当前user_id通用优惠券（glocal_coupon_1）
        global_coupon_key = settings.GLOBAL_COUPON % (user_id)
        CONN.hset(global_coupon_key, 'coupon_id', 0)
        CONN.hset(global_coupon_key, 'coupon_dict',
                  json.dumps(global_coupon_dict))

        # 当前user_id商品信息及优惠券存库redis

        # 构造所有课程字段到payment（须构造优惠券字段 加入到payment）（格式：payment_1_1）
        for key in shopping_car_lis:
            key = key.decode('utf-8')
            course_dict = CONN.hgetall(key)

            payment_dict = {}   # 构建结算中心单个商品的dict 同时清空上一个商品信息
            for k, v in course_dict.items():    # 循环当前user_id的所有购物车中的商品
                k, v = k.decode('utf-8'), v.decode('utf-8')

                # # 如果循环到id字段 为course_id赋值 并以此生成单个商品的key（payment_1_1）（删除 待确认）
                # course_id = v if k == 'id' else None
                # payment_key = settings.PAYMENT % (user_id, course_id)

                # 构造payment的字段 遇到price_dict单独处理
                payment_dict[k] = ast.literal_eval(
                    v) if k == 'price_dict' else v

                # 如果当前课程有优惠券 将优惠券数据添加到 payment_dict
                if k == 'id':
                    for num in coupon_dict:
                        if num == int(v):   # 如果当前课程有优惠券
                            payment_dict['coupon_id'] = 0
                            payment_dict['coupon_dict'] = coupon_dict[num]
                        # print('v', type(v), v)

                        # 构造当前课程的payment_key（payment_1_1）
                        payment_key = settings.PAYMENT % (user_id, v)
            # print('payment_key', type(payment_key), payment_key)

            # 存库redis：当前用户单个课程的所有字段（含新加入的优惠券）
            CONN.hmset(payment_key, payment_dict)

        return Response({'code': 1, 'data': '添加到结算中心成功！'})

    def put(self, request, *args, **kwargs):
        """
        修改单个商品优惠券id 及通用优惠券id（未完成）
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = BaseResponse()
        data.data = {}
        user_id = request.user.id
        course_id = int(request.query_params.get('course_id'))
        coupon_id = int(request.query_params.get('coupon_id'))
        # global_coupon_id = request.query_params.get(
        # 'global_coupon_id')
        print('coupon_id', type(coupon_id), coupon_id)

        # print('global_coupon_id', type(global_coupon_id), global_coupon_id)

    # 'payment_1_3':{
    #     id:3,
    #     mame:Django框架学习,
    #     price_id:1,
    #     price_priod:30,
    #     price:199,
    #     defaul_coupon_id:0,
    #     coupon_dict: {              ----> 绑定了课程3的优惠券
    #         0: '请选择课程优惠券',
    #         1:'xxx',
    #         2:'xxx',
    #         3:'xxx',
    #         4:'xxx',
    #     }
    # },

        # 修改结算中心每个商品的优惠券id
        key = settings.PAYMENT % (user_id, '*')
        payment_list = CONN.keys(key)
        for key in payment_list:
            # print('item', key)
            key = key.decode('utf-8')
            # print('item', key)
            id = CONN.hget(key, 'id').decode('utf-8')
            # print(id == course_id, type(id), type(course_id), id, course_id)
            if int(id) == course_id:
                CONN.hset(key, 'coupon_id', coupon_id),

        # 修改结算中心全局优惠券id
        key = settings.GLOBAL_COUPON % (user_id)
        print('key', key)
        # coupon_dict = CONN.hget(key, 'coupon_dict')
        coupon_dict = CONN.hgetall(key)
        print('coupon_dict', type(coupon_dict), coupon_dict)
        coupon_dict = json.loads(coupon_dict)

        return Response({'code': 1, 'data': '修改成功！'})
