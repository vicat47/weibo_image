import requests
import json
import pprint

import os
import urllib.request
import re
import time

from os import environ

from utils.db_util import DB


headers = {
    'User-Agent': environ.get('REQUEST_HEADER') or 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/91.0.4472.77'
}

Cookie = {
    'Cookie': environ.get('USER_COOKIES') or '_ga=GA1.2.516691287.1615897662; _T_WM=69757438418; SCF=AggWWQmfIK6sS_1kiZ43mpm8n5ZqbuorHYqEwQBbOBEsq8K-BGkCbG9N9kXNhKUmNo-P9_dwSBlRY668nfgdoHo.; SUB=_2A25NseDNDeRhGeVG71ER8izMwj2IHXVvXYCFrDV6PUJbktAKLXX-kW1NT7mxCpW9n-wCCzbz6ebXdfuKO7tplG9f; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWOS2ZViVF.soq4vvfvEmU05NHD95Q01hB0ehzEeh.pWs4Dqcj_i--Ni-2fiKL8i--fi-2fiKnNi--NiKLWiKnXi--NiKnpi-8si--Ni-8hi-ih; SSOLoginState=1622511773; WEIBOCN_FROM=1110003030; MLOGIN=1; XSRF-TOKEN=92d67f; M_WEIBOCN_PARAMS=lfid=1076033843022091&luicode=20000174&uicode=20000061&fid=4643033742576688&oid=4643033742576688'
}

# 存放图片主人微博名和url的字典
pic_info = {}
pic_set = set()

DOWNLOAD_PATH = './data/pics/'
WEIBO_ID = environ.get('WEIBO_ID') or '4643385863048927'
WEIBO_COMMENT_URL = 'https://m.weibo.cn/comments/hotflow?id=%s&mid=%s'
CHILD_COMMENT_URL = 'https://m.weibo.cn/comments/hotFlowChild?cid=%s&max_id=0&max_id_type=0'

REQ_DELAY = int(environ.get('REQ_DELAY')) or 15
REQ_CHILD = bool(environ.get('REQ_CHILD')) or False

DB_PATH = './data/weibo.db'

db = DB('sqlite3', DB_PATH)

def download_picset():
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)  # 如果没有这个path则直接创建
    for url in pic_set:
        time.sleep(REQ_DELAY)
        print('下载: ' + url)
        urllib.request.urlretrieve(url, filename=DOWNLOAD_PATH + url.split('/')[-1])

def download_pic_db():
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)  # 如果没有这个path则直接创建
    res = db.select_data('select * from images where downloaded=0')
    current_num = 0
    for img in res:
        current_num += 1
        print('下载第%d张: %s' % (current_num, img['url']))
        urllib.request.urlretrieve(img['url'], filename=DOWNLOAD_PATH + img['url'].split('/')[-1])
        db.update_data('images', {
            'url' : img['url']
        }, {
            'downloaded' : 1,
            'dl_time' : time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        })

'''
格式化请求获取到的数据，返回格式化后的数据
'''
def format_request_data(result: dict) -> dict:
    if result.get('ok') == 0:
        return None
    print('%s 请求评论 %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))), result['data']['max_id']))
    comment_data = {
        'ok' : result['ok'],
        'max' : result['data']['max'],
        'max_id' : result['data']['max_id'],
        'max_id_type' : result['data']['max_id_type'],
        'datas' : result['data']['data']
    }
    return comment_data

def format_child_data(result: dict) -> dict:
    if result.get('ok') == 0:
        return None
    print('%s 请求子数据 %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time()))), result['max_id']))
    comment_data = {
        'ok' : result['ok'],
        'max' : result['max'],
        'max_id' : result['max_id'],
        'max_id_type' : result['max_id_type'],
        'datas' : result['data']
    }
    return comment_data

def request_comment_data(weibo_id:str, max_id = None, max_id_type = None):
    time.sleep(REQ_DELAY)
    if max_id == None and max_id_type == None:
        response = requests.get(
            WEIBO_COMMENT_URL % (weibo_id, weibo_id) + '&max_id_type=0',
            cookies=Cookie, headers=headers)
        return format_request_data(json.loads(response.text))
    response = requests.get(
        WEIBO_COMMENT_URL % (weibo_id, weibo_id) + '&max_id={}&max_id_type={}'.format(max_id, max_id_type),
        headers=headers, cookies=Cookie)
    return format_request_data(json.loads(response.text))

def request_child_comm_data(cid, max_id = None, max_id_type = None):
    time.sleep(REQ_DELAY)
    if max_id == None and max_id_type == None:
        response = requests.get(
            CHILD_COMMENT_URL % cid + '&max_id_type=0',
            cookies=Cookie, headers=headers)
        return format_child_data(json.loads(response.text))
    response = requests.get(
        CHILD_COMMENT_URL % cid + '&max_id={}&max_id_type={}'.format(max_id, max_id_type),
        headers=headers, cookies=Cookie)
    return format_child_data(json.loads(response.text))

def get_pic_data(datas: dict):
    for data in datas:
        db.insert_data('catch_list', {
            'com_id' : data['id'],
            'root_id' : data['rootid'],
            'is_child' : 0,
            'user' : data['user']['screen_name'],
            'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(data['created_at'], "%a %b %d %H:%M:%S %z %Y")),
            'catch_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        })
        if REQ_CHILD:
            if data['total_number'] > 0:
                count = 1
                res = request_child_comm_data(data['id'])
                while res != None and count < res['max']:
                    get_child_pic_data(res['datas'])
                    res = request_child_comm_data(data['id'], res['max_id'], res['max_id_type'])
                    count += 1
        if 'pic' in data:
            username = data['user']['screen_name']
            print(username)
            url = data['pic']['large']['url']
            print(url)
            pic_info[username] = url
            pic_set.add(url)
            db.insert_data('images', {
                'url' : url,
                'catch_id' : data['id']
            })

def get_child_pic_data(datas: dict):
    for data in datas:
        db.insert_data('catch_list', {
            'com_id' : data['id'],
            'root_id' : data['rootid'],
            'is_child' : 1,
            'user' : data['user']['screen_name'],
            'create_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.mktime(time.strptime(data['created_at'], "%a %b %d %H:%M:%S %z %Y"))))),
            'catch_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        })
        reobj = re.search(r'<a data-url=.+href=\"(.+)\"\s', data['text'])
        if reobj != None:
            print(data['user']['screen_name'])
            img = reobj.group(1)
            print(img)
            pic_set.add(img)
            db.insert_data('images', {
                'url' : img,
                'catch_id' : data['id']
            })

def request_all_image(weibo_id):
    result = request_comment_data(weibo_id)
    count = 1
    while result != None and count < result['max']:
        get_pic_data(result['datas'])
        result = request_comment_data(weibo_id, result['max_id'], result['max_id_type'])
        count += 1

if __name__ == '__main__':
    db.execute_sql('./db.sql')
    result = request_comment_data(WEIBO_ID)
    count = 1
    while result != None and count < result['max']:
        get_pic_data(result['datas'])
        result = request_comment_data(WEIBO_ID, result['max_id'], result['max_id_type'])
        count += 1
    # download_picset()
    download_pic_db()