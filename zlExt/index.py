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

    isSumary = context.content == '你怎么看'
    if (isSumary):
        taskMap[groupId] = '系统任务'
        messages = getMessages(groupId)
        content = json.dumps(messages, ensure_ascii=False)
        content = f"""
            注意，我是在一个聊天群里，我会给你群里最近的一些聊天记录，
            你需要根据聊天记录，提炼大概得内容，给出一些点评，点评的主要目的是：
            1. 帮助解答某些人的问题。
            2. 发现别人的亮点，给与中肯真诚的赞扬。
            注意，直接用我的口吻给出简洁的点评即可，
            我会直接拷贝你的点评到群里的，所以不要让群里的人看出我是一个 AI，或者知道我是借助AI进行点评。
            好了，下面是近期具体的聊天记录（json 格式）：
            {content}
        """
        answer = getAnswer(content, groupId, isGroup=True)
        del taskMap[groupId]

        return Reply(ReplyType.TEXT, answer)
    else:
        taskMap[groupId] = context.content # 记录上次的问题

        appendMessage(groupId, f'用户「{msg.actual_user_nickname}」说: {msg.content}')
        answer = getAnswer(context.content, groupId, isGroup=True)
        del taskMap[groupId]
        appendMessage(groupId, f'用户「{msg.to_user_nickname}」说：{answer}')

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
    
