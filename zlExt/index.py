from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
from zlExt.service import getAnswer

taskMap = {}

def getZlReply(context):
    if (context.type != ContextType.TEXT):
        return Reply(ReplyType.ERROR, '暂不支持该类型消息...')

    msg = context['msg']
    content = (context.content or msg.content or '').strip()
    userId = msg.from_user_nickname or msg.from_user_id
    # toUserId = context['receiver']
    isGroup = context['isgroup'] or False

    if (taskMap.get(userId)):
        return Reply(ReplyType.TEXT, f'正在处理问题「{taskMap[userId]}」，请稍后再提问')
    taskMap[userId] = content # 记录上次的问题

    logger.info(f"will get answer use: content={content}; userId={userId}; isGroup={isGroup}")
    answer = getAnswer(content, userId, isGroup)

    del taskMap[userId]

    reply = Reply(ReplyType.TEXT, answer)
    return reply