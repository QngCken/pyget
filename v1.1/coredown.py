#!/usr/bin/evn/python3
# -*- coding: utf-8 -*-
import requests, os, time

class pyget:

    def __init__(self, url, path='.', fname=None, headers={}, ext='.pyg'):
        self.size = 0
        self.total = 0
        self.reqSize = 0
        self.t = '.downtemp'
        self.url = url
        self.fN = fname
        self.p = path
        self.hdr = headers
        self.ext = ext
    
    def doFile(self):
        if self.fN is None:
            self.fN = str(time.time()).replace('.', '') + self.ext
        f = self.fN
        self.fN = os.path.join(self.p, self.fN)
        if os.path.exists(self.fN) and not os.path.exists(self.fN + self.t):
            print('The file <%s> is existed. This download will be skipped over...' % f)
            return True
        return False

    def touch(self, file):  #创建文件
        open(file, 'w').close()

    def support_continue(self):
        headers = {
            'Range': 'bytes=0-4'        #请求头判断是否支持断点续传
        }
        try:
            r = requests.head(self.url, headers = headers)
            crange = r.headers['content-range']     #requests内构结构，不必查询字母大小写
            self.total = int(crange[10:])       #即"bytes 0-4/"后面的总大小
            return True
        except:
            pass
        try:            #查询请求长度content-length，仍没有则为0
            self.reqSize = int(r.headers['content-length'])
        except:
            self.reqSize = 0
        return False


    def download(self):
        if self.url is None:
            return
        if self.doFile():
            return
        finished = False
        block = int(self.hdr.get('block') or 1024)      #获取block大小，默认 1 kB = 1024 bytes
        tmpFile = self.fN + self.t
        if self.support_continue():  # 支持断点续传
            try:
                with open(tmpFile, 'r') as ft:
                    self.size = int(ft.read())    #获取已下载文件名及其下载断点
                    print('Renewal the last download\nThe Last Size: %s bytes...' % self.size)
            except:
                self.touch(tmpFile)    #缓存文件不存在则创建
                print('Create a new download <BPRable>...')
            finally:
                self.hdr['Range'] = "bytes=%d-" % (self.size)  #请求头断点续传 或 新的下载
        else:
            self.touch(tmpFile)
            self.touch(self.fN)  #不支持断点续传，直接检测/创建文件
            print('Create a new download <disBPRable>...')
        
        size = self.size
        sz = self.total or self.reqSize
        r = requests.get(self.url, stream = True, verify = False, headers = self.hdr)
        if sz:
            if sz < 1024:
                print("[+] File Size: %dB" % (sz))
            elif sz < 1024*1024:
                print("[+] File Size: %0.2fKB" % (sz/1024))
            else:
                print("[+] File Size: %0.2fMB" % (sz/1024/1024))
        else:
            print("[+] Size: None")
        start_t = time.time()
        with open(self.fN, 'ab+') as f:  #二进制追加读写
            f.seek(self.size, 0)
            f.truncate()
            try:
                for chunk in r.iter_content(chunk_size = block): 
                    if chunk:
                        f.write(chunk)
                        size += len(chunk)  #即时记录当前文件大小
                        f.flush()
                    print('\b' * 64 + 'Now Loaded: %s / %s(bytes)' % (size, sz), end='')
                if size == (sz or size):
                    finished = True
                    os.remove(tmpFile)
                    print('\nDownload Finished!')
                else:
                    print('\nUnexpected suspension! Please retry again...')
                spend = int(time.time() - start_t)
                speed = int((size - self.size) / 1024 / spend)
                print('Total Time: %ss, Download Speed: %sk/s\n' % (spend, speed))
            except:
                print("\nDownload pause.\n")
            finally:                         
                if not finished:   #发生意外中断，记录断点位置
                    with open(tmpFile, 'w') as ftmp:
                        ftmp.write(str(size))
                    print('Auto start to retry...')
                    self.download()
        return finished


if __name__ == '__main__':
    u='http://451352.161.ctc.data.tv002.com/down/709dde75ad1c45399a6a6a63d8fb2798/%E5%91%A8%E6%9D%B0%E4%BC%A6-%E3%80%8A%E4%B9%94%E5%85%8B%E5%8F%94%E5%8F%94%E3%80%8B%E8%B6%85%E5%93%81%E8%B4%A8MP3%E5%8D%95%E6%9B%B2.rar?cts=ot-f-D210A41A101A251F48cb3&ctp=210A41A101A251&ctt=1569259095&limit=2&spd=1800000&ctk=709dde75ad1c45399a6a6a63d8fb2798&chk=9afde366c0d26bf6d8a11ddb39419e92-10238178&mtd=1'
    pyget(u, fname='1001.rar').download()