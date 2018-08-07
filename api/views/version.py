
from rest_framework.views import APIView
from django.shortcuts import HttpResponse
from api.utlis.response import BaseResponse

# Create your views here.


class Version(APIView):

    def get(self, request, version):
        if request.version == 'v1':
            data = 'v1'
        else:
            data = '非法api'
        return HttpResponse(data)
