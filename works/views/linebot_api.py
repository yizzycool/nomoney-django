### My Function ###
from works.functions.push import notify_acceptance, notify_application


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
