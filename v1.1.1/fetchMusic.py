#!/usr/bin/evn/python3
# -*- coding: utf-8 -*-
import re, requests, json, asyncio, time
import threading
from random import random
from coredown import pyget
from decorat import test

import urllib3
urllib3.disable_warnings()

#    ↓↓ 博客主页：http://blog.sina.com.cn/s/articlelist_6055728941_0_{{page}}.html
#    ↓↓ 音乐子页：http://blog.sina.com.cn/s/blog_{{blogid}}.html
#    ↓↓ 城通网站：https://545c.com/file/{{userid}}-{{fileid}}  <<<==太傻逼了
#    ↓↓ js互动获取downurl：详见blogmusic.info    <<<==已解决

tasknum = 0
taskmax = 4
result = True
lock = threading.Lock()
api_server = 'https://webapi.400gb.com'
sinablog = 'http://blog.sina.com.cn/s/articlelist_6055728941_0_%d.html'
cookie = None
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
}

def getHTML(url, n=1):
    global cookie
    try:
        h = requests.get(url, headers=headers, cookies=cookie)
        cookie = h.cookies
        h.encoding = 'utf-8'
        return h.text
    except:
        if n<6:
            print('Waiting for retrying with %d times...\n  url:' % n, url)
            return getHTML(url, n+1)
        else:
            print('Connection Timeout WTF???')
            return ''
            # raise

def getBlog(page=1):    #找到主博客下的资源博客
    blog = sinablog % page
    print('Start searching the page %d...' % page)
    html = getHTML(blog)
    reblog = r'(?is)<span class="atc_title">.*?href="(.*?)">.*?</a></span>'
    return re.finditer(reblog, html)  #返回一个迭代器

def getMusic(mbs):    #找到资源博客下的城通网盘链接信息,返回迭代信息
    i = 1
    for mb in mbs:
        mblog = mb.group(1)
        mhtml = getHTML(mblog)
        i += 1
        recity = r'(?is)<a href="(.*?/(\d+)-(\d+))".*?>\1</a>'
        cityurl = re.search(recity, mhtml)
        if cityurl:
            _, uid, fid = cityurl.groups()
            yield uid, fid
        else:
            print('Unsuccessful:', mblog)

def getJSON(url, uid, fid, pms=None):
    h = dict(headers)
    h['Host'] = 'webapi.400gb.com'
    h['Origin'] = 'https://545c.com'
    h['Referer'] = 'https://545c.com/file/' + uid + '-' +fid
    h['Cookies'] = 'PHPSESSID=v455tlbfm23kkk2bbogoes27g3'
    r = requests.get(url, params=pms, headers=h)
    try:
        j = r.json()
    except:
        try:
            j = json.loads(r.text)
        except:
            print('Unjson:', r.text)
            j = {}
    return j

def getMSG(uid, fid, ref='', n=0):
    url = api_server + '/getfile.php'
    kvs = {'f': '%s-%s' % (uid, fid), 'passcode': '', 'ref': ref}
    j = getJSON(url, uid, fid, kvs)
    fn = j.get('file_name')
    #fs = j['file_size']
    fc = j.get('file_chk')
    #uid = j['userid']
    #fid = j['file_id']
    if (fn and fc) is None:
        if j.get('code') == 200 and n < 2:
            return getMSG(uid, fid, n=n+1)
    return fn, fc

def getURL(uid, fid, fchk, n=0):    #待定**kw可使用"kw.get(key) or default"
    url = api_server + '/get_file_url.php'
    kvs = {'uid': uid, 'fid': fid, 'folder_id': 0, 'file_chk': fchk, 'mb': 0, 'app': 0, 'acheck': 1, 'verifycode': '', 'rd': random()}
    j = getJSON(url, uid, fid, kvs)
    durl = j.get('downurl')
    if (durl is None) and n < 3:
        return getURL(uid, fid, fchk, n+1)
    return durl

def spider(loop):
    global result
    for i in range(7, 62):
        for u, f in getMusic(getBlog(i)):
            fn, fc = getMSG(u, f)
            if (fn or fc) is None:      # j['code'] != 200
                print('%s-%s is missing ...' % (u, f))
                continue
            while tasknum >= taskmax:
                time.sleep(1)
            else:
                if result:
                    loop.run_in_executor(None, down, u, f, fc, fn)
                else:
                    return
                
def down(u, f, fc, fn):
    path = r'C:\Users\15520\Music\blogmusic'
    global result
    chnum(1)
    r = pyget(getURL(u, f, fc), path, fname=fn).download()
    chnum(-1)
    result = result and not (r is False)

def chnum(n):
    global tasknum
    lock.acquire()
    tasknum += n
    lock.release()

def startEvent(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=startEvent, args=(loop,))
    spider(loop)
