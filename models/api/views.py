from django.shortcuts import render
from django.http import JsonResponse
from .models import *
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
import os
import hmac
from django.conf import settings


@csrf_exempt
def get_list(request):
    apts = Apartment.objects.all().values()
    data = {}
    data['valid'] = True
    data['result'] = list(apts)
    ids = {}
    if len(Apartment.objects.all()) > 0:
        ids['id'] = list(apts)[0].get('id')
    for i in range(len(data['result'])):
        data['result'][i]['id'] = list(apts)[i].get('id')
    return JsonResponse(data)

@csrf_exempt
def get_top_list(request):
    apts = Apartment.objects.all().order_by('-rating')[:5].values()
    data = {}
    data['valid'] = True
    data['result'] = list(apts)
    ids = {}
    if len(Apartment.objects.all()) > 0:
        ids['id'] = list(apts)[0].get('id')
    for i in range(len(data['result'])):
        data['result'][i]['id'] = list(apts)[i].get('id')
    return JsonResponse(data)

@csrf_exempt
def get_price_list(request):
    apts = Apartment.objects.all().order_by('price')[:5].values()
    data = {}
    data['valid'] = True
    data['result'] = list(apts)
    ids = {}
    if len(Apartment.objects.all()) > 0:
        ids['id'] = list(apts)[0].get('id')
    for i in range(len(data['result'])):
        data['result'][i]['id'] = list(apts)[i].get('id')
    return JsonResponse(data)

@csrf_exempt
def item(request, id):
    data = {}
    if Apartment.objects.all().filter(id=id).exists():
        apts = Apartment.objects.all().filter(id=id).values()
        data = {}
        data['valid'] = True
        data['result'] = list(apts)
        data['result'][0]['id'] = id
        print(data['result'])
    else:
        data['valid'] = False
        data['message'] = 'Apartment does not exist.'
    return JsonResponse(data)



@csrf_exempt
def delete(request, id):
    data = {}
    if request.method == "GET":
        if Apartment.objects.all().filter(id=id).exists():
            apt = Apartment.objects.get(id=id)
            apt.delete()
            data['valid'] = True
            data['message'] = 'Apartment deleted.'
        else:
            data['valid'] = False
            data['message'] = 'Apartment does not exist.'
    else:
        data['valid'] = False
        data['message'] = 'Not a GET request.'
    return JsonResponse(data)


@csrf_exempt
def create(request):
    data = {}
    if request.method == "POST":
        apt = Apartment()
        apt.name = request.POST.get('name', "")
        apt.price = request.POST.get('price', "")
        apt.save()
        jsondata = [{
            "name": apt.name,
            'id': apt.id,
            'price': apt.price,
        }]
        data['valid'] = True
        data['message'] = 'Created new Apartment.'
        data['result'] = jsondata
    else:
        data['valid'] = False
        data['message'] = 'Not a POST request.'
    return JsonResponse(data)

@csrf_exempt
def update(request, id):
    data = {}
    if request.method == "POST":
        apt = Apartment()
        apt.id = id
        apt.name = request.POST.get('name')
        apt.price = request.POST.get('price')
        apt.save()
        jsondata = [{
            "name": apt.name,
            'id': apt.id,
            'price': apt.price,
        }]
        data['valid'] = True
        data['message'] = 'Updated the Apartment.'
        data['result'] = jsondata
    else:
        data['valid'] = False
        data['message'] = 'Not a POST request.'
    return JsonResponse(data)
