import json
### Django ###
from django.http import HttpResponse, JsonResponse
from django.utils import timezone as tz
### Django Models ###
from works.models import User, Case, Application, Hashtag, MiddleAgent
### My functions
from works.functions import utils


# API
def search_case(request):
    if len(request.POST.copy().keys()) != 0:
        post = request.POST.copy()
    else:
        post = json.loads(request.body.decode('utf-8'))
    userIdToken = post.get('userIdToken')
    keyword = post.get('keyword')
    keyword = keyword.split() if keyword else []
    offset = int(post['offset'])
    obj = Case.objects.all().order_by('-publishTime')
    # remove cases that had been closed
    obj = obj.filter(status='O')
    # remove cases posted by userIdToken
    obj = obj.exclude(employerId__userId=userIdToken)
    # If condition set
    if 'conditions' in post:
        for key, value in post.get('conditions').items():
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
    # New Func: find hashtags
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
