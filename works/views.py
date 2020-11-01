from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone as tz
import os
import sqlite3
from time import gmtime, strftime
from works.models import User, Case, Application, Hashtag, MiddleAgent
import json
from django.template import Context, loader
from . import utils 
from .push import notify_acceptance, notify_application
import requests


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
            'hashtag': [ mid_obj.hashtag.tag for mid_obj in app.caseId.middleagent_set.all() ]
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
                #'gender': case.employerId.gender,
                #'phone': case.employerId.phone,
                #'rating': case.employerId.rating,
                #'lineId': case.employerId.lineId,
            },
            'title': case.title,
            'text': case.text,
            'location': case.location,
            'pay': case.pay,
            'status': case.status,
            'publishTime': tz.localtime(case.publishTime),
            'modifiedTime': tz.localtime(case.modifiedTime),
            'caseId': case.id,
            'hashtag': [ mid_obj.hashtag.tag for mid_obj in case.middleagent_set.all() ],
        }
        for case in sorted_obj
    ]
    return {
        'count': obj.count(),
        'noData': True if obj.count() == 0 else False,
        'cases': cases,
    }


# Function
def get_application_by_case_id(body, isOwner):
    #body = json.loads(request.body.decode('utf-8'))
    caseId = body['caseId']
    userIdToken = body['userIdToken']
    obj = Case.objects.filter(id=caseId).first()
    if obj == None: return JsonResponse({'noData':True})
    if isOwner:
        child_obj = obj.application_set.all().order_by('-id')
    else:
        child_obj = obj.application_set.all().filter(employeeId__userId=userIdToken).order_by('-id')
    applications = [
        {
            'caseId': obj.caseId.id,
            'employeeId': obj.employeeId.userId,
            'displayName': obj.employeeId.displayName,
            'message': obj.message,
            'accepted': obj.accepted,
            'employerRating': obj.employeeRating,
            'employerRating': obj.employerRating,
            'phone': obj.employeeId.phone if obj.accepted == 'A' else '',
            'lineId': obj.employeeId.lineId,
        }
        for obj in child_obj
    ]
    for app in applications:
        if app['accepted'] != 'A':
            app.pop('phone', None)
            app.pop('lineId', None)
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
    # 判斷是否為 Owner
    isOwner = True if userIdToken == obj.employerId.userId else False
    applications = get_application_by_case_id(body, isOwner)
    case = {
        'noData': False,
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
        'hashtag': [ mid_obj.hashtag.tag for mid_obj in obj.middleagent_set.all() ],
        #------ Employee Data ------#
        'count': applications['count'],
        'applications':applications['applications'],
        'recommendations':[]
    }
    app_obj = Application.objects.filter(employeeId__userId=userIdToken, caseId__id=caseId).first()
    if not isOwner and app_obj and app_obj.accepted != 'A':
        case['employer'].pop('image', None)
        case['employer'].pop('phone', None)
        case['employer'].pop('lineId', None)
    if len(case['hashtag']) == 0:
        return JsonResponse(case)
    rec_data = {
        "userIdToken": userIdToken,
        "keyword": ' '.join(case['hashtag']),
        "offset": 0
    }
    rec_response = requests.post('https://nomoney.nlplab.cc/api/search_case', json.dumps(rec_data), headers={os.getenv('CHECK_KEY'):os.getenv('CHECK_VALUE')})
    rec = json.loads(rec_response.text)
    if rec['noData']:
        return JsonResponse(case)
    else:
        rec['cases'] = [r for r in rec['cases'] if r['caseId']!=case['caseId']]
        for rec_case in rec['cases'][:5]:
            case['recommendations'].append({
                'caseId': rec_case['caseId'],
                'title': rec_case['title'],
                'location': rec_case['location'],
                'pay': rec_case['pay']
                })
    return JsonResponse(case)


# API
def search_case(request):
    body = json.loads(request.body.decode('utf-8'))
    userIdToken = body['userIdToken']
    keyword = body['keyword'].split()
    offset = int(body['offset'])
    obj = Case.objects.all().order_by('-publishTime')
    # 過濾掉已關閉的
    obj = obj.filter(status='O')
    # 過濾掉自己發的
    obj = obj.exclude(employerId__userId=userIdToken)
    # If condition
    if 'conditions' in body:
        for key, value in body['conditions'].items():
            if key == 'location' and value != '':
                locationCounty, locationDistrict = value.split('/')
                if locationCounty == '全部': pass
                elif locationDistrict == '全部':
                    obj = obj.filter(location__istartswith=locationCounty) | obj.filter(location__istartswith='全部')
                else:
                    obj = obj.filter(location=value) | obj.filter(location=locationCounty+'/全部') | obj.filter(location__istartswith='全部')
            if key == 'minpay':
                obj = obj.filter(pay__gte=int(value))
            if key == 'maxpay':
                obj = obj.filter(pay__lte=int(value))
    if obj.count() == 0:
        return JsonResponse({'noData': True})
    # New Func: hashtags
    if len(keyword) != 0:
        tags = [tok[1:] for tok in keyword if tok[0] == '#']
        keyword = [tok for tok in keyword if tok[0] != '#']
        obj_score = [0.0 for _ in range(obj.count())]
        for idx, case in enumerate(obj):
            case_tags = set([mid.hashtag.tag for mid in case.middleagent_set.all()])
            obj_score[idx] += len(set(tags)&case_tags) * 100
            title = set(utils.extract_tokens(case.title))
            text = set(utils.extract_tokens(case.text))
            obj_score[idx] += len(set(keyword)&title) * 2
            obj_score[idx] += len(set(keyword)&text)
        cases = [
            {
                'matchScore' : obj_score[idx],
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
                'hashtag': [ mid_obj.hashtag.tag for mid_obj in case.middleagent_set.all() ]
            }
            for idx, case in enumerate(obj)
        ]
        cases = list(filter(lambda x: x['matchScore'] > 0, cases))
        if len(cases) == 0: return JsonResponse({ 'noData': True })
        cases = sorted(cases, key=lambda x: x['matchScore'], reverse=True)
        return JsonResponse({
            'count': len(cases),
            'noData': False,
            'offset': offset,
            'cases': cases,#[offset:offset+10],
        })
    else:
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
                'hashtag': [ mid_obj.hashtag.tag for mid_obj in case.middleagent_set.all() ]
            }
            for case in obj
        ]
        return JsonResponse({
            'count': len(cases),
            'noData': False,
            'offset': offset,
            'cases': cases,#[offset:offset+10],
        })


# Function
def get_crud_profile(obj):
    return {
        'noData': False,
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


# API
def crud_profile(request):
    body = json.loads(request.body.decode('utf-8'))
    action = body['action']
    userIdToken = body['userIdToken']
    isNewUser = False
    if action == 'create' or action == 'update':
        if User.objects.filter(userId=userIdToken).count() == 0:
            obj = User(userId=userIdToken)
            isNewUser = True
        else:
            obj = User.objects.get(userId=userIdToken)
        if action == 'create' and not isNewUser:
            return JsonResponse(get_crud_profile(obj))
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
        if 'county' in body:
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
        'noData': False,
        'employerId': obj.employerId.userId,
        'title': obj.title,
        'text': obj.text,
        'location': obj.location,
        'pay': obj.pay,
        'status': obj.status,
        'publishTime': obj.publishTime,
        'modifiedTime': obj.modifiedTime,
        'caseId': obj.id,
        'hashtag': [ 
            mid_obj.hashtag.tag for mid_obj in obj.middleagent_set.all()
        ]
    }


def crud_case(request):
    body = json.loads(request.body.decode('utf-8'))
    action = body['action']
    caseId = body['caseId']
    if action == 'create':
        obj = Case()
        localtime = tz.localtime(tz.now())
        obj.publishTime = localtime
        obj.modifiedTime = localtime
    elif action == 'update':
        obj = Case.objects.filter(id=caseId).first()
        if obj == None: return JsonResponse({'noData':True})
        #obj.modifiedTime = tz.localtime(tz.now())
    if action == 'create' or action == 'update':
        if 'employerId' in body:
            obj.employerId = User.objects.get(userId=body['employerId'])
        if 'title' in body:
            obj.title = body['title']
        if 'text' in body:
            obj.text = body['text']
        if 'location' in body:
            obj.location = body['location']
        if 'pay' in body:
            obj.pay = body['pay']
        if 'status' in body:
            obj.status = body['status']
        obj.save()
        # New func: add keywords as hashtag
        if 'title' in body or 'text' in body or 'updateHashtag' in body:
            # Before hashtag: delete old hashtag if exist
            for mid in obj.middleagent_set.all():
                hash_obj = Hashtag.objects.filter(id=mid.hashtag.id).first()
                if hash_obj:
                    hash_obj.count = max( 0, hash_obj.count - 1 )
                    hash_obj.save()
                    if hash_obj.count < 1:
                        hash_obj.delete()
                mid.delete()
            content = obj.title + '\n' + obj.text
            tok_pos = utils.extract_tokens_pos(content)
            keywords = utils.chi_square_test(tok_pos)
            for keyword, _, _ in keywords:
                # save hash tag here
                hash_obj = Hashtag.objects.filter(tag = keyword).first()
                if hash_obj == None:
                    hash_obj = Hashtag(tag = keyword, count = 1)
                    hash_obj.save()
                    middle_agent = MiddleAgent(case = obj, hashtag = hash_obj)
                    middle_agent.save()
                else:
                    hash_obj.count += 1
                    hash_obj.save()
                    middle_obj = MiddleAgent.objects.filter(case__id = obj.id, hashtag__tag = keyword).first()
                    if middle_obj == None:
                        middle_obj = MiddleAgent(case = obj, hashtag = hash_obj)
                        middle_obj.save()
        return JsonResponse(get_crud_case(obj))
    elif action == 'read':
        obj = Case.objects.filter(id=caseId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        return JsonResponse(get_crud_case(obj))
    elif action == 'delete':
        userIdToken = body['userIdToken']
        # 先判斷 hash tag 需不需要刪除
        for mid in Case.objects.filter(id=caseId).first().middleagent_set.all():
            hash_obj = Hashtag.objects.filter(id=mid.hashtag.id).first()
            if hash_obj:
                hash_obj.count = max( 0, hash_obj.count - 1 )
                hash_obj.save()
                if hash_obj.count == 0:
                    hash_obj.delete()
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
        'noData': False,
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
        if Application.objects.filter(caseId__id=caseId, employeeId__userId=employeeId):
            return JsonResponse({
                'error': 'duplicated'
            })
        obj = Application()
        obj.caseId = Case.objects.get(id = caseId)
        obj.employeeId = User.objects.get(userId = employeeId)
        if 'message' in body:
            obj.message=body['message']
        obj.save()
        # call line bot to send notification
        try:
            call_linebot_notify_application(obj.caseId.employerId.userId, obj)
        except:
            pass
        return JsonResponse(get_crud_application(obj))
    # "UPDATE" is Only for employer
    if action == 'update':
        obj = Application.objects.filter(caseId__id=caseId, employeeId__userId=employeeId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        if 'message' in body:
            obj.message=body['message']
        if 'accepted' in body:
            obj.accepted=body['accepted']
            if body['accepted'] == "A":
                # call line bot to send notification
                try:
                    call_linebot_notify_acceptance(employeeId, obj)
                except:
                    pass
        if 'employerRating' in body:
            obj.employerRating=body['employerRating']
        if 'employeeRating' in body:
            obj.employeeRating=body['employeeRating']
        obj.save()
        return get_case_by_case_id(request)
    if action == 'read':
        obj = Application.objects.filter(caseId__id=caseId).filter(employeeId__userId=employeeId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        return JsonResponse(get_crud_application(obj))
    if action == 'delete':
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
    gender = gender_exclude[user_obj.gender]
    county = user_obj.county.split('/')
    # 過濾已經關閉的 / 自己發的案件
    cases_obj = Case.objects.filter(status='O').exclude(employerId__userId=userIdToken)
    # 過濾掉已經應徵的
    applications = list(set([app.caseId.id for app in Application.objects.filter(employeeId__userId=userIdToken).all()]))
    cases_obj = cases_obj.exclude(id__in=applications)
    if gender != '':
        cases_obj.exclude(title__icontains=gender).exclude(text__icontains=gender)
    cases_score = [0.0 for case in range(cases_obj.count())]
    for idx, case in enumerate(cases_obj):
        title = set(utils.extract_tokens(case.title))
        text = set(utils.extract_tokens(case.text))
        location = case.location.split('/')
        pay = int(case.pay)
        cases_score[idx] += min(len(intro&title) * 2, 9999)
        cases_score[idx] += min(len(intro&text), 9999)
        if len(county) == 2 and len(location) == 2:
            if county[0] == location[0]:
                if county[1] == location[1]:
                    cases_score[idx] += 9999
                elif county[1] == '全部' or location == '全部':
                    cases_score[idx] += 8000
                else:
                    cases_score[idx] += 5000
            elif county[0] == '全部' or location[0] == '全部':
                cases_score[idx] += 5000
    cases = [{
        'caseId': case.id,
        'title': case.title.strip(),
        'description': case.text.strip(),
        'pay': case.pay,
        'publishTime': case.publishTime,
        'location': case.location,
        'matchScore': cases_score[idx],
        'url': 'https://liff.line.me/1655089903-YawqnnaN/case?caseId='+str(case.id) ,
    } for idx, case in enumerate(cases_obj)
    ]
    cases = sorted(cases, key=lambda x: (x['matchScore'], x['publishTime']), reverse=True)[:5]
    return cases


# Function  ->  curd_application : 'update'
def call_linebot_notify_acceptance(employeeId, obj):
    # call line-bot notify_acceptance
    case = {
        'title': obj.caseId.title,
        'description': obj.caseId.text,
        'url': "https://liff.line.me/1655089903-YawqnnaN/case?caseId="+str(obj.caseId.id)
    }
    user = {
        'phone_number': obj.caseId.employerId.phone,
        'lineid': obj.caseId.employerId.lineId,
    }
    notify_acceptance(employeeId, case, user)
    return


# Function  ->  curd_application : 'create'
def call_linebot_notify_application(employeeId, obj):
    # call line-bot notify_application
    case = {
        'title': obj.caseId.title,
        'url': "https://liff.line.me/1655089903-YawqnnaN/case?caseId="+str(obj.caseId.id)
    }
    application = {
        'description': obj.message,
        'image': obj.employeeId.image,
    }
    notify_application(employeeId, case, application)
    return


# Owner function: delete null hashtag
"""def delete_hashtag(request):
    hash_obj = Hashtag.objects.filter(count__lt=1).all()
    delete_num = [(obj.tag, obj.count) for obj in hash_obj]
    for obj in hash_obj:
        obj.delete()
    hash_obj = Hashtag.objects.filter(count__gte=1).all()
    for obj in hash_obj:
        obj.count = len(obj.middleagent_set.all())
        obj.save()
        if obj.count < 1:
            obj.delete()
    return JsonResponse({'delete_sets':delete_num})"""