from django.http import JsonResponse
from api import models
from rest_framework import serializers
from rest_framework.views import APIView
from dev.serializers import course
from rest_framework.response import Response
from django.shortcuts import HttpResponse
from django.shortcuts import render
import json
from dev.utlis.response import BaseResponse

# Create your views here.


class CourseVersion(APIView):

    def get(self, request):
        if request.version == 'v1':
            data = 'v1'
        else:
            data = 'other'
        return HttpResponse(data)


# class DegreeCourse(APIView):
#     def get(self,request):
#         print('Course get ----------')
#         data = {'code':1}
#         all_degreecourse = models.DegreeCourse.objects.all()
#         data['degreecourse'] = {}
#         for i in all_degreecourse:
#             # data['degreecourse'][i.id] = {
#             #     'course':i.name,
#             #     'teachers': [ i.name for i in i.teachers.all()],
#             # }
#             print(i.name)
#             res = i.degreecourse_price_policy.all()
#             res = api_serializers.DegreeCourseSer(res,many=True)
#             print('data',data)
#             for i in res:
#                 print('i.price',i.price)
#
#         return JsonResponse(res.data, safe=False)
# return JsonResponse(data, safe=False)
# return JsonResponse(data, safe=False)
# return Response(res)

# ORM练习
# a.查看所有学位课并打印学位课名称以及授课老师
# class Course(APIView):
#     def get(self, request, version):
#         data = BaseResponse()
#         all_degreecourse = models.DegreeCourse.objects.all()
#         data.degreecourse = {}
#         for i in all_degreecourse:
#             data.degreecourse[i.id] = {
#                 'course': i.name,
#                 'teachers': [i.name for i in i.teachers.all()],
#             }
#         return HttpResponse(json.dumps(data.dict, ensure_ascii=False))
#
# b.查看所有学位课并打印学位课名称以及学位课的奖学金

# class Course(APIView):
#     def get(self, request, version):
#         data = BaseResponse()
#         all_degreecourse = models.DegreeCourse.objects.all()
#         data.degreecourse = {}
#         for i in all_degreecourse:
#             data.degreecourse[i.id] = {
#                 'course': i.name,
#                 # 'scholarship': [i.value for i in i.scholarship_set.all()],    # 查询方法一
#                 'scholarship': [i for i in i.degreecourse_price_policy.all().values('price')]   # 查询方法二
#             }
#         return HttpResponse(json.dumps(data.dict,ensure_ascii=False))

#
# c.展示所有的专题课
# models.Course.objects.filter(degree_course__isnull=True)

# class Course(APIView):
#
#     def get(self, request, version):
#         data = BaseResponse()
#         all_course = models.Course.objects.filter(degree_course__isnull=True)
#         all_course = course.CourseSer(all_course,many=True)
#
#         data.data = {}
#         data.data['course'] = all_course.data
#
#         return JsonResponse(data.dict)


#
# d.查看id = 1 的学位课对应的所有模块名称
# class Course(APIView):

#     def get(self, request, version):
#         data = BaseResponse()

#         all_course = models.Course.objects.filter(degree_course_id=1)
#         all_course = course.CourseSer(all_course, many=True)

#         data.data = {}
#         data.data['course'] = all_course.data

#         return HttpResponse(json.dumps(data.dict, ensure_ascii=False))
#
# e.获取id =
# 1的专题课，并打印：课程名、级别(中文)、why_study、what_to_study_brief、所有recommend_courses
class Course(APIView):

    def get(self, request, version):
        data = BaseResponse()

        # course_obj = models.Course.objects.filter(id=1).first()
        course_obj = models.Course.objects.get(id=1)

        print('coursedetail__hours', course_obj.coursedetail.hours)
        all_recommend = course_obj.coursedetail.recommend_courses.all()
        all_recommend = course.CourseSer(all_recommend, many=True)

        data.data = {
            'name': course_obj.name,
            'level': course_obj.level,
            'why_study': course_obj.coursedetail.why_study,
            'what_to_study_brief': course_obj.coursedetail.what_to_study_brief,
            'recommend_courses': all_recommend.data,
        }
        print(data.dict)
        # data.data['course'] = course_obj
        # return Response(data.dict)
        # return JsonResponse
        return HttpResponse(json.dumps(data.dict, ensure_ascii=False))

#
# f.获取id = 1的专题课，并打印该课程相关的所有常见问题
#
# g.获取id = 1的专题课，并打印该课程相关的课程大纲
#
# h.获取id = 1的专题课，并打印该课程相关的所有章节
#
# i.获取id = 1的专题课，并打印该课程相关的所有课时
# 第1章·Python
# 介绍、基础语法、流程控制
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# 第1章·Python
# 介绍、基础语法、流程控制
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# 01 - 课程介绍（一）
# i.获取id = 1的专题课，并打印该课程相关的所有的价格策略
