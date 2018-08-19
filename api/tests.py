# from django.test import TestCase
# import json
# import requests

# # Create your tests here.


# # 第一步 获取access_token
# ret = requests.get(  # 使用模块requests
#     url='https://api.weixin.qq.com/cgi-bin/token',
#     params={
#         'grant_type': 'client_credential',
#         'appid': 'wx45351926e9ed39ac',
#         'secret': '4b91671be73c8e559d6eaa17fc60216b',
#     }
# )
# access_token = json.loads(ret.text)['access_token']  # json反序列化为dict
# print(ret.text)

# # 第二步 获取指定用户openid（引导用户绑定主站账户与微信账户）
# openid = 'orGaTtyWl9JwMsii2Oxz58GdPFYg'


# # 第三步 发送模板消息
# body = {
#     "touser": openid,
#     "template_id": "ZqzReF4TLXpvigwFtVoc6NDEVlR1gA0JCyh98rBjpkA",

#     "data": {
#         "keyword1": {
#             "value": "巧克力",
#             "color": "#173177"
#         },
#     }
# }

# send = requests.post(

#     url='https://api.weixin.qq.com/cgi-bin/message/template/send',
#     params={
#         'access_token': access_token,
#     },
#     data=json.dumps(body),
# )
# print(send)
# print(send.text)

###################
# dic = ({
#     '1': {'id': 1, 'price': 11.0, 'valid_period': 1, 'valid_period_display': '1天'},
#     '5': {'id': 5, 'price': 33.0, 'valid_period': 3, 'valid_period_display': '3天'}
# },)
# for x in dic[0]:
#     print('1' in x)

# print('11111')
##################
# from api import models
# ret = models.Course.objects.filter(degree_course__id=1)
# print(ret)