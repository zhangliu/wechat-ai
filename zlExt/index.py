from bridge.reply import Reply, ReplyType
from zlExt.api2d import getAnswer

def getZlReply(context):
    msg = context['msg']
    userId = msg.from_user_nickname or msg.from_user_id
    answer = getAnswer(msg.content, userId)
    reply = Reply(ReplyType.TEXT, answer)
    return reply

def getZlWaitingReply():
    reply = Reply(ReplyType.TEXT, '思考中...')
    return reply