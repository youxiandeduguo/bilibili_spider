import random

import requests
import csv
import hashlib
import time
from urllib.parse import quote
import re
from datetime import datetime



def hash(data, date,oid):
    en = [
        "mode=3",
        f"oid={oid}",
        f"pagination_str={quote(data)}",
        "plat=1",
        "seek_rpid=""",
        "type=1",
        "web_location=1315875",
        f"wts={date}",
    ]
    wt = "ea1db124af3c7062474693fa704f4ff8"
    Jt = '&'.join(en)
    #"mode=3&oid=995250683&pagination_str=%7B%22offset%22%3A%22%22%7D&plat=1&seek_rpid=&type=1&web_location=1315875&wts=1720927766"
    string = Jt + wt
    MD5 = hashlib.md5()
    MD5.update(string.encode('utf-8'))
    w_rid = MD5.hexdigest()
    # print(w_rid)
    return w_rid


def get_one(csvwriter,oid):
    comment_cot=0
    date = str(int(time.time()))
    pagination_str = '{"offset":""}'
    w_rid = hash(pagination_str, date,oid)
    # print(w_rid)
    url = 'https://api.bilibili.com/x/v2/reply/wbi/main?'
    data = {
        'oid': oid,
        'type': '1',
        'mode': '3',
        'pagination_str': '{"offset":""}',
        'plat': '1',
        'seek_rpid':'',
        'web_location': '1315875',
        'w_rid': w_rid,
        'wts': date,
    }
    response = requests.get(url=url, params=data, headers=headers)
    json_data=response.json()
    replies=json_data['data']['replies']
    for i in range(0,len(replies)):
        # print(replies[i]['content']['message'])
        try:
            position=replies[i]['reply_control']['location']
        except:
            position="其它"
        dic={
            'name': replies[i]['member']['uname'],
            'comment':replies[i]['content']['message'],
            'time': str(datetime.fromtimestamp(replies[i]['ctime'])),
            'position': position,
            'like': replies[i]['like']
        }
        csvwriter.writerow(dic.values())
        comment_cot+=1
        re_replies=replies[i]['replies']
        for j in range(0,len(re_replies)):
            try:
                position = re_replies[i]['reply_control']['location']
            except:
                position = "其它"
            dic = {
                'name': re_replies[j]['member']['uname'],
                'comment': re_replies[j]['content']['message'],
                'time': str(datetime.fromtimestamp(re_replies[j]['ctime'])),
                'position': position,
                'like': re_replies[j]['like']
            }
            csvwriter.writerow(dic.values())
            comment_cot+=1

    response.close()
    return json_data['data']['cursor']['session_id'],json_data['data']['cursor']['all_count'],comment_cot

def get_content(session_id,headers,oid):
    comment_cot=0
    date = str(int(time.time()))
    pagination_str = '{"offset":"{\\"type\\":1,\\"direction\\":1,\\"session_id\\":\\"%s\\",\\"data\\":{}}"}' %session_id
    w_rid = hash(pagination_str, date,oid)
    # print(w_rid)


    url = 'https://api.bilibili.com/x/v2/reply/wbi/main?'
    data = {
        'oid': oid,
        'type': '1',
        'mode': '3',
        'pagination_str': '{"offset":"{\\"type\\":1,\\"direction\\":1,\\"session_id\\":\\"%s\\",\\"data\\":{}}"}' %session_id,
        'plat': '1',
        'seek_rpid': '',
        'web_location': '1315875',
        'w_rid': w_rid,
        'wts': date,
    }
    response = requests.get(url=url, params=data, headers=headers)
    json_data = response.json()
    replies = json_data['data']['replies']
    if replies is not None:
        for i in replies:
            # print(replies[i]['content']['message'])
            try:
                position = i['reply_control']['location']
            except:
                position = "其它"
            dic = {
                'name': i['member']['uname'],
                'comment': i['content']['message'],
                'time': str(datetime.fromtimestamp(i['ctime'])),
                'position':position,
                'like':i['like']

            }
            csvwriter.writerow(dic.values())
            comment_cot+=1
            re_replies = i['replies']
            for j in range(0, len(re_replies)):
                try:
                    position = re_replies[i]['reply_control']['location']
                except:
                    position = "其它"
                dic = {
                    'name': re_replies[j]['member']['uname'],
                    'comment': re_replies[j]['content']['message'],
                    'time': str(datetime.fromtimestamp(re_replies[j]['ctime'])),
                    'position': position,
                    'like': re_replies[j]['like']
                }
                csvwriter.writerow(dic.values())
                comment_cot+=1
    response.close()
    return comment_cot

def get_main(page,headers,rid):
    comment_cot=0
    url=f"https://api.bilibili.com/x/web-interface/dynamic/region?ps=14&pn={page}&rid={rid}"
    res=requests.get(url,headers=headers)
    json_data=res.json()
    vid_list=json_data['data']['archives']

    for j in vid_list:
        oid=j['stat']['aid']
        reply_num=j['stat']['reply']
        if reply_num<10:
            continue
        print(oid)
        section_id, all_count,the_cot = get_one(csvwriter,oid)
        comment_cot+=the_cot
        total_page = int(all_count / 20)
        for i in range(2, total_page):
            time.sleep(random.random()+1)
            the_cot=get_content(section_id, headers,oid)
            comment_cot+=the_cot
    return comment_cot
if __name__ == '__main__':

    goal_comment=100000
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
        'Cookie': 'buvid4=41E92047-B193-5342-A198-596127CC9F8068678-023060713-imcfn3P5GzC1xu89g5vofA%3D%3D; buvid_fp_plain=undefined; i-wanna-go-back=-1; LIVE_BUVID=AUTO9916887037351584; is-2022-channel=1; enable_web_push=DISABLE; header_theme_version=CLOSE; FEED_LIVE_VERSION=V_WATCHLATER_PIP_WINDOW3; _uuid=679109F21-513C-69D9-B49A-DE1EE8E62CE526030infoc; buvid3=A05BE272-B119-32A5-554A-737F5E71A0B055396infoc; b_nut=1720676155; rpdid=0z9Zw2XM52|4ZS2ajqo|Mx6|3w1SrN9Y; CURRENT_BLACKGAP=0; CURRENT_QUALITY=80; PVID=4; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjIxNTQyODIsImlhdCI6MTcyMTg5NTAyMiwicGx0IjotMX0.88uQ2QFGrGVhagWHMMPzgHNkUmT_CzfwSRyaN_e5uNQ; bili_ticket_expires=1722154222; fingerprint=dc1cbed4951a9e28632dc3443057d556; SESSDATA=000cba5e%2C1737623673%2Ceaf64%2A71CjBw0KlMkT4BGYyFpuqRbGaGP2i-dDEp2a1zbHvQDLyiAl5nussuZYwUt4fbJJAWRs8SVi1LbHM4Z1NMc2J4YWI3TUFMQ3VhMHFnWHRwYldyVm5iYi1iMEdfRlRmLVpiMkZ1aXpzRDRIaExUZThtc3ZDOHhjZjRuMzhsTFJfazZITEpoUkFqRlpnIIEC; bili_jct=3ad3f0bda69783187ecc59185d0c510b; DedeUserID=92137574; DedeUserID__ckMd5=4f270df4cc742ed6; bp_t_offset_92137574=958846664238432256; buvid_fp=dc1cbed4951a9e28632dc3443057d556; CURRENT_FNVAL=16; b_lsid=AA222F79_190F65990D3; home_feed_column=4; browser_resolution=440-714',
        'Referer': 'https://www.bilibili.com/v/ent/?spm_id_from=333.1007.0.0'
    }

    f = open('bilibili鬼畜区.csv', mode='a', encoding='utf-8', newline='')  # 创建文件对象，保存数据
    csvwriter = csv.writer(f)
    comment_cot=0
    #1
    page_cot=1
    rid=24
    while comment_cot<goal_comment:
        print('-'+str(page_cot))
        time.sleep(random.random()+1)
        comment_cot+=get_main(page_cot%13,headers,rid)
        page_cot+=1
    f.close()

