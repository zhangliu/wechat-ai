import zlExt.utils.historyMsg.index as historyMsg

def addPrompt(history: list, prompt):
    history.insert(0, {"role": "user", "parts": [{"text": prompt}]})
    history.insert(1, {"role": "model", "parts": [{"text": "好的，我明白了！"}]})
    return history

def appendMessage(id, msg, isGropu=False, limit=2000):
    item = {
        "role": msg["role"] or "user",
        "parts": [{"text": msg["content"]}]
    }
    historyMsg.appendMessage(id, item, isGropu, limit)

def appendUserMessage(id, content, limit=2000):
    msg = {"role": "user", "content": content}
    return appendMessage(id, msg, False, limit)

def appendModelMessage(id, content, limit=2000):
    msg = {"role": "model", "content": content}
    return appendMessage(id, msg, False, limit)

def appendGroupUserMessage(id, content, limit=2000):
    msg = {"role": "user", "content": content}
    return appendMessage(id, msg, True, limit)

def appendGroupModelMessage(id, content, limit=2000):
    msg = {"role": "model", "content": content}
    return appendMessage(id, msg, True, limit)

def getMessages(id, isGropu=False):
    return historyMsg.getMessages(id, isGropu)

def getGroupMessages(id):
    return getMessages(id, True)