#!/usr/bin/python3.5

from flask import Flask, request, make_response
import hashlib
import json
from lxml import etree
import time
import logging
import requests
from . import config
import re
from bs4 import BeautifulSoup

logging.basicConfig(filename='logger.log', level=logging.INFO)

app = Flask(__name__)
doc_string = """
发送中文：AI自动回复。(具有情景上下文)\n
发送图片：进行人脸识别。\n
发送\"movie [电影名]\": 可以寻找磁力链接（我从不开车 = =）\n
例\"movie 驴得水\"可以寻找电影驴得水的磁力链接
"""
mov_url = "http://www.btkiki.com/s/"


@app.route('/')
def index():
    return 'Index Page'


@app.route('/weixin', methods=['GET', 'POST'])
def weixin():
    result = "<h1>Hello Weixin</h1>"
    if request.method == 'POST':
        logging.info("POST")
        logging.info(request.data)
        # recv_msg = BeautifulSoup(request.data.decode('utf-8'), "lxml")
        recv_msg = etree.XML(request.data)
        to_user = recv_msg.find('ToUserName').text
        from_user = recv_msg.find('FromUserName').text
        msg_type = recv_msg.find('MsgType').text
        logging.info("to: "+to_user)
        logging.info("from: "+from_user)
        logging.info("type: "+msg_type)

        ret_content = handle_msg(msg_type, recv_msg)

        reply = """
                    <xml>
                        <ToUserName><![CDATA[%s]]></ToUserName>
                        <FromUserName><![CDATA[%s]]></FromUserName>
                        <CreateTime>%s</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[%s]]></Content>
                        <FuncFlag>0</FuncFlag>
                    </xml>
                """
        reply_str = reply % (from_user, to_user, int(time.time()), ret_content)
        response = make_response(reply_str)
        response.content_type = 'application/xml'
        return response
    else:
        token = config.wx_token
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get("echostr")
        try:
            L = [token, timestamp, nonce]
            L.sort()
            string_check = L[0]+L[1]+L[2]
            result += '\n' + string_check
            string_check = string_check.encode("utf-8")
            check_answer = hashlib.sha1(string_check).hexdigest()
            result += '\n' + check_answer
            if check_answer == signature:
                return echostr
        except Exception as e:
            result += str(e)
    return result


def handle_msg(msg_type, recv_msg):
    ret_content = str()
    if msg_type == 'event':
        subscribe = recv_msg.find('Event').text
        if subscribe == 'subscribe':
            ret_content = "欢迎关注。\n你可以输入 /help 来获取使用帮助。"

    elif msg_type == 'text':
        content = recv_msg.find('Content').text
        if re.findall("/help", content):
            ret_content = doc_string
        elif re.findall("movie( +)(.+)", content):
            pattern = re.compile("movie( +)(.+)")
            group = pattern.match(content)
            # print(group.group(2))
            res = requests.get(mov_url + group.group(2) + '.html')
            html = res.content.decode('utf-8')
            res.close()
            soup = BeautifulSoup(html, 'lxml')
            try:
                movies = soup.findAll('div', {'class': 'g'})
                for i in range(min(len(movies), 3)):
                    movie = movies[i]
                    href = movie.findAll('a', {'target': '_blank'})
                    if href:
                        href = href[0].attrs.get('href')
                        mov_res = requests.get(href)
                        mov_html = mov_res.content
                        mov_res.close()
                        mov_soup = BeautifulSoup(mov_html, 'lxml')
                        mov_info = mov_soup.findAll('div', {'id': 'result'})
                        if mov_info:
                            print(mov_info[0].findAll('h1')[0].get_text())
                            ret_content += mov_info[0].findAll('h1')[0].get_text()+'\n'
                            for mov_thing in mov_info[0].findAll('p'):
                                print(mov_thing.get_text())
                                ret_content += mov_thing.get_text()+'\n'
                    print("------------------")
                    ret_content += "--------------------------------------------"+'\n'
            except Exception as e:
                ret_content = "Sorry, 没有找到该电影."
                print(e)

        else: # get turing response.
            try:
                ret_content = get_turing_response(content, recv_msg.find('FromUserName').text)
            except Exception as e:
                logging.error(e)
                ret_content =  "Sorry. it failed. If you doubt this, plz contact me from 994819188@qq.com"

    elif msg_type == 'image':
        pic_url = recv_msg.find('PicUrl').text
        # img_file = requests.get(pic_url)
        # img = img_file.content
        # img_file.close()
        # pic_id = pic_url[-10:]
        # pic_name = "./src_file/"+pic_id+".jpg"
        # file = open(pic_name, "wb+")
        # file.write(img)
        try:
            url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
            api_key = config.api_key
            api_secret = config.api_secret
            param = dict()
            param['api_key'] = api_key
            param['api_secret'] = api_secret
            param['image_url'] = pic_url + ".jpg"
            param['return_landmark'] = 1
            param['return_attributes'] = 'gender,age,smiling,glass,headpose,facequality,blur'
            res = requests.post(url=url, data=param)
            info = json.loads(res.content.decode('utf-8'))
            if info['faces']:
                ret_content += "I have detected faces in this pic!\n"
                logging.info(info['faces'][0]['attributes'])
                for face in info['faces']:
                    attributes = face['attributes']
                    ret_content += 'gender: '+attributes['gender']['value']+'\n'
                    ret_content += 'age: '+str(attributes['age']['value'])+'\n'
                    ret_content += 'glasses: '+str(attributes['glass']['value']+'\n')
            else:
                ret_content = "No Face Detected."
        except Exception as e:
            logging.error(e)
            ret_content = "Sorry, failed to detect Face. With any doubt you can contact 994819188@qq.com"
        # os.remove(pic_name)
    return ret_content


def get_turing_response(content, from_user):
    turing_key = config.turing_key
    turing_api = config.turing_api
    ask_info = dict()
    ask_info['key'] = turing_key
    ask_info['info'] = content
    ask_info['userid'] = from_user
    r = requests.get(turing_api, params=ask_info)
    r = json.loads(r.text)
    ret_code = r['code']
    ret_content = content
    normal_code = [100000, 200000, 302000, 308000, 343000, 314000]
    if ret_code in normal_code:
        logging.debug("AI REPLY: " + r['text'])
        ret_content = r['text']
    if ret_code == 40004:
        logging.info("Too Many times")
        ret_content = "I'm tired today. Tomorrow you can come play with me."
    return ret_content


if __name__ == '__main__':
    app.run(debug=True)
