from bridge.reply import Reply, ReplyType
from zlExt.api2d import getAnswer

def testReply(content):
    answer = getAnswer(content)
    reply = Reply(ReplyType.TEXT, answer)
    return reply