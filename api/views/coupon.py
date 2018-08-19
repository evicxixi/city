from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from api.utlis.response import BaseResponse

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, UpdateModelMixin

import json

from api.serializers import srl
from api import models
# Create your views here.

# 获取用户ID=1的所有优惠券
# 获取专题课ID=1且用户ID=10的所有优惠券
# 获取用户ID=10的所有未绑定课程的优惠券
# 获取用户ID=1的所有可用优惠券


USER_ID = 1

# 优惠券（处理不需要传参的请求：所有、添加）


class Coupon(GenericAPIView, ListModelMixin, CreateModelMixin):
    queryset = models.Coupon.objects.all()
    serializer_class = srl.CouponSer

    def get(self, request, *args, **kwargs):
        print('request', request)
        print('request._request', request._request)
        print('request.data', request.data)
        print('request.body', request.body)
        print('request._request.body', request._request.body)
        print('request.query_params', request.query_params)
        return self.list(request, *args, **kwargs)


class CouponDetail(GenericAPIView, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin):
    queryset = models.Coupon.objects.all()
    serializer_class = srl.CouponSer
    # print('pk1', pk)

    def get(self, request, pk, *args, **kwargs):
        print('pk2', pk)
        return self.retrieve(request, pk, *args, **kwargs)

# 优惠券发放记录（处理需要传参的请求：查看单条、删除、更新）


class CouponRecord(GenericAPIView, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin):
    queryset = models.CouponRecord.objects.all()
    serializer_class = srl.CouponRecordSer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CouponGlobal(GenericAPIView, ListModelMixin, CreateModelMixin):

    # 全局优惠券
    queryset = models.CouponRecord.objects.filter(
        account_id=USER_ID, coupon__content_type__isnull=True)

    serializer_class = srl.CouponRecordSer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
