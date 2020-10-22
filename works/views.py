from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
import os
import sqlite3
from datetime import datetime
from time import gmtime, strftime
from works.models import User, Case, Application
import json


# Create your views here.
def index(request):
    return HttpResponse('Hello World!')


def update_profile(request):
    pass
    body = request.body
    #timezone = strftime("%z", gmtime())  # get timezone
    #set_timezone = timezone[]
    parse_datetime(str(datetime.now())+'-0800')

    pass


def get_profile(request):
    body = json.loads(request.body.decode('utf-8'))
    userId = body['userIdToken']
    obj = User.objects.filter(userId=userId).first()
    if obj == None:
        return JsonResponse({
            'uerId': None,
            'displayName': None,
            'image': None,
            'intro': None,
            'gender': None,
            'birthday': None,
            'phone': None,
            'county': None,
            'rating': None,
        })
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
    }
    return JsonResponse(data)


    






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


def webhook(request):
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print(signature)

    # get request body as text
    body = json.loads(request.body.decode('utf-8'))
    #body = request.get_data(as_text=True)
    print('Request body', body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return HttpResponse('OK')



@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))