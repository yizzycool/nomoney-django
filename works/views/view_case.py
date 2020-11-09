from django.http import HttpResponse, JsonResponse
from works.models import User, Case, Application, Hashtag, MiddleAgent
import json
from django.utils import timezone as tz
from works.views.view_search_case import search_case


# API
def get_case_by_case_id(request):
    post = json.loads(request.body.decode('utf-8'))
    caseId = int(post.get('caseId'))
    userIdToken = post.get('userIdToken')
    obj = Case.objects.filter(id=caseId).first()
    if obj == None: return JsonResponse({'noData': True})
    # Judge if request from Owner
    isOwner = True if userIdToken == obj.employerId.userId else False
    # get applications of this case
    applications = get_application_by_case_id(post, isOwner)
    case = {
        'noData': False,
        'employer':{
            #------ Employer part ------#
            'employerId': obj.employerId.userId,
            'displayName': obj.employerId.displayName,
            'image': obj.employerId.image,
            'gender': obj.employerId.gender,
            'rating': obj.employerId.rating,
            'phone': obj.employerId.phone,
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
    # If not Owner, then remove private information to keep data secure
    if not isOwner and app_obj and app_obj.accepted != 'A':
        case['employer'].pop('image', None)
        case['employer'].pop('phone', None)
        case['employer'].pop('lineId', None)
    if len(case['hashtag']) == 0:
        return JsonResponse(case)
    # get recommendations of this case by hashtag (count of hashtag need to be more than 0)
    request.POST = request.POST.copy()
    request.POST['userIdToken'] = userIdToken
    request.POST['keyword'] = ' '.join(case['hashtag'])
    request.POST['offset'] = 0
    recommendations = json.loads(search_case(request).content)
    if recommendations['noData']:
        return JsonResponse(case)
    else:
        recommendations['cases'] = list(filter(lambda r: r['caseId']!=case['caseId'], recommendations['cases']))
        for rec_case in recommendations['cases'][:5]:
            case['recommendations'].append({
                'caseId': rec_case['caseId'],
                'title': rec_case['title'],
                'location': rec_case['location'],
                'pay': rec_case['pay']
                })
    return JsonResponse(case)


# Function
def get_application_by_case_id(post, isOwner):
    caseId = post.get('caseId')
    userIdToken = post.get('userIdToken')
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
            'employeeRating': obj.employeeId.rating,
            'employerRating': obj.caseId.employerId.rating,
            'phone': obj.employeeId.phone,
            'lineId': obj.employeeId.lineId,
        }
        for obj in child_obj
    ]
    # Remove personal information if not yet accepted to keep secure
    for app in applications:
        if app['accepted'] != 'A':
            app.pop('phone', None)
            app.pop('lineId', None)
    return {
        'count': child_obj.count(),
        'applications': applications,
    }