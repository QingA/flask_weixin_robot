import requests
import json
import config
import re
from bs4 import BeautifulSoup


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
    param['image_url'] = "http://mmbiz.qpic.cn/mmbiz_jpg/WuEqBMro7GBDEBNg5gtzib7yupEiaicBxIGQSlFlrPZxRerUVRJyzdAzAZm1xCfhS9UbujBbibVOZAXUrJ7UydibCgQ/0.jpg"

    param['return_landmark'] = 1
    param['return_attributes'] = 'gender,age,smiling,glass,headpose,facequality,blur'
    res = requests.post(url=url, data=param)
    info = json.loads(res.content.decode('utf-8'))
    print(info['faces'][0]['attributes']['gender'])


def test_pic():
    url = "http://mmbiz.qpic.cn/mmbiz_jpg/WuEqBMro7GBDEBNg5gtzib7yupEiaicBxIGQSlFlrPZxRerUVRJyzdAzAZm1xCfhS9UbujBbibVOZAXUrJ7UydibCgQ/0"
    r = requests.get(url)
    file = open("./src_file/1.jpg", "wb")
    file.write(r.content)
    file.close()


def test_mov():
    content = "movie驴得水"
    mov_url = "http://www.btkiki.com/s/"
    if re.findall("movie( *)(.+)", content):
        pattern = re.compile("movie( *)(.+)")
        group = pattern.match(content)
        print(group.group(2))
        res = requests.get(mov_url+group.group(2)+'.html')
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
                        for mov_thing in mov_info[0].findAll('p'):
                            print(mov_thing.get_text())
                print("------------------")
        except Exception as e:
            print(e)


def test_music():
    value = "演员"
    url = 'http://sug.music.baidu.com/info/suggestion'
    payload = {'word': value, 'version': '2', 'from': '0'}
    print(value)

    r = requests.get(url, params=payload)
    # contents = r.text
    # d = json.loads(contents, encoding="utf-8")
    d = r.json()
    # if d is not None and 'data' not in d:
    #     continue
    print(d)
    songid = d["data"]["song"][0]["songid"]
    print("find songid: %s" % songid)

    url = "http://music.baidu.com/data/music/fmlink"
    payload = {'songIds': songid, 'type': 'flac'}
    r = requests.get(url, params=payload)
    # contents = r.text
    # d = json.loads(contents, encoding="utf-8")
    d = r.json()
    # if ('data' not in d) or d['data'] == '':
    #     continue
    print(d)
    songlink = d["data"]["songList"][0]["songLink"]
    print("find songlink: "+songlink)


def test_book():
    book_url = 'http://www.ireadweek.com/'
    book_query_url = "http://www.ireadweek.com/index.php/Index/bookList.html?keyword="
    bookname = "1Q84"
    html = requests.get(book_query_url+bookname).text
    soup = BeautifulSoup(html, 'lxml')
    li = soup.findAll('a', href=re.compile('/index.php/bookInfo/(\d+).html'))
    res = None
    max_num = 0
    if li:
        for item in li:
            li_res = item.find('div', {'class': 'hanghang-list-num'})
            if li_res:
                if int(li_res.get_text()) > max_num :
                    res = item
    # print(res)
    href = book_url + res.attrs.get('href')
    book_html = requests.get(url=href).text
    book_soup = BeautifulSoup(book_html, "lxml")
    book_info = book_soup.find('div', {'class': 'hanghang-shu-content-font'})
    print(book_info.get_text())
    book_link = book_soup.find('a', {'class': 'downloads'})
    print(book_link.attrs.get('href'))


def test_douban_login():
    login_url = "https://accounts.douban.com/login"
    data = {
        'redir': "https://www.douban.com",
        'form_email': config.douban_email,
        'form_password': config.douban_password,
        'remember': 'on',
        'login': '登录'
    }
    session = requests.Session()
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.1)\
               AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'}
    r = session.post(login_url, data=data, headers=headers)
    print(r.text)


def test_douban_rate():
    ret_content = str()
    base_url = 'https://www.douban.com/search?q='
    content = '西游记'
    html = requests.get(base_url+content).text
    soup = BeautifulSoup(html, 'lxml')
    results = soup.findAll('div', {'class': 'result'})
    for cnt in range(min(3, len(results))):
        item = results[cnt]
        print(cnt+1, item.get_text().replace('\n', '').replace('\t', '').replace(' ',''))
        link = item.findAll('a', {'class': 'nbg'})
        if link:
            print(link[0].attrs.get('href'))
        print('------------------------------------\n')


if __name__ == "__main__":
    # test_face()
    # test_pic()
    # test_mov()
    # test_music()
    test_book()
    # test_douban_rate()