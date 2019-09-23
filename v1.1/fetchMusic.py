#!/usr/bin/evn/python3
# -*- coding: utf-8 -*-
import re, requests, json
from random import random
from coredown import pyget



#    ↓↓ 博客主页：http://blog.sina.com.cn/s/articlelist_6055728941_0_{{page}}.html
#    ↓↓ 音乐子页：http://blog.sina.com.cn/s/blog_{{blogid}}.html
#    ↓↓ 城通网站：https://545c.com/file/{{userid}}-{{fileid}}  <<<==太傻逼了
#    ↓↓ js互动获取downurl：详见blogmusic.info    <<<==已解决

api_server = 'https://webapi.400gb.com'

def getHTML(url):
    h = requests.get(url)
    h.encoding = 'utf-8'
    return h.text

def getBlog(page=1):    #找到主博客下的资源博客
    blog = 'http://blog.sina.com.cn/s/articlelist_6055728941_0_' + str(page) +'.html'
    html = getHTML(blog)
    reblog = r'(?is)<span class="atc_title">.*?href="(.*?)">.*?</a></span>'
    return re.finditer(reblog, html)  #返回一个迭代器

def getMusic(mbs):    #找到资源博客下的城通网盘链接信息,返回迭代信息
    for mb in mbs:
        mblog = mb.group(1)
        mhtml = getHTML(mblog)
        recity = r'(?is)<a href="(https://.*?/(\d+)-(\d+))".*?>\1</a>'
        cityurl = re.search(recity, mhtml)
        _, uid, fid = cityurl.groups()
        yield uid, fid

def getJSON():
    pass

def getMSG(uid, fid, ref=''):
    url = api_server + '/getfile.php'
    kvs = {'f': '%s-%s' % (uid, fid), 'ref': ref}
    r = requests.get(url, params=kvs)
    j = json.loads(r.text)
    fn = j['file_name']
    #fs = j['file_size']
    fc = j['file_chk']
    #uid = j['userid']
    #fid = j['file_id']
    return fn, fc

def getURL(uid, fid, fchk):    #待定**kw可使用"kw.get(key) or default"
    url = api_server + '/get_file_url.php'
    kvs = {'uid': uid, 'fid': fid, 'folder_id': 0, 'file_chk': fchk, 'mb': 0, 'app': 0, 'acheck': 1, 'verifycode': '', 'rd': random()}
    r = requests.get(url, params=kvs)
    j = json.loads(r.text)
    durl = j.get('downurl')
    return durl

def spider():
    for i in range(1, 2):
        for u, f in getMusic(getBlog(i)):
            fn, fc = getMSG(u, f)
            pyget(getURL(u, f, fc), fname=fn).download()

#spider()