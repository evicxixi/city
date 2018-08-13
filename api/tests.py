from django.test import TestCase
import json
import requests

# Create your tests here.


# 第一步 获取access_token
ret = requests.get(  # 使用模块requests
    url='https://api.weixin.qq.com/cgi-bin/token',
    params={
        'grant_type': 'client_credential',
        'appid': 'wx45351926e9ed39ac',
        'secret': '4b91671be73c8e559d6eaa17fc60216b',
    }
)
access_token = json.loads(ret.text)['access_token']  # json反序列化为dict


# 第二步 发送模板消息
body = {
    "touser": "orGaTt1HyNQiKwTEbLOv69_N7SlM",
    "template_id": "ZqzReF4TLXpvigwFtVoc6NDEVlR1gA0JCyh98rBjpkA",
    "url": "http://weixin.qq.com/download",
           "miniprogram": {
               "appid": "xiaochengxuappid12345",
               "pagepath": "index?foo=bar"
           },
    "data": {
               "first": {
                   "value": "恭喜你购买成功！",
                   "color": "#173177"
               },
               "keyword1": {
                   "value": "巧克力",
                   "color": "#173177"
               },
               "keyword2": {
                   "value": "39.8元",
                   "color": "#173177"
               },
               "keyword3": {
                   "value": "2014年9月22日",
                   "color": "#173177"
               },
               "remark": {
                   "value": "欢迎再次购买！",
                   "color": "#173177"
               }
           }
}

send = requests.post(

    url='https://api.weixin.qq.com/cgi-bin/message/template/send',
    params={
        'access_token': access_token,
    },
    data=json.dumps(body),
)
