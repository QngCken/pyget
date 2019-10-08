import zipfile, os

def Unzip(zf, uzpath):
    fz = zipfile.ZipFile(zf, 'r', zipfile.ZIP_DEFLATED)
    for f in fz.namelist():
        if f.endswith('3') or f.endswith('v'):
            fz.extract(f, uzpath)
    fz.close()

def UnzipAll(fromdir, todir='.'):
    for z in os.listdir(fromdir):
        if z.endswith('zip'):
            Unzip(os.path.join(fromdir, z), todir)

# def test(fnp, path='.'):
#     fz = zipfile.ZipFile(fnp, 'r', zipfile.ZIP_DEFLATED)
#     print(fz.namelist())
#     fz.close()

if __name__ == "__main__":
    p = os.getcwd()
    UnzipAll(os.path.join(p, 'z'), p)