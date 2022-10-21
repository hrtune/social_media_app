from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('<h1>ようこそ、社会本へ！</h1>')