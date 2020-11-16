import json
### Django ###
from django.http import HttpResponse, JsonResponse
### Django Models
from works.models import User, Case, Application, Hashtag, MiddleAgent, Rating

check_key = {'caseId', 'appId', 'rating', 'userIdToken'}

def rating(request):
    post = json.loads(request.body.decode('utf-8'))
    if check_key | set(post) < len(check_key):
        return HttpResponse(status=403)
    caseId = int(post.get('caseId'))
    appId = int(post.get('appId'))
    rating = float(post.get('rating'))
    comment = post.get('comment') or ''
    userIdToken = post.get('userIdToken')
    obj = Rating.objects.filter(caseId__id = caseId, appId__id = appId, raterId__userId = userIdToken)
    obj = Rating() if obj.count() == 0 else obj.first()
    try:
        app_obj = Application.objects.get(id = appId)
        id_set = {app_obj.employeeId.userId, app_obj.caseId.employerId.userId}   
        obj.caseId = Case.objects.get(id=caseId)
        obj.appId = Application.objects.get(id=appId)
        obj.raterId = User.objects.get(userId=)
    except Exception as e:
        print(e)
        return HttpResponse(status=403)
    
    #obj.save()
