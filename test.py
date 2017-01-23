import requests
import json

turing_key = "004aa6070348422b9afcdc9dfdb04b9a"
turing_api = "http://www.tuling123.com/openapi/api"
ask_info = {}
content = "nihao"
from_user = "123456"
ask_info['key'] = turing_key
ask_info['info'] = content
ask_info['userid'] = from_user
print(ask_info)
r = requests.get(turing_api, params=ask_info)
res = json.loads(r.text)
print(res['text'])