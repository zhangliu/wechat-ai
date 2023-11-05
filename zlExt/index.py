import json
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
from zlExt.models.index import appendMessage, getMessages
from zlExt.service import getAnswer

taskMap = {}
MESSAGE_LIMIT = 10

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

    if not msg.is_at: return
    if (taskMap.get(groupId)):
        return Reply(ReplyType.TEXT, f'正在处理「{taskMap[groupId]}」，请稍后再试')

    isSumary = (context.content or '') == '总结一下'
    if (isSumary):
        taskMap[groupId] = '系统任务'
        messages = getMessages(groupId)
        content = json.dumps(messages, ensure_ascii=False)
        content = f"""
            注意，我是在一个聊天群里，我会给你群里最近的一些聊天记录，
            你需要根据聊天记录，给出合适的回复，回复的目的是能够帮助到别人，例如：
            1. 能够帮助解答某些人的问题。
            2. 能够安慰到别人。
            3. 能够给与别人一些中肯的建议。
            4. 能够发现别人的亮点，给与合适真诚的赞扬。
            注意，直接用我的口吻给出简洁的回复即可，
            我会直接拷贝你的回复到群里的，所以不要让群里看出我是一个 AI，或者知道我是借助你进行回复的。
            好了，下面是近期具体的聊天记录（json 格式）：
            {content}
        """
        answer = getAnswer(content, groupId, isGroup=True)
        del taskMap[groupId]

        return Reply(ReplyType.TEXT, answer)
    else:
        appendMessage(groupId, f'用户「{msg.actual_user_nickname}」说: {msg.content}')
        taskMap[groupId] = context.content # 记录上次的问题

        answer = getAnswer(context.content, groupId, isGroup=True)
        del taskMap[groupId]
        appendMessage(groupId, f'用户「{msg.to_user_nickname}」说：{answer}')

        return Reply(ReplyType.TEXT, answer)
    
