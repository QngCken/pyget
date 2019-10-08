import os

def main():
    p = r'G:\Programage\Python\视频\Python异步协程高级进阶'
    for i in range(1, 99):
        fdp = os.path.join(p, str(i), '80')
        # os.rename(os.path.join(fdp, 'vedio.ms4'), os.path.join(fdp, 'v%02d.mp4' % i))
        # os.rename(os.path.join(fdp, 'audio.ms4'), os.path.join(fdp, 'a%02d.mp3' % i))
        s = 'video.m4s'
        t = 'v%02d.mp4' % i
        for _ in range(2):
            with open(os.path.join(fdp, s), 'rb') as frm:
                with open(os.path.join(p, t), 'wb') as tof:
                    while True:
                        w = frm.read(1024)
                        if w:
                            tof.write(w)
                        else:
                            break
            s = 'audio.m4s'
            t = 'a%02d.mp3' % i

if __name__ == "__main__":
    main()