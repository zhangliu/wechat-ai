import time

prefix = '[zlExt]'

def log(*args, **kwargs):
    print(time.strftime('%Y-%m-%d %H:%M:%S'), ':', prefix, *args, **kwargs);