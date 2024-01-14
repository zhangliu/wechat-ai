from concurrent.futures import ThreadPoolExecutor
import time

def runTimes(limit, timeout, func, *args, **kwargs):
    times = 0
    while times < limit:
        try:
            print('start run func:', func.__name__, times, 'time')
            times += 1
            return runTimeout(timeout, func, *args, **kwargs)
        except Exception as e:
            print('run func', func.__name__, 'error:', str(e) or 'Time out!')
            time.sleep(1)
            continue

    return None

def runTimeout(timeout, func, *args, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result(timeout=timeout)