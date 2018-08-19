import json

from django.http import JsonResponse
from django.shortcuts import HttpResponse, render
from django.conf import settings

# 版本 redis + ViewSetMixin, GenericAPIView

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.renderers import JSONRenderer

import redis

from api import models
from api.serializers import srl
from django_redis import get_redis_connection
from api.utlis.response import BaseResponse


# Create your views here.

USER_ID = 1

# 局部模式设置获取redis
# CONN = redis.Redis(host='118.24.111.198', port=6379)

# 全局模式设置获取redis
CONN = get_redis_connection("default")
# CONN.flushall()


# class ShoppingCar(GenericViewSet):
# ViewSetMixin, APIView
class ShoppingCar(ViewSetMixin, GenericAPIView, ):
    serializer_class = srl.CouponSer

    def list(self, request, *args, **kwargs):
        """
        查看购物车
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = BaseResponse()
        data.data = {}

        # 设置drf认证组件后 通过request.user获取当前用户信息
        user_id = request.user.id

        key = settings.SHAPPING_CAR % (user_id, '*')    # 格式为 shopping_car_1_1
        lis = CONN.keys(key)    # 按照key模糊查询redis中的数据（匹配用户id的所有课程）

        # 如果购物车为空
        if not lis:
            return Response('购物车为空！', headers={'Access-Control-Allow-Origin': '*'})

        # 如果购物车不为空
        shopping_car_item = {}
        for x in lis:
            key = x.decode('utf-8')   # shopping_car_1_1
            print('x', type(x), x)
            print('key', type(key), key)

            shopping_car_item[key] = {    # 将 redis 中的若干 dict 构造到内存中
                'id': CONN.hget(key, 'id').decode('utf-8'),
                'name': CONN.hget(key, 'name').decode('utf-8'),
                'img': CONN.hget(key, 'img').decode('utf-8'),
                'price_id': CONN.hget(key, 'price_id'),
                'price_dict': json.loads(CONN.hget(key, 'price_dict').decode('utf-8')),
            }
            print(111)
        data.data = shopping_car_item
        print(222)
        return Response(data.data, headers={'Access-Control-Allow-Origin': '*'})
        # return self.list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        添加商品到购物车
        :param request:
        :param args: course_id,price_id
        :param kwargs:
        :return:
        """
        data = BaseResponse()
        data.data = {}

        # print('request._request', request._request)
        print('request.data', request.data)
        # print('request.body', request.body)

        # 取值 course_id,price_id
        course_id = int(request.data.get('course_id'))
        price_id = int(request.data.get('price_id'))

        # 校验课程
        course_obj = models.Course.objects.filter(id=course_id).first()
        if not course_obj:
            return Response('课程不存在！', headers={'Access-Control-Allow-Origin': '*'})

        # 构造所选商品价格策略到内存
        price_queryset = course_obj.price_policy.all()
        print('price_queryset', price_queryset)
        price_dict = {}
        for item in price_queryset:
            temp = {
                'id': item.id,
                'price': item.price,
                'valid_period': item.valid_period,
                'valid_period_display': item.get_valid_period_display()
            }
            price_dict[item.id] = temp

        # 校验所选价格策略是否合法（是否在价格策略中）
        if price_id not in price_dict:
            return Response({'code': -13, 'error': '价格策略不存在！'})

        # 存库到redis
        key = settings.SHAPPING_CAR % (USER_ID, course_id)
        CONN.hset(key, 'id', str(course_id))
        CONN.hset(key, 'name', course_obj.name)
        CONN.hset(key, 'img', course_obj.course_img)
        CONN.hset(key, 'price_id', str(price_id))
        CONN.hset(key, 'price_dict', json.dumps(price_dict))

        return Response({'code': 1, 'data': '添加到购物车成功！'})


class Payment(ViewSetMixin, GenericAPIView):
    serializer_class = srl.CouponSer

    # 提交到结算中心 post
    def commit(self, request, *args, **kwargs):
        data = BaseResponse()
        data.data = {}

        # 设置drf认证组件后 通过request.user获取当前用户信息
        user_id = request.user.id

        # 过滤出购物车中当前user_id的所有商品
        key = settings.SHAPPING_CAR % (user_id, '*')    # 格式为 shopping_car_1_1
        shopping_car_lis = CONN.keys(key)

        # 如果购物车为空
        if not shopping_car_lis:
            return Response('购物车为空无法结算！', headers={'Access-Control-Allow-Origin': '*'})

        # 如果购物车不为空
        # 构造所有课程字段到payment（须构造优惠券字段 加入到payment）（格式：payment_1_1）
        for item in shopping_car_lis:
            key = item.decode('utf-8')
            course_id = CONN.hget(key, 'id').decode('utf-8')
            course_obj = models.Course.objects.filter(id=course_id).first()

            # 构造payment字段数据
            course_id = CONN.hget(key, 'id').decode('utf-8')
            price_id = CONN.hget(key, 'price_id').decode('utf-8')
            price_tuple = json.loads(
                CONN.hget(key, 'price_dict').decode('utf-8')),

            # 为payment构造价格字段 price_dict为价格dict（id为key，价格详情dict为value）
            for price_dict in price_tuple[0]:
                if price_id in price_dict:
                    price = price_tuple[0][price_dict]['price']
                    price_priod = price_tuple[0][price_dict]['valid_period']

            coupon_dict = {0: '请选择优惠券'}

            # 构造当前课程 的优惠券字段
            coupon_queryset = course_obj.coupon.all()
            for num in range(len(coupon_queryset)):
                coupon_dict[num + 1] = coupon_queryset[num].name

            # 写入redis
            key = settings.PAYMENT % (user_id, course_id)
            CONN.hset(key, 'id', course_id)
            CONN.hset(key, 'price_id', price_id)
            CONN.hset(key, 'price_priod', price_priod)
            CONN.hset(key, 'price', price)
            CONN.hset(key, 'coupon_id', 0)
            CONN.hset(key, 'coupon_dict', json.dumps(coupon_dict))

        # 构造全局优惠券（glocal_coupon_1）
        global_coupon = models.CouponRecord.objects.filter(
            account_id=USER_ID, coupon__content_type__isnull=True).values('coupon_id', 'coupon__name')
        # [{"coupon_id": 1, "coupon__name": "双十一立减100"}]

        key = settings.GLOBAL_COUPON % (USER_ID)

        # 当前全局优惠券存库redis
        coupon_dict = {}
        for item in global_coupon:
            coupon_dict[item['coupon_id']] = item['coupon__name']
            # CONN.hset(key, item['coupon_id'], item['coupon__name'])
        CONN.hset(key, 'coupon_dict', json.dumps(coupon_dict))

        return Response({'code': 1, 'data': '添加成功！'})

    # 查看结算中心 get
    def all(self, request, *args, **kwargs):
        data = BaseResponse()
        data.data = {}

        # 设置drf认证组件后 通过request.user获取当前用户信息
        user_id = request.user.id
        key = settings.PAYMENT % (user_id, '*')    # 格式为 shopping_car_1_1
        lis = CONN.keys(key)    # 按照key模糊查询redis中的数据（匹配用户id的所有课程）

        # 如果购物车为空
        if not lis:
            return Response('购物车为空！', headers={'Access-Control-Allow-Origin': '*'})

        # 如果购物车不为空
        payment_item = {}
        for x in lis:
            key = x.decode('utf-8')   # payment_1_1
            # print('x', type(x), x)
            # print('key', type(key), key)

            payment_item[key] = {    # 将 redis 中的若干商品dict 构造到内存中
                'id': CONN.hget(key, 'id').decode('utf-8'),
                'price_id': CONN.hget(key, 'price_id').decode('utf-8'),
                'price_priod': CONN.hget(key, 'price_priod').decode('utf-8'),
                'price': CONN.hget(key, 'price'),
                'coupon_id': CONN.hget(key, 'coupon_id'),
                'coupon_dict': json.loads(CONN.hget(key, 'coupon_dict').decode('utf-8')),
            }

        # 将redis中的一个全局优惠券dict构造到内存中
        key = settings.GLOBAL_COUPON % (USER_ID)
        coupon_dict = CONN.hget(key, 'coupon_dict')
        payment_item[key] = json.loads(coupon_dict)
        data.data = payment_item
        return Response(data.data, headers={'Access-Control-Allow-Origin': '*'})
        # return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
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
        key = settings.GLOBAL_COUPON % (USER_ID)
        print('key', key)
        # coupon_dict = CONN.hget(key, 'coupon_dict')
        coupon_dict = CONN.hgetall(key)
        print('coupon_dict', type(coupon_dict), coupon_dict)
        coupon_dict = json.loads(coupon_dict)

        return Response({'code': 1, 'data': '修改成功！'})
