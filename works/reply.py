from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)

import json
import os
import sys

from .message_objects import recommanded_cases_message
from .views import recommanded_cases

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@csrf_exempt
def callback(request):
    
    # get X-Line-Signature header value
    signature = request.META['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    body = request.body.decode('utf-8')
    print(body)

    # handle webhook body

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()

    return HttpResponse("callback")

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    if event.message.text != '精選工作':
        return

    userid = event.source.userId

    recommanded_cases = recommanded_cases(userid)
    recommanded_cases_message = recommanded_cases_message(recommanded_cases)
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text = '有人需要你的幫忙！', contents=recommanded_cases_message)
    )

