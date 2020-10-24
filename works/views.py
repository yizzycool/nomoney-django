from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone as tz
import os
import sqlite3
from time import gmtime, strftime
from works.models import User, Case, Application
import json
from django.template import Context, loader
from jieba import analyse
from . import utils 
from .push import notify_acceptance, notify_application


# API
def index(request):
    #template  = loader.get_template('index_template/index.html')
    return HttpResponse('Hello')


# API
def get_history(request):
    body = json.loads(request.body.decode('utf-8'))
    types = body['type']
    if types == 'seek':
        return JsonResponse(get_employee_history(body))
    if types == 'provide':
        return JsonResponse(get_employer_history(body))


# Function
def get_employee_history(body):
    userIdToken = body['userIdToken']
    # order by ...
    order_list = {'O':3, 'C':2, 'D':1}
    obj = Application.objects.filter(employeeId__userId=userIdToken).all()
    sorted_obj = sorted(obj, key=lambda x: (order_list[x.caseId.status], x.caseId.publishTime), reverse=True)
    cases = [
        {
            'employer':{
                #------ Employer part ------#
                'employerId': app.caseId.employerId.userId,
                'displayName': app.caseId.employerId.displayName,
                'image': app.caseId.employerId.image,
            },
            'employee':{
                #------ Employee part ------#
                'employeeId': app.employeeId.userId,
                'message': app.message,
                'accepted': app.accepted,
                'employerRating': app.employerRating,
                'employeeRating': app.employeeRating,
            },
            'title': app.caseId.title,
            'text': app.caseId.text,
            'location': app.caseId.location,
            'pay': app.caseId.pay,
            'status': app.caseId.status,
            'publishTime': tz.localtime(app.caseId.publishTime),
            'modifiedTime': tz.localtime(app.caseId.modifiedTime),
            'caseId': app.caseId.id,
        }
        for app in sorted_obj
    ]
    return {
        'count': obj.count(),
        'noData': True if obj.count() == 0 else False,
        'cases': cases,
    }


# Function
def get_employer_history(body):
    userIdToken = body['userIdToken']
    # order by ...
    order_list = {'O':3, 'C':2, 'D':1}
    #obj = Case.objects.filter(employerId__userId=userIdToken).extra(select={'o':'(case when status="O" then 1 when status="C" then 2 when status="D" then 3 end)'}, order_by=['o', '-publishTime']).all()
    obj = Case.objects.filter(employerId__userId=userIdToken).all()
    sorted_obj = sorted(obj, key=lambda x: (order_list[x.status], x.publishTime), reverse=True)
    #obj = Case.objects.filter(employerId__userId=userIdToken).order_by('-publishTime')
    cases = [
        {
            'employer':{
                #------ Employer part ------#
                'employerId': case.employerId.userId,
                'displayName': case.employerId.displayName,
                'image': case.employerId.image,
                'gender': case.employerId.gender,
                'phone': case.employerId.phone,
                'rating': case.employerId.rating,
                'lineId': case.employerId.lineId,
            },
            'title': case.title,
            'text': case.text,
            'location': case.location,
            'pay': case.pay,
            'status': case.status,
            'publishTime': tz.localtime(case.publishTime),
            'modifiedTime': tz.localtime(case.modifiedTime),
            'caseId': case.id,
        }
        for case in sorted_obj
    ]
    return {
        'count': obj.count(),
        'noData': True if obj.count() == 0 else False,
        'cases': cases,
    }


# Function
def get_application_by_case_id(body):
    #body = json.loads(request.body.decode('utf-8'))
    caseId = body['caseId']
    obj = Case.objects.filter(id=caseId).first()
    if obj == None: return JsonResponse({'noData':True})
    child_obj = obj.application_set.all().order_by('-id')
    applications = [
        {
            'caseId': obj.caseId.id,
            'employeeId': obj.employeeId.userId,
            'displayName': obj.employeeId.displayName,
            'message': obj.message,
            'accepted': obj.accepted,
            'employerRating': obj.employeeRating,
            'employerRating': obj.employerRating,
        }
        for obj in child_obj
    ]
    return {
        'count': child_obj.count(),
        'applications': applications,
    }


# API
def get_case_by_case_id(request):
    body = json.loads(request.body.decode('utf-8'))
    caseId = body['caseId']
    userIdToken = body['userIdToken']
    obj = Case.objects.filter(id=caseId)
    if obj.count() != 1: return JsonResponse({'noData': True})
    obj = obj.first()
    isOwner = True if userIdToken == obj.employerId.userId else False
    applications = get_application_by_case_id(body)
    case = {
        'noData': True,
        'employer':{
            #------ Employer part ------#
            'employerId': obj.employerId.userId,
            'displayName': obj.employerId.displayName,
            'image': obj.employerId.image,
            'gender': obj.employerId.gender,
            'phone': obj.employerId.phone,
            'rating': obj.employerId.rating,
            'lineId': obj.employerId.lineId,
        },
        'title': obj.title,
        'text': obj.text,
        'location': obj.location,
        'pay': obj.pay,
        'status': obj.status,
        'publishTime': tz.localtime(obj.publishTime),
        'modifiedTime': tz.localtime(obj.modifiedTime),
        'caseId': obj.id,
        'isOwner': isOwner,
        #------ Employee Data ------#
        'count': applications['count'],
        'applications':applications['applications'],
    }
    return JsonResponse(case)


# API
def search_case(request):
    body = json.loads(request.body.decode('utf-8'))
    userIdToken = body['userIdToken']
    keyword = body['keyword']
    print(userIdToken)
    obj = Case.objects.all().order_by('-publishTime')
    # 過濾掉已關閉的
    obj = obj.filter(status='O')
    # 過濾掉自己發的
    obj = obj.exclude(employerId__userId=userIdToken)
    # 過濾掉已經應徵的
    applications = list(set([app.caseId.id for app in Application.objects.filter(employeeId__userId=userIdToken).all()]))
    obj = obj.exclude(id__in=applications)
    obj_score = []
    offset = int(body['offset'])
    #if 'conditions'
    if 'conditions' in body:
        for key, value in body['conditions'].items():
            if key == 'location':
                obj = obj.filter(location__icontains=value)
            if key == 'minpay':
                obj = obj.filter(pay__gt=int(value))
            if key == 'maxpay':
                obj = obj.filter(pay__lt=int(value))
    if keyword != '':
        title_obj = obj.filter(title__icontains=keyword)
        if title_obj.count() != 0:
            obj = title_obj
        else:
            obj = obj.filter(text__icontains=keyword)
    if obj.count() == 0:
        return JsonResponse({'noData':True})
    else:
        total_match = obj.count()
        obj = obj[offset:offset+10]
        cases = [
            {
                'caseId': case.id,
                'employerId': case.employerId.userId,
                'displayName': case.employerId.displayName,
                'title': case.title,
                'text': case.text,
                'location': case.location,
                'pay': case.pay,
                'status': case.status,
                'publishTime': tz.localtime(case.publishTime),
                'modifiedTime': tz.localtime(case.modifiedTime),
            }
            for case in obj
        ]
        return JsonResponse({
            'count': total_match,
            'noData': True if obj.count() == 0 else False,
            'offset': offset,
            'cases': cases,
        })


# Function
def get_crud_profile(obj):
    return {
        'noDate': False,
        'userId': obj.userId,
        'displayName': obj.displayName,
        'image': obj.image,
        'intro': obj.intro,
        'gender': obj.gender,
        'birthday': obj.birthday,
        'phone': obj.phone,
        'county': obj.county,
        'rating': obj.rating,
        'lineId': obj.lineId,
    }
    pass


# Function
def put_crud_profile(obj_raw, body):
    obj = obj_raw
    if 'displayName' in body:
        obj.displayName=body['displayName']
    if 'image' in body:
        obj.image=body['image']
    if 'intro' in body:
        obj.intro=body['intro']
    if 'gender' in body:
        obj.gender=body['gender']
    if 'birthday' in body:
        obj.birthday=body['birthday']
    if 'phone' in body:
        obj.phone=body['phone']
    if 'contry' in body:
        obj.county=body['county']
    if 'rating' in body:
        obj.rating=body['rating']
    if 'lineId' in body:
        obj.lineId=body['lineId']
    return obj


# API
def crud_profile(request):
    body = json.loads(request.body.decode('utf-8'))
    action = body['action']
    userIdToken = body['userIdToken']
    if action == 'update' or action =='create':
        obj, created = User.objects.update_or_create(userId=userIdToken)
        if 'displayName' in body:
            obj.displayName=body['displayName']
        if 'image' in body:
            obj.image=body['image']
        if 'intro' in body:
            obj.intro=body['intro']
        if 'gender' in body:
            obj.gender=body['gender']
        if 'birthday' in body:
            obj.birthday=body['birthday']
        if 'phone' in body:
            obj.phone=body['phone']
        if 'contry' in body:
            obj.county=body['county']
        if 'rating' in body:
            obj.rating=body['rating']
        if 'lineId' in body:
            obj.lineId=body['lineId']
        obj.save()
        return JsonResponse(get_crud_profile(obj))
    elif action == 'read':
        obj = User.objects.filter(userId=userIdToken).first()
        if obj == None:
            return JsonResponse({'noData':True})
        return JsonResponse(get_crud_profile(obj))
    elif action == 'delete':
        User.object.filter(userId=userIdToken).delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'noData': True})


# Function
def get_crud_case(obj):
    return {
        'noDate': False,
        'employerId': obj.employerId.userId,
        'title': obj.title,
        'text': obj.text,
        'location': obj.location,
        'pay': obj.pay,
        'status': obj.status,
        'publishTime': obj.publishTime,
        'modifiedTime': obj.modifiedTime,
        'caseId': obj.id,
    }


def crud_case(request):
    body = json.loads(request.body.decode('utf-8'))
    action = body['action']
    caseId = body['caseId']
    if action == 'create':
        obj = Case()
        if 'employerId' in body:
            obj.employerId = User.objects.get(userId=body['employerId'])
        if 'title' in body:
            obj.title=body['title']
        if 'text' in body:
            obj.text=body['text']
        if 'location' in body:
            obj.location=body['location']
        if 'pay' in body:
            obj.pay=body['pay']
        if 'status' in body:
            obj.status=body['status']
        localtime = tz.localtime(tz.now())
        obj.publishTime = localtime
        obj.modifiedTime = localtime
        obj.save()
        return JsonResponse(get_crud_case(obj))
    elif action == 'update':
        obj, created = Case.objects.update_or_create(id=caseId)
        if 'employerId' in body:
            obj.employerId = User.objects.get(userId=body['employerId'])
        if 'title' in body:
            obj.title=body['title']
        if 'text' in body:
            obj.text=body['text']
        if 'location' in body:
            obj.location=body['location']
        if 'pay' in body:
            obj.pay=body['pay']
        if 'status' in body:
            obj.status=body['status']
        obj.modifiedTime = tz.localtime(tz.now())
        obj.save()
        return JsonResponse(get_crud_case(obj))
    elif action == 'read':
        obj = Case.objects.filter(id=caseId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        return JsonResponse(get_crud_case(obj))
    elif action == 'delete':
        userIdToken = body['userIdToken']
        Case.objects.filter(id=caseId).delete()
        cases = get_employer_history({'userIdToken':userIdToken})
        return JsonResponse({
            'success': True,
            'count': cases['count'],
            'noData': cases['noData'],
            'cases': cases['cases'], 
            })
    else:
        return JsonResponse({'noData': True})


# Function
def get_crud_application(obj):
    return {
        'noDate': False,
        'caseId': obj.caseId.id,
        'employeeId': obj.employeeId.userId,
        'message': obj.message,
        'accepted': obj.accepted,
        'employerRating': obj.employerRating,
        'employeeRating': obj.employeeRating,
    }


# API
def crud_application(request):
    body = json.loads(request.body.decode('utf-8'))
    action = body['action']
    caseId = body['caseId']
    employeeId = body['employeeId']
    if action == 'create':
        obj = Application()
        obj.caseId = Case.objects.get(id = caseId)
        obj.employeeId = User.objects.get(userId = employeeId)
        if 'message' in body:
            obj.message=body['message']
        return JsonResponse(get_crud_application(obj))
    elif action == 'update':
        print('UPDATE')
        obj = Application.objects.filter(caseId__id=caseId, employeeId__userId=employeeId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        if 'message' in body:
            obj.message=body['message']
        if 'accepted' in body:
            obj.accepted=body['accepted']
            if body['accepted'] == True:
                print()
                call_linebot_notify_acceptance(employeeId, obj)
        if 'employerRating' in body:
            obj.employerRating=body['employerRating']
        if 'employeeRating' in body:
            obj.employeeRating=body['employeeRating']
        obj.save()
        return JsonResponse(get_crud_application(obj))
    elif action == 'read':
        obj = Application.objects.filter(caseId__id=caseId).filter(employeeId__userId=employeeId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        return JsonResponse(get_crud_application(obj))
    elif action == 'delete':
        Application.objects.filter(caseId__id=caseId).filter(employeeId__userId=employeeId).delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'noData': True})


######################
# API for line-bot
######################
def recommanded_cases(userIdToken):
    gender_exclude = {'M':'限女', 'F':'限男', 'O':'', '':''}
    user_obj = User.objects.filter(userId=userIdToken)
    if user_obj.count() != 1:
        return None
    user_obj = user_obj.first()
    # 用 monpy 取出好的詞彙
    intro = set(utils.extract_tokens(user_obj.intro))
    print(intro)
    gender = gender_exclude[user_obj.gender]
    county = user_obj.county
    # 過濾已經關閉的 / 自己發的案件
    cases_obj = Case.objects.filter(status='O').exclude(employerId__userId=userIdToken)
    # 過濾掉已經應徵的
    applications = list(set([app.caseId.id for app in Application.objects.filter(employeeId__userId=userIdToken).all()]))
    cases_obj = cases_obj.exclude(id__in=applications)
    if gender != '':
        cases_obj.exclude(title__icontains=gender).exclude(text__icontains=gender)
    print(cases_obj)
    cases_score = [0.0 for case in range(cases_obj.count())]
    for idx, case in enumerate(cases_obj):
        title = set(utils.extract_tokens(case.title))
        text = set(utils.extract_tokens(case.title))
        location = case.location
        pay = int(case.pay)
        cases_score[idx] += min(len(intro&title) * 2, 9999)
        cases_score[idx] += min(len(intro&text), 9999)
        if county == location:
            cases_score[idx] += 9999
        
    cases = [{
        'caseId': case.id,
        'title': case.title.strip(),
        'description': case.text.strip(),
        'pay': case.pay,
        'publishTime': case.publishTime,
        'location': case.location,
        'matchScore': cases_score[idx],
    } for idx, case in enumerate(cases_obj)
    ][:5]
    cases = sorted(cases, key=lambda x: (x['matchScore'], x['publishTime']), reverse=True)
    return cases


# Function
def call_linebot_notify_acceptance(employeeId, obj):
    # call line-bot notify_acceptance
    case = {
        'title': obj.caseId.title,
        'description': obj.caseId.text,
    }
    user = {
        'phone_number': obj.caseId.employerId.phone,
        'lineid': obj.caseId.employerId.lineId,
    }
    notify_acceptance(employeeId, case, user)
    return