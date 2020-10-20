from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
import sqlite3

# Create your views here.
def index(request):
    return HttpResponse('Hello World!')











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