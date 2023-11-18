import json
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
import threading
from datetime import datetime, timedelta
from zlExt.models.index import appendMessage, getMessages
from zlExt.service import getAnswer
from zlExt.utils.logger import log

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
    groupId = msg.from_user_nickname or msg.from_user_id

    if (msg.is_at): return handleGroupAt(context)
    if (context.type != ContextType.TEXT): return

    appendMessage(groupId, f'用户「{msg.actual_user_nickname}」说: {msg.content}')


def handleGroupAt(context):
    msg = context['msg']
    groupId = msg.from_user_nickname or msg.from_user_id

    if (context.type != ContextType.TEXT):
        return Reply(ReplyType.ERROR, '暂不支持该类型消息...')

    if (taskMap.get(groupId)):
        return Reply(ReplyType.TEXT, f'正在处理「{taskMap[groupId]}」，请稍后再试')

    taskMap[groupId] = context.content # 记录上次的问题
    appendMessage(groupId, f'用户「{msg.actual_user_nickname}」问: {msg.content}')
    messages = getMessages(groupId)
    content = json.dumps(messages, ensure_ascii=False)
    content = f"""
        注意，你现在在一个聊天群里，你在群里的名字叫：「{msg.to_user_nickname}」，你需要根据群里最近的聊天记录，给出恰当的回复，回复的主要目的是：
        1. 结合聊天上下文，帮助解答问题。
        2. 结合聊天上下文，发现别人的亮点，给与赞扬，让他更喜欢你。
        回复时请注意：
        1. 你在群里的名字叫：「{msg.to_user_nickname}」，如果某个人 @ 你的名字，表示他在主动询问你，如果聊天中 @ 你多次，你只需回复最后一个问题即可。
        2. 请务必结合上下文给出比较简洁口语化的回复，内容最好不要超过 30 个字！
        好了，下面是最近的聊天上下文（json 格式）：
        {content}
    """
    answer = getAnswer(content, groupId, isGroup=True)
    del taskMap[groupId]
    appendMessage(groupId, f'用户「{msg.to_user_nickname}」回复：{answer}')

    return Reply(ReplyType.TEXT, answer)

# 向文件助手定时发消息来保活
timer = None

def handleSelfMsg(itchat):
    global timer

    if timer:
        timer.cancel()
        timer.join()
        timer = None

    sendAliveMsg(itchat)

def sendAliveMsg(itchat):
    global timer
    try:
        now = (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
        itchat.send(f'Time => {now}', toUserName='filehelper')

        timer = threading.Timer(60, sendAliveMsg, args=[itchat])
        timer.start()
    except Exception as e:
        log('send filehelper message error:', e)
        raise e