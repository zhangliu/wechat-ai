import zlExt.utils.historyMsg.index as historyMsg

def addPrompt(history: list, prompt):
    history.insert(0, {"role": "user", "parts": [{"text": prompt}]})
    # history.insert(0, {"role": "model", "parts": [{"text": "好的，我明白了！"}]})
    return history

def appendMessage(id, msg, isGropu=False, limit = 20):
    item = {
        "role": msg["role"] or "user",
        "parts": [{"text": msg["content"]}]
    }
    historyMsg.appendMessage(id, item, isGropu, limit)

def getMessages(id, isGropu=False):
    return historyMsg.getMessages(id, isGropu)