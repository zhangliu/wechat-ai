from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
from zlExt.service import getAnswer

def getZlReply(context):
    if (context.type != ContextType.TEXT):
        return Reply(ReplyType.ERROR, '暂不支持该类型消息...')

    msg = context['msg']
    content = context.content or msg.content
    userId = msg.from_user_nickname or msg.from_user_id
    isGroup = context['isgroup'] or False
    logger.info(f"will get answer use: content={content}; userId={userId}; isGroup={isGroup}")
    answer = getAnswer(content, userId, isGroup)

    reply = Reply(ReplyType.TEXT, answer)
    return reply