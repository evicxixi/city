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


class ShoppingCar(GenericViewSet, ViewSetMixin):

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
            shopping_car_item[key] = {    # 将 redis 中的若干 dict 构造到内存中
                'id': CONN.hget(key, 'id').decode('utf-8'),
                'name': CONN.hget(key, 'name').decode('utf-8'),
                'img': CONN.hget(key, 'img').decode('utf-8'),
                'price_id': CONN.hget(key, 'price_id'),
                'price_dict': json.loads(CONN.hget(key, 'price_dict').decode('utf-8')),
            }
        data.data = shopping_car_item
        return Response(data.data, headers={'Access-Control-Allow-Origin': '*'})

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

        # 取值 course_id,price_id
        course_id = int(request.data.get('course_id'))
        price_id = int(request.data.get('price_id'))

        # 校验课程
        course_obj = models.Course.objects.filter(id=course_id).first()
        if not course_obj:
            return Response('课程不存在！', headers={'Access-Control-Allow-Origin': '*'})

        # 构造所选商品价格策略到内存
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

        # 校验所选价格策略是否合法（是否在价格策略中）
        if price_id not in price_dict:
            return Response({'code': -13, 'error': '价格策略不存在！'})

        # 存库到redis
        user_id = request.user.id  # 设置drf认证组件后 通过request.user获取当前用户信息
        # print('user_id', type(user_id), user_id)
        # print('course_id', type(course_id), course_id)
        key = settings.SHAPPING_CAR % (user_id, course_id)
        # print('key', type(key), key)
        CONN.hset(key, 'id', str(course_id))
        CONN.hset(key, 'name', course_obj.name)
        CONN.hset(key, 'img', course_obj.course_img)
        CONN.hset(key, 'price_id', str(price_id))
        CONN.hset(key, 'price_dict', json.dumps(price_dict))

        return Response({'code': 1, 'data': '添加到购物车成功！'})
