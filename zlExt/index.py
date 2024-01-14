from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
import threading
from datetime import datetime, timedelta
import zlExt.bots.gemini.index as gemini
import zlExt.bots.gemini.history as geminiHistory
from zlExt.utils.logger import log
import zlExt.utils.promptHelper.commonPrompt as commonPrompt

taskMap = {}
MESSAGE_LIMIT = 20

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

    try:
        logger.info(f"will get answer use: content={content}; userId={userId}; isGroup={False}")
        
        messages = geminiHistory.getMessages(userId)
        answer = gemini.getTextAnswer({"content": content}, history=messages)
        geminiHistory.appendMessage(userId, {"content": msg.content, "role": "user"})
        geminiHistory.appendMessage(userId, {"content": answer, "role": "model"})

        reply = Reply(ReplyType.TEXT, answer)
        return reply
    except Exception as e:
        return Reply(ReplyType.TEXT, str(e)[:120])
    finally:
        del taskMap[userId]

def handleSingleImg(context):
    context['msg'].prepare() # 初始化消息，将图片下载到本地
    imgPath = context.content

# 搜集到足够的群聊内容，就主动发表一次消息
def handleGroup(context):
    msg = context['msg']
    groupId = msg.from_user_nickname or msg.from_user_id

    if (msg.is_at): return handleGroupAt(context)
    if (context.type != ContextType.TEXT): return

    geminiHistory.appendGroupUserMessage(groupId, f'用户「{msg.actual_user_nickname}」说: {msg.content}')
    geminiHistory.appendGroupModelMessage(groupId, f'收到，你的消息我先记下了')

def handleGroupAt(context):
    msg = context['msg']
    groupId = msg.from_user_nickname or msg.from_user_id

    if (context.type != ContextType.TEXT):
        return Reply(ReplyType.ERROR, '暂不支持该类型消息...')

    if (taskMap.get(groupId)):
        return Reply(ReplyType.TEXT, f'正在处理「{taskMap[groupId]}」，请稍后再试')
    taskMap[groupId] = context.content # 记录上次的问题

    try:
        history = geminiHistory.getGroupMessages(groupId)
        history = geminiHistory.addPrompt(history, commonPrompt.getPrompt(msg))
        answer = gemini.getTextAnswer({"content": context.content}, history)
        geminiHistory.appendGroupUserMessage(groupId, f'用户「{msg.actual_user_nickname}」问: {msg.content}')
        geminiHistory.appendGroupModelMessage(groupId, answer)

        return Reply(ReplyType.TEXT, answer)
    except Exception as e:
        return Reply(ReplyType.TEXT, str(e)[:120])
    finally:
        del taskMap[groupId]

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