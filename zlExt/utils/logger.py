import time

prefix = '[zlExt]'

def log(*args, **kwargs):
    print(prefix, f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]", *args, **kwargs);