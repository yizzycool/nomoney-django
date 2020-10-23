# %%
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage, TemplateSendMessage, CarouselTemplate, Template
from linebot.exceptions import LineBotApiError
import message_objects

import os

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

print(channel_access_token)

# %%
line_bot_api = LineBotApi(channel_access_token)


def push_message(userid, messages):
    try:
        line_bot_api.push_message(userid, messages)
    except LineBotApiError as e:
        # error handle
        print(e)
        pass


def notify_acceptance(receiverid, case, user):
    # 有人需要你的幫忙！
    message = message_objects.acceptance_message(case, user)
    message_object = FlexSendMessage(alt_text='有人需要你的幫忙！', contents=message)
    push_message(receiverid, message_object)


def notify_application(receiverid, case, application):
    # 幫手出現了！
    message = message_objects.application_message(case, application)
    message_object = FlexSendMessage(alt_text='幫手出現了！', contents=message)
    push_message(receiverid, message_object)


if __name__ == '__main__':
    test_message = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "image",
                    "url": "https://images.pexels.com/photos/1310532/pexels-photo-1310532.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=500",
                    "aspectMode": "cover",
                    "aspectRatio": "1.6:1",
                    "gravity": "top",
                    "align": "start",
                    "size": "full"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "position": "absolute",
                    "backgroundColor": "#00000055",
                    "width": "100%",
                    "height": "100%",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "有人需要你的幫忙！",
                                            "size": "xl",
                                            "color": "#ffffff"
                                        }
                                    ]
                                }
                            ],
                            "spacing": "xs"
                        }
                    ],
                    "position": "absolute",
                    "offsetBottom": "0px",
                    "offsetStart": "0px",
                    "offsetEnd": "0px",
                    "paddingAll": "20px",
                }
            ],
            "paddingAll": "0px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "title",
                    "weight": "regular",
                    "size": "lg",
                    "margin": "xs"
                },
                {
                    "type": "text",
                    "text": "description",
                    "size": "sm",
                    "margin": "md",
                    "wrap": True,
                    "color": "#AAAAAA",
                    "maxLines": 2
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": "聯絡資訊",
                    "margin": "xl",
                    "size": "lg",
                    "contents": []
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "icon",
                                    "margin": "none",
                                    "position": "absolute",
                                    "url": "https://imgur.com/10x7MDi.png"
                                },
                                {
                                    "type": "text",
                                    "text": "0912345678",
                                    "margin": "md",
                                    "size": "sm",
                                    "offsetStart": "xl",
                                    "color": "#000099"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "paddingTop": "sm",
                    "paddingBottom": "md",
                    "action": {
                        "type": "uri",
                        "label": "action",
                        "uri": "tel:0912345678"
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "icon",
                                    "url": "https://imgur.com/7wQMu5i.png",
                                    "position": "absolute"
                                },
                                {
                                    "type": "text",
                                    "text": "lineid",
                                    "margin": "md",
                                    "size": "sm",
                                    "offsetStart": "xl",
                                    "color": "#000099"
                                }
                            ],
                            "margin": "md"
                        }
                    ],
                    "paddingTop": "xs",
                    "paddingBottom": "md",
                    "action": {
                        "type": "uri",
                        "label": "action",
                        "uri": "https://line.me/R/ti/p/~"
                    }
                }
            ],
            "backgroundColor": "#00000000",
            "paddingAll": "20px"
        }
    }
    test_userid = 'U2f7e15e05e4c914d1131b88756d1c39a'
    test_case = {'title': '高中數學題', 'description': '高中數學題求解，請附上解題過程'}
    test_application = {'description': '我會ㄛ 選我選我'}
    test_user = {'phone_number': '0912345678', 'lineid': 'lineid'}

    print(test_userid)

    # test_userid = 'U04d1a0375336023979bce781d7da76b3'
    # notify_acceptance(test_userid, test_case, test_user)
    # notify_application(test_userid, test_case, test_application)
    push_message('U2f7e15e05e4c914d1131b88756d1c39a', FlexSendMessage(alt_text='精選', contents=(test_message)))
    # push_message(test_userid, TextSendMessage(text='Hello World!'))


# %%
