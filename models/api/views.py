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
from django.contrib.auth.hashers import *
from django.forms.models import model_to_dict

@csrf_exempt
def item(request, id):
    data = {}
    auth = request.COOKIES.get('auth')
    if Apartment.objects.all().filter(id=id).exists():
        apts = Apartment.objects.all().filter(id=id).values()
        user_id = Authenticator.objects.get(authenticator=auth).user_id
        data = {}
        data['valid'] = True
        data['result'] = list(apts)
        data['result'][0]['id'] = id
        data['result'][0]['user_id'] = user_id

        recommended = [f['recommended_items'] for f in list(Recommendations.objects.all().filter(item_id=id).values())]
        data['rec'] = recommended
        recommended_apts = []
        for apt_id in recommended:
            recommended_apts.append(model_to_dict(Apartment.objects.get(id=apt_id)))
        data['rec'] = recommended_apts
        print(data['result'])
    else:
        data['valid'] = False
        data['message'] = 'Apartment does not exist.'
    return JsonResponse(data)

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
def profile(request, username):
    data = {}
    if User.objects.all().filter(username=username).exists():
        apts = Apartment.objects.all().filter(username=username).values()
        user = {}
        user['username'] = username
        user['email'] = User.objects.get(username=username).email
        data = {}
        data['valid'] = True
        data['user'] = user
        data['result'] = list(apts)
        print(data['result'])
    else:
        data['valid'] = False
        data['message'] = 'Apartment does not exist.'
    return JsonResponse(data)

@csrf_exempt
def user_profile(request):
    data = {}
    auth = request.POST.get('auth')
    if Authenticator.objects.all().filter(authenticator=auth).exists():
        user_id = Authenticator.objects.get(authenticator=auth).user_id
        if User.objects.all().filter(id=user_id).exists():
            user = User.objects.get(id=user_id)
            apts = Apartment.objects.all().filter(username=user.username).values()
            user_data = {}
            user_data['username'] = user.username
            user_data['email'] = user.email
            data = {}
            data['valid'] = True
            data['user'] = user_data
            data['result'] = list(apts)
            print(data['result'])
        else:
            data['valid'] = False
            data['message'] = 'Apartment does not exist.'
    else:
        data['valid'] = False
        data['message'] = 'Authenticator invalid.'
    return JsonResponse(data)

@csrf_exempt
def signup(request):
    data = {}
    if request.method == "POST":
        if User.objects.all().filter(username=request.POST.get('username')).exists():
            data['valid'] = False
            data['message'] = 'Username already exists.'
        elif User.objects.all().filter(email=request.POST.get('email')).exists():
            data['valid'] = False
            data['message'] = "Email already has an associated account."
        else:
            user = User()
            user.username = request.POST.get('username')
            user.password = request.POST.get('password')
            user.email = request.POST.get('email')
            user.save()

            authenticator = Authenticator()
            authenticator_value = hmac.new(
                key=settings.SECRET_KEY.encode('utf-8'),
                msg=os.urandom(32),
                digestmod='sha256',
            ).hexdigest()
            authenticator.authenticator = authenticator_value
            authenticator.user_id = user.id
            authenticator.save()

            jsondata = [{
                "username": user.username,
                'email': user.email
            }]
            data['valid'] = True
            data['message'] = 'Created new User.'
            data['result'] = jsondata
            data['authenticator'] = authenticator_value
    else:
        data['valid'] = False
        data['message'] = 'Not a POST request.'
    return JsonResponse(data)

@csrf_exempt
def login(request):
    data = {}
    if request.method == "POST":
        if not (User.objects.all().filter(username=request.POST.get('username')).exists()):
            data['valid'] = False
            data['message'] = 'Username does not exist.'
        else:
            user = User.objects.get(username=request.POST.get('username'))
            if check_password(request.POST.get('password'), user.password):
                if not (Authenticator.objects.all().filter(user_id=user.id).exists()):
                    authenticator = Authenticator()
                    authenticator_value = hmac.new(
                        key=settings.SECRET_KEY.encode('utf-8'),
                        msg=os.urandom(32),
                        digestmod='sha256',
                    ).hexdigest()
                    authenticator.authenticator = authenticator_value
                    authenticator.user_id = user.id
                    authenticator.save()

                    jsondata = [{
                        "username": user.username,
                        'id': user.id
                    }]
                    data['valid'] = True
                    data['message'] = 'User authenticated.'
                    data['result'] = jsondata
                    data['authenticator'] = authenticator_value
                else:
                    data['valid'] = True
                    data['message'] = 'User is already authenticated.'
                    data['authenticator'] = Authenticator.objects.get(user_id=user.id).authenticator
            else:
                data['valid'] = False
                data['message'] = 'Password incorrect.'
    else:
        data['valid'] = False
        data['message'] = 'Not a POST request.'
    return JsonResponse(data)

@csrf_exempt
def logout(request):
    data = {}
    if not (Authenticator.objects.all().filter(authenticator=request.POST.get('auth')).exists()):
        data['valid'] = False
        data['message'] = 'Authenticator does not exist.'
    else:
        auth = Authenticator.objects.get(authenticator=request.POST.get('auth'))
        auth.delete()
        data['valid'] = True
        data['message'] = 'Authenticator removed successfully';
    return JsonResponse(data)

@csrf_exempt
def auth(request):
    data = {}
    if not (Authenticator.objects.all().filter(authenticator=request.POST.get('auth')).exists()):
        data['valid'] = False
        data['message'] = 'Authenticator does not exist.'
    else:
        data['valid'] = True
        data['message'] = 'Authenticator exists';
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
        user_id = Authenticator.objects.get(authenticator=request.POST.get('auth')).user_id
        username = User.objects.get(id=user_id).username
        #checking if name already exists in database; no duplicate apartment posts allowed
        # if Apartment.objects.all().filter(name=request.POST.get('name')).exists():
        #     data['valid'] = False
        #     data['message'] = 'Apartment name already exists.  No duplicate entries are allowed.'
        # else:
        apt = Apartment()
        apt.name = request.POST.get('name', "")
        apt.price = request.POST.get('price', "")
        apt.username = username
        apt.save()
        jsondata = [{
            "name": apt.name,
            'id': apt.id,
            'price': apt.price,
            'username': apt.username,
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

