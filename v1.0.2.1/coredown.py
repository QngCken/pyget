#!/usr/bin/evn/python3
# -*- coding: utf-8 -*-
import requests, os, time

class pyget:

    def __init__(self, url, path='.', fname=None, headers={}, **kw):
        self.size = 0           #下载文件当前大小
        self.total = 0          #下载文件总共大小
        self.reqSize = 0        #本次下载请求的文件大小
        self.url = url          #下载url
        self.fN = fname         #下载文件名称
        self.p = path           #下载文件存储路径//self.p = os.path.abspath(path)
        self.hdr = headers      #自定义请求头
        self.t = '.' + kw.get('tempFormat', 'downtemp') #默认缓存文件扩展后缀'.downtemp'
        self.x = '.' + kw.get('fileFormat', 'pyg')      #默认无名存储文件格式'.pyget'

    def doFile(self):
        if self.fN is None:
            self.fN = str(time.time()).replace('.', '') + self.x
        self.fl = os.path.join(self.p, self.fN)
        if os.path.exists(self.fl) and not os.path.exists(self.fl + self.t):
            return True
        return False

    # def touch(self, file):  #创建文件
    #     open(file, 'w').close()

    def isRenawable(self):
        hdrs = self.hdr
        hdrs['Range'] = 'bytes=0-4'        #设置特殊请求头判断是否支持断点续传
        r = requests.head(self.url, headers = hdrs)
        cr = r.headers.get('content-range')     #requests内构结构，协议不区分大小写
        cl = r.headers.get('content-length', 0)
        if cr :
            self.total = int(cr[10:])           #即"bytes 0-4/"后面的总大小
            return True
        self.reqSize = int(cl)      #没有content-range，查询请求长度content-length，仍没有则为0
        return False

    def watch(self):
        pass

    def download(self, renewable=False):
        if not self.url:
            print('Pyget with an empty url!')
            return
        if self.doFile():
            print('The file <%s> is existed and skipped...' % self.fN)
            return
        finished = False
        retry = True
        block = int(self.hdr.get('block', 1024))    #获取block大小，默认 1 kB = 1024 bytes
        tmpFile = self.fl + self.t
        renewable = renewable or self.isRenawable() #短路运算
        if renewable:  # 支持断点续传
            try:
                with open(tmpFile, 'r') as ft:
                    self.size = int(ft.read())      #获取已下载文件大小
                    print('Renewal the last size: %s bytes...' % self.size)
            except:
                # self.touch(tmpFile)    #缓存文件不存在则创建
                open(tmpFile, 'w').close()
                print('Create a new download <BPRable>...')
            finally:
                self.hdr['Range'] = "bytes=%d-" % (self.size)  #请求断点续传 或 新的下载
        else:
            # self.touch(tmpFile)
            # self.touch(self.fN)  #不支持断点续传，直接检测/创建文件
            open(tmpFile, 'w').close()
            print('Create a new download <disBPRable>...')
        
        size = self.size
        r = requests.get(self.url, stream = True, verify = False, headers = self.hdr)
        if self.reqSize:
            self.reqSize = int(r.headers.get('content-length', 0))  #获取最新的请求大小
        sz = self.total or self.reqSize
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
        with open(self.fl, 'ab+') as f:  #二进制追加读写
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
                    retry = False
                    os.remove(tmpFile)
                    print('\n<%s>\nDownload Finished!' % self.fN)
                else:
                    print('\nUnexpected size for file!')
                spend = time.time() - start_t
                speed = (size - self.size) / 1024 / spend if spend else 0
                print('Total Time: %.1fs, Download Speed: %.1fk/s\n' % (spend, speed))
            except KeyboardInterrupt:
                finished = False
                retry = False
                print("\nDownload pause.\n")
            except Exception as e:
                finished = False
                retry = True
                print('\nUnexpected Error happend:\n', e)
            finally:                         
                if finished is False:   #发生意外中断，记录断点位置 类似while finished：pass
                    with open(tmpFile, 'w') as ftmp:
                        ftmp.write(str(size))
                    if retry:
                        print('Auto start to retry...')
                        finished = self.download(renewable)
        if size < 2048:
            os.remove(self.fl)
        return finished


if __name__ == '__main__':
    u = ''
    pyget(u, fname='test.rar').download()