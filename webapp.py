from flask import Flask, request, make_response
import hashlib
import json
from lxml import etree
import time
import logging
import requests

logging.basicConfig(filename='logger.log', level=logging.INFO)

app = Flask(__name__)


@app.route('/')
def index():
    return 'Index Page'


@app.route('/weixin', methods=['GET', 'POST'])
def weixin():
    turing_key = "004aa6070348422b9afcdc9dfdb04b9a"
    turing_api = "http://www.tuling123.com/openapi/api"
    result = "<h1>Hello Weixin</h1>"
    if request.method == 'POST':
        logging.info("POST")
        logging.info(request.data)
        # recv_msg = BeautifulSoup(request.data.decode('utf-8'), "lxml")
        recv_msg = etree.XML(request.data)
        to_user = recv_msg.find('ToUserName').text
        from_user = recv_msg.find('FromUserName').text
        content = recv_msg.find('Content').text
        logging.info("to: "+to_user)
        logging.info("from: "+from_user)
        logging.info("content: "+content)

        ret_content = get_turing_response(turing_api, turing_key, content, from_user)

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
        token = "yanghan"
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


def get_turing_response(turing_api, turing_key, content, from_user):
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
    app.run(host="0.0.0.0", port=80, debug=True)
