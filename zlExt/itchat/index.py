import re
from zlExt.utils.logger import log

def handleSyncCheckRes(res):
    log(f'get sync check result: {res.text}')

    regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
    pm = re.search(regx, res.text)

    if pm is None:
        raise Exception(f'get sync check {res.text}')

    if pm.group(1) == '-1':
        raise Exception(f'get sync check {res.text}')
    
    if pm.group(1) != '0':
        raise Exception(f'get sync check {res.text}')

    return pm.group(2)