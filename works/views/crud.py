import json
### Django ###
from django.http import HttpResponse, JsonResponse
from django.utils import timezone as tz
### Django Models ###
from works.models import User, Case, Application, Hashtag, MiddleAgent
### My Function ###
from works.views.linebot_api import call_linebot_notify_acceptance, call_linebot_notify_application
from works.views.get_case import get_case_by_case_id
from works.views.history import get_employer_history
from works.functions.render_dict import get_crud_profile, get_crud_case, get_crud_application
from works.functions import utils


# API
def crud_profile(request):
    post = json.loads(request.body.decode('utf-8'))
    action = post.get('action')
    userIdToken = post.get('userIdToken')
    if not action or not userIdToken:
        return HttpResponse(status = 400)
    isNewUser = False
    if action == 'create' or action == 'update':
        if User.objects.filter(userId=userIdToken).count() == 0:
            obj = User(userId=userIdToken)
            isNewUser = True
        else:
            obj = User.objects.get(userId=userIdToken)
        if action == 'create' and not isNewUser:
            return JsonResponse(get_crud_profile(obj))
        if 'displayName' in post:
            obj.displayName = post['displayName']
        if 'image' in post:
            obj.image = post['image']
        if 'intro' in post:
            obj.intro = post['intro']
        if 'gender' in post:
            obj.gender = post['gender']
        if 'birthday' in post:
            obj.birthday = post['birthday']
        if 'phone' in post:
            obj.phone = post['phone']
        if 'county' in post:
            obj.county = post['county']
        if 'rating' in post:
            obj.rating = post['rating']
        if 'lineId' in post:
            obj.lineId = post['lineId']
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


# API
def crud_case(request):
    post = json.loads(request.body.decode('utf-8'))
    action = post.get('action')
    caseId = post.get('caseId')
    if not action or caseId == None:
        return HttpResponse(status = 400)
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
        if 'employerId' in post:
            obj.employerId = User.objects.get(userId=post['employerId'])
        if 'title' in post:
            obj.title = post['title']
        if 'text' in post:
            obj.text = post['text']
        if 'location' in post:
            obj.location = post['location']
        if 'pay' in post:
            obj.pay = post['pay']
        if 'status' in post:
            obj.status = post['status']
        obj.save()
        # New func: add keywords as hashtag
        if 'title' in post or 'text' in post or 'updateHashtag' in post:
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
        userIdToken = post['userIdToken']
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



# API
def crud_application(request):
    post = json.loads(request.body.decode('utf-8'))
    action = post.get('action')
    caseId = post.get('caseId')
    #employeeId = post.get('employeeId')
    userIdToken = post.get('userIdToken')
    appId = post.get('appId')
    if not action or not caseId or not appId or not userIdToken:
        return HttpResponse(status = 400)
    appId = int(appId)
    if action == 'create':
        if Application.objects.filter(caseId__id=caseId, id=appId):
            return JsonResponse({
                'error': 'duplicated'
            })
        obj = Application()
        obj.caseId = Case.objects.get(id = caseId)
        obj.employeeId = User.objects.get(userId = userIdToken)
        if 'message' in post:
            obj.message=post['message']
        obj.save()
        # call line bot to send notification
        try:
            call_linebot_notify_application(obj.caseId.employerId.userId, obj)
        except:
            pass
        return JsonResponse(get_crud_application(obj))
    # "UPDATE" is Only for employer
    if action == 'update':
        obj = Application.objects.filter(caseId__id=caseId, id=appId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        if 'message' in post:
            obj.message=post['message']
        if 'accepted' in post:
            obj.accepted=post['accepted']
            if post['accepted'] == "A":
                # call line bot to send notification
                try:
                    call_linebot_notify_acceptance(obj.employeeId.userId, obj)
                except:
                    pass
        if 'employerRating' in post:
            obj.employerRating=post['employerRating']
        if 'employeeRating' in post:
            obj.employeeRating=post['employeeRating']
        obj.save()
        return get_case_by_case_id(request)
    if action == 'read':
        obj = Application.objects.filter(caseId__id=caseId).filter(id=appId).first()
        if obj == None:
            return JsonResponse({'noData':True})
        return JsonResponse(get_crud_application(obj))
    if action == 'delete':
        Application.objects.filter(caseId__id=caseId).filter(id=appId).delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'noData': True})
