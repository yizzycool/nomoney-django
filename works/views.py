from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
import os
import sqlite3
from time import gmtime, strftime
from works.models import User, Case, Application
import json


# Create your views here.
def index(request):
    return HttpResponse('Hold on!')


def get_profile(request):
    body = json.loads(request.body.decode('utf-8'))
    userIdToken = body['userIdToken']
    obj = User.objects.filter(userId=userIdToken).first()
    if obj == None:
        return JsonResponse({'noData':None})
    data = {
        'uerId': obj.userId,
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


def get_history(request):
    body = json.loads(request.body.decode('utf-8'))
    types = body['type']
    if types == 'help':
        return get_employee_history(body)
    if types == 'seek':
        return get_employer_history(body)


def get_employee_history(body):
    userIdToken = body['userIdToken']
    obj = Application.objects.filter(employeeId=userIdToken).order_by('-caseId__publishTime')
    cases = [
        {
            #------ Employer part ------#
            'employerId': app.caseId.employerId.userId,
            'displayName': app.caseId.employerId.displayName,
            'image': app.caseId.employerId.image,
            'title': app.caseId.title,
            'text': app.caseId.text,
            'location': app.caseId.location,
            'pay': app.caseId.pay,
            'status': app.caseId.status,
            'publishTime': app.caseId.publishTime,
            'modifiedTime': app.caseId.modifiedTime,
            'caseId': app.caseId.id,
            #------ Employee part ------#
            'employeeId': app.employeeId.userId,
            'message': app.message,
            'accepted': app.accepted,
            'employerRating': app.employerRating,
            'employeeRating': app.employeeRating,
        }
        for app in obj
    ]
    return JsonResponse({
        'count': len(cases),
        'cases': cases,
    })


def get_employer_history(body):
    userIdToken = body['userIdToken']
    obj = Case.objects.filter(employerId=userIdToken).order_by('-publishTime')
    cases = [
        {
            #------ Employer part ------#
            'employerId': case.employerId.userId,
            'displayName': case.employerId.displayName,
            'image': case.employerId.image,
            'title': case.title,
            'text': case.text,
            'location': case.location,
            'pay': case.pay,
            'status': case.status,
            'publishTime': case.publishTime,
            'modifiedTime': case.modifiedTime,
            'caseId': case.id,
        }
        for case in obj
    ]
    return JsonResponse({
        'count': len(cases),
        'cases': cases,
    })


def get_application_by_case(request):
    pass


def find_job(request):
    pass




def crud_case(request):

    pass


def crud_application(request):

    pass


def crud_user(request):
    return HttpResponse(timezone.localtime(timezone.now()))
    pass
    body = request.body
    #timezone = strftime("%z", gmtime())  # get timezone
    #set_timezone = timezone[]
    parse_datetime(str(datetime.now())+'-0800')

    pass
    






#
# Line-bot section
#

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    LocationMessage,
    LocationSendMessage,
    TemplateSendMessage,
    MessageTemplateAction,
    ButtonsTemplate,
    PostbackTemplateAction,
    URITemplateAction,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    PostbackEvent,
)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
