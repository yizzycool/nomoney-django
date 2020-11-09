# %%
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage, TemplateSendMessage, CarouselTemplate, Template
from linebot.exceptions import LineBotApiError
from works.views import message_objects
import os

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# print(channel_access_token)

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
    # 有人接受了你的幫助！
    message = message_objects.acceptance_message(case, user)
    message_object = FlexSendMessage(alt_text='【錄取通知】'+case['title'], contents=message)
    push_message(receiverid, message_object)
    return


def notify_application(receiverid, case, application):
    # 幫手出現了！
    message = message_objects.application_message(case, application)
    message_object = FlexSendMessage(alt_text='幫手出現了！', contents=message)
    push_message(receiverid, message_object)
    return


if __name__ == '__main__':
    
    test_userid = 'U2f7e15e05e4c914d1131b88756d1c39a'
    test_case = {'title': '高中數學題', 'description': '高中數學題求解，請附上解題過程', 'pay': 0, 'location': '新竹市', 'url':'https://google.com'}
    test_application = {'description': '我會ㄛ 選我選我', 'image':''}
    test_user = {'phone_number': '0912345678', 'lineid': 'lineid'}

    # print(test_userid)

    # test_userid = 'U04d1a0375336023979bce781d7da76b3'
    # notify_acceptance(test_userid, test_case, test_user)
    # notify_application(test_userid, test_case, test_application)
    # push_message('U2f7e15e05e4c914d1131b88756d1c39a', FlexSendMessage(alt_text='精選外快', contents=message_objects.recommanded_cases_message([test_case, test_case])))
    # push_message(test_userid, TextSendMessage(text='Hello World!'))
    # print(message_objects.acceptance_message(test_case, test_user))
    # print(message_objects.application_message(test_case, test_application))


# %%


# %%
