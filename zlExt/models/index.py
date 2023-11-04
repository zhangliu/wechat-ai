import json
import os

def getFile(groupId):
    return f'./{groupId}_message.json'

def appendMessage(groupId, msg, limit = 20):
    filename = getFile(groupId)
    data = getMessages(groupId)
    data.append(msg)
    if (limit > 0): data = data[-limit:]

    with open(filename, 'w') as fp:
        json.dump(data, fp, indent=2)

def getMessages(groupId):
    filename = getFile(groupId)
    if (not os.path.exists(filename)):
        fp = open(filename, 'w')
        fp.close()

    try:
        with open(filename, '+r') as fp:
            return json.load(fp) or []
    except Exception as e:
        print(e)
        return []