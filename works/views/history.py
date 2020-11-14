import json
### Django ###
from django.http import HttpResponse, JsonResponse
### Django Models ###
from works.models import User, Case, Application, Hashtag, MiddleAgent


# API
def get_history(request):
    post = json.loads(request.body.decode('utf-8'))
    types = post.get('type')
    if types == 'seek':
        return JsonResponse(get_employee_history(post))
    elif types == 'provide':
        return JsonResponse(get_employer_history(post))
    else:
        return HttpResponse(status=400)


# Function
def get_employee_history(post):
    userIdToken = post['userIdToken']
    # order by OPEN -> CLOSE -> DELETE
    order_list = {'O':3, 'C':2, 'D':1}
    obj = Application.objects.filter(employeeId__userId=userIdToken).all()
    # if no data
    if obj == None:
        return JsonResponse({'noData': True})
    # sort by status and then by publish time
    sorted_obj = sorted(obj, key=lambda x: (order_list[x.caseId.status], x.caseId.publishTime), reverse=True)
    cases = [
        {
            'employer':{
                #------ Employer part ------#
                #'employerId': app.caseId.employerId.userId,
                'displayName': app.caseId.employerId.displayName,
                'image': app.caseId.employerId.image,
            },
            'employee':{
                #------ Employee part ------#
                #'employeeId': app.employeeId.userId,
                #'message': app.message,
                'accepted': app.accepted,
                'employerRating': app.employerRating,
                'employeeRating': app.employeeRating,
            },
            'title': app.caseId.title,
            'text': app.caseId.text,
            'location': app.caseId.location,
            'pay': app.caseId.pay,
            'status': app.caseId.status,
            #'publishTime': tz.localtime(app.caseId.publishTime),
            #'modifiedTime': tz.localtime(app.caseId.modifiedTime),
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
def get_employer_history(post):
    userIdToken = post.get('userIdToken')
    # order by OPEN -> CLOSE -> DELETE
    order_list = {'O':3, 'C':2, 'D':1}
    obj = Case.objects.filter(employerId__userId=userIdToken).all()
    # sort by status and then by publish time
    sorted_obj = sorted(obj, key=lambda x: (order_list[x.status], x.publishTime), reverse=True)
    cases = [
        {
            'employer':{
                #------ Employer part ------#
                #'employerId': case.employerId.userId,
                'displayName': case.employerId.displayName,
                'image': case.employerId.image,
            },
            'title': case.title,
            'text': case.text,
            'location': case.location,
            'pay': case.pay,
            'status': case.status,
            #'publishTime': tz.localtime(case.publishTime),
            #'modifiedTime': tz.localtime(case.modifiedTime),
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
