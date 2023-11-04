import json
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
from zlExt.models.index import appendMessage, getMessages
from zlExt.service import getAnswer

taskMap = {}
MESSAGE_LIMIT = 6

def getZlReply(context):
    isGroup = context['isgroup'] or False

    if (not isGroup): return handleSingle(context)
    return handleGroup(context)

def handleSingle(context):
    msg = context['msg']
    if (context.type != ContextType.TEXT):
        return Reply(ReplyType.ERROR, '暂不支持该类型消息...')

    content = (context.content or '').strip()
    userId = msg.from_user_nickname or msg.from_user_id

    if (taskMap.get(userId)):
        return Reply(ReplyType.TEXT, f'正在处理问题「{taskMap[userId]}」，请稍后再提问')
    taskMap[userId] = content # 记录上次的问题

    logger.info(f"will get answer use: content={content}; userId={userId}; isGroup={False}")
    answer = getAnswer(content, userId, False)

    del taskMap[userId]

    reply = Reply(ReplyType.TEXT, answer)
    return reply

# 搜集到足够的群聊内容，就主动发表一次消息
def handleGroup(context):
    msg = context['msg']

    if (context.type != ContextType.TEXT):
        if (msg.is_at): return Reply(ReplyType.ERROR, '暂不支持该类型消息...')
        else: return

    groupId = msg.from_user_nickname or msg.from_user_id

    appendMessage(groupId, f'用户「{msg.actual_user_nickname}」说: {msg.content}')

    # 如果群里 @ ai 助手或者群里聊天记录数量达到阈值，就进行回复
    if (msg.is_at):
        if (taskMap.get(groupId)):
            return Reply(ReplyType.TEXT, f'正在处理「{taskMap[groupId]}」，请稍后再提问')
        taskMap[groupId] = context.content # 记录上次的问题

        answer = getAnswer(context.content, groupId, isGroup=True)
        appendMessage(groupId, f'用户「{msg.to_user_nickname}」说：{answer}')
        del taskMap[groupId]

        return Reply(ReplyType.TEXT, answer)

    messages = getMessages(groupId)
    if (len(messages) > MESSAGE_LIMIT):
        if (taskMap.get(groupId)): return
        taskMap[groupId] = '系统任务'

        content = json.dumps(messages, ensure_ascii=False)
        content = f"""
            注意，我是在一个聊天群里，我会给你群里最近的一些聊天记录，
            你需要根据聊天记录，帮我给出一个的高质量的回复，回复后，总是能够帮助到一些人，
            比如解答了别人关心的问题；或是安慰了别人，或是给与别人中肯的建议等。
            当然，如果感觉不需要参与回复，你就回复「无需回答」四个字。
            好了，下面是近期具体的聊天记录（json 格式）：
            {content}
        """
        answer = getAnswer(content, groupId, isGroup=True)
        appendMessage(groupId, f'用户「{msg.to_user_nickname}」说：{answer}')

        del taskMap[groupId]

        return Reply(ReplyType.TEXT, answer)
    
