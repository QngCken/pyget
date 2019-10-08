import os

def gather():
    mp = r'G:\Music'
    zp = os.path.join(mp, '解压')
    for fd in os.listdir(zp):
        fdp = os.path.join(zp, fd)
        for f in os.listdir(fdp):
            tof = None
            if f.endswith('3'):
                tof = os.path.join(mp, f)
            elif f.endswith('v'):
                tof = os.path.join(mp, 'wav', f)
            if tof:
                frf = os.path.join(fdp, f)
                with open(tof, 'wb') as tom:
                    with open(frf, 'rb') as frm:
                        while True:
                            w = frm.read(1024)
                            if w:
                                tom.write(w)
                            else:
                                break
                os.remove(frf)
                
if __name__ == "__main__":
    gather()