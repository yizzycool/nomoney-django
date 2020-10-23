def acceptance_message(case, user):
    title = case['title']
    description = case['description']
    phone_number = user['phone_number']
    lineid = user['lineid']
    message = {
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
                    "paddingAll": "20px"
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
                    "text": title,
                    "weight": "regular",
                    "size": "lg",
                    "margin": "xs"
                },
                {
                    "type": "text",
                    "text": description,
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
                                    "text": phone_number,
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
                        "uri": "tel:" + phone_number
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
                                    "text": lineid,
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
                        "uri": "https://line.me/R/ti/p/~" + lineid
                    }
                }
            ],
            "backgroundColor": "#00000000",
            "paddingAll": "20px"
        }
    }
    return message


def application_message(case, application):
    title = case['title']
    description = application['description']
    image = 'https://imgur.com/ac7lLvz.png'
    message = {
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
                    "animated": False,
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
                                            "text": "幫手出現了！",
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
                    "paddingAll": "20px"
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
                    "text": title,
                    "weight": "regular",
                    "size": "lg",
                    "margin": "xs"
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "image",
                                    "url": image,
                                    "size": "full",
                                    "margin": "none",
                                    "aspectRatio": "1:1"
                                }
                            ],
                            "spacing": "none",
                            "width": "40px"
                        },
                        {
                            "type": "text",
                            "text": description,
                            "size": "sm",
                            "margin": "md",
                            "wrap": True,
                            "color": "#AAAAAA",
                            "offsetStart": "xs",
                            "maxLines": 2
                        }
                    ],
                    "margin": "lg",
                    "paddingAll": "none"
                }
            ],
            "backgroundColor": "#00000000",
            "paddingAll": "20px"
        }
    }
    return message


def recommanded_cases_message(cases):
    messages = {
        "type": "carousel",
        "contents": []
    }
    colors = ['#0088aa', '#CC8800', '#71A483']
    for idx, case in list(enumerate(cases)):
        title = case['title']
        description = case['description']
        pay = case['pay']
        location = case['location']
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [],
                "backgroundColor": colors[idx%3],
                "paddingAll": "md"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "size": "lg",
                        "text": title,
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
                                "text": description,
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
                                        "url": "https://imgur.com/3pRXEWY.png",
                                        "position": "absolute"
                                    },
                                    {
                                        "type": "text",
                                        "text": location,
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
                                        "text": '$' + str(pay),
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
        }
        messages['contents'].append(bubble)

    return messages
