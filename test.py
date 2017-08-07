import requests
import json
import config


def test_turing():
    turing_key = config.turing_key
    turing_api = config.turing_api
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


def test_face():
    url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
    api_key = config.api_key
    api_secret = config.api_secret
    param = dict()
    param['api_key'] = api_key
    param['api_secret'] = api_secret
    param['image_url'] = "http://www.jiushixing.com/d/file/uploads/2015/allimg/150605/125-150605144121.jpg"
    param['return_landmark'] = 1
    param['return_attributes'] = 'gender,age,smiling,glass,headpose,facequality,blur'
    res = requests.post(url=url, data=param)
    info = json.loads(res.content.decode('utf-8'))
    print(info['faces'][0]['attributes']['gender'])


if __name__ == "__main__":
    test_face()
