import json
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
import threading
from datetime import datetime, timedelta
import zlExt.bots.gemini.index as gemini
import zlExt.bots.gemini.history as geminiHistory
import zlExt.utils.historyMsg.index as historyMsg
from zlExt.utils.logger import log
# import zlExt.utils.promptHelper.commonPrompt as commonPrompt
import zlExt.utils.promptHelper.englishPrompt as englishPrompt
import zlExt.service as service

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
    if (not msg.is_at): return handleGroupNoAt(context)
    if (context.type != ContextType.TEXT): return

    historyMsg.appendGroupMessage(groupId, f'「{msg.actual_user_nickname}」说: {msg.content}')

def handleGroupAt(context):
    msg = context['msg']
    groupId = msg.from_user_nickname or msg.from_user_id

    if (context.type != ContextType.TEXT):
        return Reply(ReplyType.ERROR, '暂不支持该类型消息...')

    if (taskMap.get(groupId)):
        return Reply(ReplyType.TEXT, f'正在处理「{taskMap[groupId]}」，请稍后再试')
    taskMap[groupId] = context.content # 记录上次的问题

    try:
        historyMsg.appendGroupMessage(groupId, f'「{msg.actual_user_nickname}」问: {msg.content}')
        messages = historyMsg.getGroupMessages(groupId)
        prompt = json.dumps(messages, ensure_ascii=False)
        # prompt = commonPrompt.getPrompt(msg, messages)
        # answer = gemini.getTextAnswer({"content": prompt})
        answer = service.getBardAnswer(prompt, groupId, msg.to_user_nickname, True)
        # limitAnswer = f'{answer[:200]}...' if len(answer) > 200 else answer
        historyMsg.appendGroupMessage(groupId, f'「{msg.to_user_nickname}」回答: {answer}')

        return Reply(ReplyType.TEXT, answer)
    except Exception as e:
        return Reply(ReplyType.TEXT, str(e)[:120])
    finally:
        del taskMap[groupId]

def handleGroupNoAt(context):
    msg = context['msg']
    groupId = msg.from_user_nickname or msg.from_user_id
    content = (context.content or '').strip()
    if (groupId != 'Ai助手测试群'): return
    if (context.type != ContextType.TEXT): return

    try:
        logger.info(f"will get answer use: content={content}; groupId={groupId}")
        
        prePrompt = englishPrompt.getPrompt(msg)
        answer = gemini.getTextAnswer({"content": prePrompt}, history=[])
        geminiHistory.appendMessage(groupId, {"content": msg.content, "role": "user"})
        geminiHistory.appendMessage(groupId, {"content": answer, "role": "model"})

        reply = Reply(ReplyType.TEXT, answer)
        return reply
    except Exception as e:
        return Reply(ReplyType.TEXT, str(e)[:120])


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