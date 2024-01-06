import threading
import time

class FunctionThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        try:
            self.result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.result = e

def runTimes(limit, timeout, func, *args, **kwargs):
    times = 0
    while times < limit:
        print('start run func:', func.__name__, times, 'time')
        funcThread = FunctionThread(func, *args, **kwargs)
        funcThread.start()
        times += 1

        # 等待 timeout 秒，然后如果线程还在运行，就中断它
        funcThread.join(timeout)
        if funcThread.is_alive():
            print('run func', func.__name__, 'timed out!')
            continue

        if (not isinstance(funcThread.result, Exception)):
            return funcThread.result

    return None