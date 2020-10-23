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


# Create your views here.
def index(request):
    #template  = loader.get_template('index_template/index.html')
    return HttpResponse('Hello')


########################
# 跟 crud_profile重複
########################
"""def get_profile(request):
    # print(request.body.decode('utf-8'))
    body = json.loads(request.body.decode('utf-8'))
    userIdToken = body['userIdToken']
    obj = User.objects.filter(userId=userIdToken).first()
    if obj == None:
        return JsonResponse({'noData':True})
    data = {
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
    return JsonResponse(data)
"""

def get_history(request):
    body = json.loads(request.body.decode('utf-8'))
    types = body['type']
    if types == 'seek':
        return get_employee_history(body)
    if types == 'provide':
        return get_employer_history(body)


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
    return JsonResponse({
        'count': obj.count(),
        'noData': True if obj.count() == 0 else False,
        'cases': cases,
    })


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
    return JsonResponse({
        'count': obj.count(),
        'noData': True if obj.count() == 0 else False,
        'cases': cases,
    })


def get_application_by_case_id(request):
    body = json.loads(request.body.decode('utf-8'))
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
    return JsonResponse({
        'count': child_obj.count(),
        'noData': True if child_obj.count() == 0 else False,
        'employees': applications,
    })


def search_case(request):
    body = json.loads(request.body.decode('utf-8'))
    #userId = body['userId']
    keyword = body['keyword']
    obj = Case.objects.all().order_by('-publishTime')
    obj_score = []
    offset = int(body['offset'])
    #if 'conditions'
    if 'conditions' in body:
        for key, value in body['conditions'].items():
            if key == 'location':
                obj = obj.filter(location__icontains=value)
            if key == 'status':
                obj = obj.filter(status__iexact=value)
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
        return JsonResponse({'nodata':True})
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


def get_case_by_case_id(request):
    body = json.loads(request.body.decode('utf-8'))
    caseId = body['caseId']
    obj = Case.objects.filter(id=caseId)
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
        for case in obj
    ]
    return JsonResponse({
        'count': obj.count(),
        'noData': True if obj.count() == 0 else False,
        'cases': cases,
    })


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
        return JsonResponse({
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
        })
    elif action == 'read':
        obj = User.objects.filter(userId=userIdToken).first()
        if obj == None:
            return JsonResponse({'noData':True})
        data = {
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
        return JsonResponse(data)
    elif action == 'delete':
        User.object.filter(userId=userIdToken).delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'noData': True})


def crud_case(request):
    body = json.loads(request.body.decode('utf-8'))
    action = body['action']
    caseId = body['caseId']
    if action == 'update' or action =='create':
        obj, created = Case.objects.update_or_create(id=caseId)
        if 'employerId' in body:
            obj.employerId=body['employerId']
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
        if 'publishTime' in body:
            obj.publishTime=body['publishTime']
        if 'modifiedTime' in body:
            obj.modifiedTime=body['modifiedTime']
        obj.save()
        return JsonResponse({
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
        })
    elif action == 'read':
        obj = Case.objects.filter(id=caseId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        data = {
            
            'noDate': False,
            'employerId': obj.employerId,
            'title': obj.title,
            'text': obj.text,
            'location': obj.location,
            'pay': obj.pay,
            'status': obj.status,
            'publishTime': obj.publishTime,
            'modifiedTime': obj.modifiedTime,
            'caseId': obj.id,
        }
        return JsonResponse(data)
    elif action == 'delete':
        Case.object.filter(id=caseId).delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'noData': True})


def crud_application(request):
    body = json.loads(request.body.decode('utf-8'))
    action = body['action']
    caseId = body['caseId']
    employeeId = body['employeeId']
    if action == 'update' or action =='create':
        obj, created = Case.objects.update_or_create(caseId=caseId, employeeId=employeeId)
        if 'message' in body:
            obj.message=body['message']
        if 'accepted' in body:
            obj.accepted=body['accepted']
            if body['accpeted'] == True:
                # call line-bot 傳給使用者
                # coding here ........
                pass
        if 'employerRating' in body:
            obj.employerRating=body['employerRating']
        if 'employeeRating' in body:
            obj.employeeRating=body['employeeRating']
        obj.save()
        return JsonResponse({
            'noDate': False,
            'caseId': obj.caseId.id,
            'employeeId': obj.employeeId.userId,
            'message': obj.message,
            'accepted': obj.accepted,
            'employerRating': obj.employerRating,
            'employeeRating': obj.employeeRating,
        })
    elif action == 'read':
        obj = Application.objects.filter(caseId__id=caseId).filter(employeeId__userId=employeeId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        data = {
            'noDate': False,
            'caseId': obj.caseId.id,
            'employeeId': obj.employeeId.userId,
            'message': obj.message,
            'accepted': obj.accepted,
            'employerRating': obj.employerRating,
            'employeeRating': obj.employeeRating,
        }
        return JsonResponse(data)
    elif action == 'delete':
        Application.object.filter(caseId__id=caseId).filter(employeeId__userId=employeeId).delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'noData': True})
    pass



######################
# API for line-bot
######################
def recommanded_cases(userIdToken):
    gender_exclude = {'M':'限女', 'F':'限男', 'O':'', '':''}
    user_obj = User.objects.filter(userId=userIdToken)
    if user_obj.count() != 1:
        return None
    user_obj = user_obj.first()
    intro = set(analyse.extract_tags(user_obj.intro))
    gender = gender_exclude[user_obj.gender]
    county = user_obj.county
    cases_obj = Case.objects.filter(status='O').exclude(title__iregex=gender).exclude(text__iregex=gender)
    cases_score = [0.0 for case in range(cases_obj.count())]
    for idx, case in enumerate(cases_obj):
        title = set(analyse.extract_tags(case.title))
        text = set(analyse.extract_tags(case.title))
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