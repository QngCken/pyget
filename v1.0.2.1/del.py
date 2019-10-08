import os, time

def rmv():
    p = r'C:\Users\15520\Music\blogmusic'
    while True:
        for i in os.listdir(p):
            if i.endswith('rar'):
                rm = False
                fp = os.path.join(p, i)
                try:
                    with open(fp, 'rb') as f:
                        if f.seek(0, 2) < 2048:
                            rm = True
                            print('removed', i)
                except:
                    pass
                try:
                    if rm:
                        os.remove(fp)
                except:
                    pass
        time.sleep(120)

if __name__ == "__main__":
    rmv()