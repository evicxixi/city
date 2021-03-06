from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from api.utlis.response import BaseResponse

from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

import json

from api.serializers import srl
from api import models
# Create your views here.


# 版本一 常规APIView
class Course(APIView):

    def get(self, request, version, key=None):
        data = BaseResponse()
        data.data = {}
        if not key:    # c.展示所有的专题课
            course_obj = models.Course.objects.all()
            course_obj = srl.CourseSer(course_obj, many=True)
            data.data = course_obj.data
        elif key.isdigit():    # e.获取id = 1的专题课，并打印：课程名、级别(中文)、why_study、what_to_study_brief、所有recommend_courses
            course_obj = models.Course.objects.get(id=key)

            # recommend_courses
            all_recommend = course_obj.coursedetail.recommend_courses.all()
            all_recommend = srl.CourseSer(all_recommend, many=True)

            # OftenAskedQuestion
            all_question = course_obj.asked_question.all()
            all_question = srl.OftenAskedQuestionSer(all_question, many=True)

            # CourseSection
            from django.forms.models import model_to_dict   # 一个转dict的模块

            # 章节+课时 构造dict
            # 1. 构造chapter_list 包含 section_list
            all_chapter = models.CourseChapter.objects.filter(
                course_id=key)
            all_setion = models.CourseSection.objects.filter(
                chapter__course_id=key)
            all_setion_list = [model_to_dict(i) for i in all_setion]
            chapter_list = []
            for i in all_chapter:
                print(i.id)
                chapter = {
                    'chapter_id': i.id,
                    'chapter__name': i.name,
                    'children': []
                }
                for x in all_setion_list:
                    print(x)
                    if i.id == x['chapter']:
                        chapter['children'].append(x)
                chapter_list.append(chapter)

            data.data = {
                'name': course_obj.name,
                'level': course_obj.level,
                'why_study': course_obj.coursedetail.why_study,
                'what_to_study_brief': course_obj.coursedetail.what_to_study_brief,
                'recommend_courses': all_recommend.data,
                'asked_question': all_question.data,
                'chapter_list': chapter_list,
                # "Access-Control-Allow-Origin" : "*",
            }

        return Response(data.dict, headers={'Access-Control-Allow-Origin': '*'})
