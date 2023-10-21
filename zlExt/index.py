import json
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
from zlExt.service import getAnswer

taskMap = {}
messageMap = {}

def getZlReply(context):
    if (context.type != ContextType.TEXT):
        return Reply(ReplyType.ERROR, '暂不支持该类型消息...')

    msg = context['msg']
    content = (context.content or msg.content or '').strip()
    userId = msg.from_user_nickname or msg.from_user_id
    # toUserId = context['receiver']
    isGroup = context['isgroup'] or False
    botName = msg.to_user_nickname

    if (isGroup):
        content = handleGroupReply(userId, context) or content

    if (taskMap.get(userId)):
        return Reply(ReplyType.TEXT, f'正在处理问题「{taskMap[userId]}」，请稍后再提问')
    taskMap[userId] = content # 记录上次的问题

    logger.info(f"will get answer use: content={content}; userId={userId}; isGroup={isGroup}; botName={botName}")
    answer = getAnswer(content, userId, isGroup, botName)

    del taskMap[userId]

    reply = Reply(ReplyType.TEXT, answer)
    return reply

# 搜集到足够的群聊内容，就主动发表一次消息
def handleGroupReply(groupId, context):
    msg = context['msg']
    userNickName = msg.actual_user_nickname
    content = f'用户「{userNickName}」说: {msg.content.strip()}'

    messageMap.setdefault(groupId, [])
    messageMap[groupId].append(content)

    if (msg.is_at):
        return json.dumps(messageMap[groupId], ensure_ascii=False)

    if (len(messageMap[groupId]) >= 10):
        content = json.dumps(messageMap[groupId], ensure_ascii=False)
        del messageMap[groupId]
        return content