from django.test import TestCase

# Create your tests here.

# redis test
import redis
print(111)
# conn = redis.Redis(host='172.16.109.139', port=6379)
# conn = redis.Redis(host='192.168.11.150', port=6379)
# conn = redis.Redis(host='192.168.11.61', port=6379)  # 教师机
conn = redis.Redis(host='118.24.111.198', port=6379)
print(222)
# conn.set('nut_name', '这是一个nut')
conn.set('nut_name', ['这是一个nut', '11', '22', 33, 44, 55])
res = conn.get('nut_name').decode('utf-8')
# res = conn.get('lijiarui_name').decode('utf-8')
conn.flushall()

print(res)
