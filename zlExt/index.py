from bridge.reply import Reply, ReplyType
from zlExt.api2d import getAnswer

def getZlReply(content):
    answer = getAnswer(content)
    reply = Reply(ReplyType.TEXT, answer)
    return reply

def getZlWaitingReply():
    reply = Reply(ReplyType.TEXT, '思考中...')
    return reply