from django.http import JsonResponse
from django.shortcuts import HttpResponse
from django.shortcuts import render


import requests


def index(request):
    return render(request, 'index.html')
