import functools
def test(sth):
    def dec(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kw):
            print(sth, 'start')
            r = fn(*args, **kw)
            print(sth, 'ended')
            return r
        return wrapper
    return dec