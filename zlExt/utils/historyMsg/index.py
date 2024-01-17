import json
import os

def getFile(id, isGroup=False):
    dirname = os.path.dirname(__file__)
    if isGroup: return f'{dirname}/data/group_{id}_message.json'
    else: return f'{dirname}/data/single_{id}_message.json'

def appendMessage(id, msg, isGroup=False, limit = 2000):
    filename = getFile(id, isGroup)
    data = getMessages(id, isGroup)
    data.append(msg)
    if (limit > 0): data = data[-limit:]

    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)

def appendGroupMessage(id, msg, limit = 2000):
    return appendMessage(id, msg, True, limit)

def getMessages(id, isGroup=False):
    filename = getFile(id, isGroup)
    if (not os.path.exists(filename)):
        fp = open(filename, 'w')
        fp.close()

    try:
        with open(filename, '+r') as fp:
            return json.load(fp) or []
    except Exception as e:
        print(e)
        return []

def getGroupMessages(id):
    return getMessages(id, True)
    
def clearMessage(id, isGroup=False, limit = 10):
    filename = getFile(id, isGroup)
    data = getMessages(id, isGroup)
    
    if (len(data) <= limit): return

    data = data[-limit:]
    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=2, ensure_ascii=False)