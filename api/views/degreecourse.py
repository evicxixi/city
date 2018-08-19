from django.http import JsonResponse
from api import models
from rest_framework import serializers
from rest_framework.views import APIView
# from api import serializers as api_serializers
from api.serializers import srl
from rest_framework.response import Response
from django.shortcuts import HttpResponse
from django.shortcuts import render
import json
from api.utlis.response import BaseResponse

# Create your views here.


class DegreeCourse(APIView):

    def get(self, request, version, key):
        print('key', key)
        # # print('request.content_type', request.content_type)
        # # print('request.GET', request.GET)
        # # print('request.parsers', request.parsers)
        # query = dict(request.GET)
        # print('request.GET', query)

        # # for k, v in request.GET:
        # #     print(k, v)
        data = BaseResponse()
        data.data = {}
        if key == 'scholarship':    # b.查看所有学位课并打印学位课名称以及学位课的奖学金
            degree_course = models.DegreeCourse.objects.all()   # 查询所有学位课
            for x in degree_course:
                scholarship_obj = x.scholarship_set.all()   # 一对多反向查询所有奖学金
                scholarship_obj = srl.ScholarshipSer(
                    scholarship_obj, many=True).data    # 序列化所有奖学金
                data.data[x.name] = scholarship_obj
            data.code = 1
        elif key == 'teacher':
            # a.查看所有学位课并打印学位课名称以及授课老师
            degree_course = models.DegreeCourse.objects.all()   # 查询所有学位课
            for x in degree_course:
                all_teacher = x.teachers.all()  # 多对对查询所有老师queryset
                all_teacher = srl.TeacherSer(
                    all_teacher, many=True).data   # 序列化所有老师queryset
                data.data[x.name] = all_teacher
            data.code = 1
        elif key.isdigit():    # d. 查看id=1的学位课对应的所有模块名称
            # print('key.isdigit()', key.isdigit())
            degree_course_obj = models.DegreeCourse.objects.get(id=key)
            all_course = degree_course_obj.course_set.all()
            all_course = srl.CourseSer(all_course, many=True).data
            data.data = all_course

        else:
            data.error = '缺少查询关键字!'

            # 查询所有DegreeCourse
        try:
            pass
        except Exception as e:
            data.code = -1
            data.error = '获取数据失败!'

        return HttpResponse(json.dumps(data.dict, ensure_ascii=False))
        # return HttpResponse(data.dict)
        # return Response(data.dict)
