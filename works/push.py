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

def notify_acceptance(receiverid, user, case):
    # 有人需要你的幫忙！
    message = message_objects.acceptance_message(user, case)
    message_object = FlexSendMessage(alt_text = '有人需要你的幫忙！', contents=message)
    push_message(receiverid, message_object)
    

def notify_application(receiverid, title, application):
    # 幫手出現了！
    message = message_objects.application_message(title, application)
    message_object = FlexSendMessage(alt_text = '幫手出現了！', contents=message)
    push_message(receiverid, message_object)


# demo userid: U2f7e15e05e4c914d1131b88756d1c39a
test_message = {
  "type": "carousel",
  "contents": [
    {
      "type": "bubble",
      "size": "kilo",
      "hero": {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "backgroundColor": "#CC8800",
        "paddingAll": "md"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "size": "lg",
            "text": "運送一張電腦椅",
            "wrap": True
          },
          {
            "type": "separator"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "需要幫忙開車載一張電腦椅，從 xxx 路送到 xxx 路",
                "color": "#8C8C8C",
                "size": "md",
                "wrap": True
              }
            ],
            "paddingAll": "sm"
          }
        ],
        "spacing": "md",
        "paddingAll": "xxl"
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
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
                    "url": "https://imgur.com/C5SBrq6.png",
                    "position": "absolute"
                  },
                  {
                    "type": "text",
                    "text": "2020/10/31",
                    "offsetStart": "20px",
                    "color": "#8C8C8C",
                    "size": "xxs"
                  }
                ],
                "margin": "none",
                "paddingTop": "none"
              }
            ]
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
                    "url": "https://imgur.com/AFc3Ug0.png",
                    "position": "absolute"
                  },
                  {
                    "type": "text",
                    "text": "$150",
                    "offsetStart": "20px",
                    "color": "#8C8C8C",
                    "size": "xxs"
                  }
                ],
                "margin": "none",
                "paddingTop": "none"
              }
            ],
            "margin": "sm"
          }
        ],
        "paddingAll": "xxl"
      },
      "styles": {
        "footer": {
          "separator": False
        }
      }
    },
    {
      "type": "bubble",
      "size": "kilo",
      "hero": {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "backgroundColor": "#0088AA",
        "paddingAll": "md"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "size": "lg",
            "text": "高中數學題",
            "wrap": True
          },
          {
            "type": "separator"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "高中數學題求解，請附上解題過程",
                "color": "#8C8C8C",
                "size": "md",
                "wrap": True
              }
            ],
            "paddingAll": "sm"
          }
        ],
        "spacing": "md",
        "paddingAll": "xl"
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
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
                    "url": "https://imgur.com/C5SBrq6.png",
                    "position": "absolute",
                  },
                  {
                    "type": "text",
                    "text": "2020/10/31",
                    "offsetStart": "20px",
                    "color": "#8C8C8C",
                    "size": "xxs"
                  }
                ],
                "margin": "none",
                "paddingTop": "none"
              }
            ]
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
                    "url": "https://imgur.com/AFc3Ug0.png",
                    "position": "absolute",
                  },
                  {
                    "type": "text",
                    "text": "$150",
                    "offsetStart": "20px",
                    "color": "#8C8C8C",
                    "size": "xxs"
                  }
                ],
                "margin": "none",
                "paddingTop": "none"
              }
            ],
            "margin": "sm"
          }
        ],
        "paddingAll": "xl"
      },
      "styles": {
        "footer": {
          "separator": False
        }
      }
    }
  ]
}

# push_message('U2f7e15e05e4c914d1131b88756d1c39a', FlexSendMessage(alt_text='精選', contents=(test_message)))
# push_message('U2f7e15e05e4c914d1131b88756d1c39a', TextSendMessage(text='Hello World!'))

