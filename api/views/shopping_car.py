from django.http import JsonResponse
from api import models
from rest_framework import serializers
from rest_framework.views import APIView
from api.serializers import srl
from rest_framework.response import Response
from django.shortcuts import HttpResponse
from django.shortcuts import render
import json
from api.utlis.response import BaseResponse
# Create your views here.


# 版本 redis + ViewSetMixin, GenericAPIView
from django.conf import settings

from rest_framework.viewsets import ViewSetMixin
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.renderers import JSONRenderer

import redis


USER_ID = 1
CONN = redis.Redis(host='118.24.111.198', port=6379)
# CONN.flushall()


class ShoppingCar(ViewSetMixin, GenericAPIView):
    # queryset = models.Course.objects.all()
    # print('queryset', queryset, type(queryset))

    def list(self, request, *args, **kwargs):
        data = BaseResponse()
        data.code = 0
        data.data = {}
        data.error = ''

        # CONN.hset('shopping_car_1_1', 'id', 1)
        # CONN.hset('shopping_car_1_1', 'name', 'nut')
        # CONN.hset('shopping_car_1_1', 'img', 'course.course_img')
        # CONN.hset('shopping_car_1_2', 'id', 2)
        # CONN.hset('shopping_car_1_2', 'name', 'got')
        # CONN.hset('shopping_car_1_2', 'img', 'course.course_img')

        key = settings.SHAPPING_CAR % (USER_ID, '*')    # 格式为 shopping_car_1_1
        lis = CONN.keys(key)    # 按照key模糊查询redis中的数据（匹配用户id的所有课程）

        # 如果购物车为空
        if not lis:
            return Response('购物车为空！', headers={'Access-Control-Allow-Origin': '*'})
        # res = CONN.get('shopping_car_1_1')
        # print('res', res)
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

    print(333)

    def create(self, request, *args, **kwargs):
        data = BaseResponse()
        data.code = 0
        data.data = {}
        data.error = ''
        # print('request._request', request._request)
        print('request.data', request.data)
        # print('request.body', request.body)
        course_id = int(request.data.get('course_id'))
        price_id = int(request.data.get('price_id'))

        # 校验课程
        course_obj = models.Course.objects.filter(id=course_id).first()
        if not course_obj:
            return Response('课程不存在！', headers={'Access-Control-Allow-Origin': '*'})

        # 校验价格策略
        price_queryset = course_obj.price_policy.all()
        price_dict = {}
        for item in price_queryset:
            temp = {
                'id': item.id,
                'price': item.price,
                'valid_period': item.valid_period,
                'valid_period_display': item.get_valid_period_display()
            }
            price_dict[item.id] = temp
        if price_id not in price_dict:
            return Response({'code': -13, 'error': '价格策略不存在！'})

        key = settings.SHAPPING_CAR % (USER_ID, course_id)
        CONN.hset(key, 'id', str(course_id))
        CONN.hset(key, 'name', course_obj.name)
        CONN.hset(key, 'img', course_obj.course_img)
        CONN.hset(key, 'price_id', str(price_id))
        CONN.hset(key, 'price_dict', json.dumps(price_dict))

        return Response({'code': 1, 'data': '添加成功！'})
