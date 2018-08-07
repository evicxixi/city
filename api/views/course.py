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

            all_recommend = course_obj.coursedetail.recommend_courses.all()
            all_recommend = srl.CourseSer(all_recommend, many=True)

            all_question = course_obj.asked_question.all()
            all_question = srl.OftenAskedQuestionSer(all_question, many=True)

            data.data = {
                'name': course_obj.name,
                'level': course_obj.level,
                'why_study': course_obj.coursedetail.why_study,
                'what_to_study_brief': course_obj.coursedetail.what_to_study_brief,
                'recommend_courses': all_recommend.data,
                'asked_question': all_question.data,
            }
        return HttpResponse(json.dumps(data.dict, ensure_ascii=False))
