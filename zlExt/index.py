import json
from bridge.reply import Reply, ReplyType
from bridge.context import ContextType
from common.log import logger
from zlExt.service import getAnswer

taskMap = {}
messageMap = {}
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

    # 如果群里 @ ai 助手或者群里聊天记录数量达到阈值，就进行回复
    if (msg.is_at):
        if (taskMap.get(groupId)):
            return Reply(ReplyType.TEXT, f'正在处理「{taskMap[groupId]}」，请稍后再提问')
        taskMap[groupId] = context.content # 记录上次的问题

        answer = getAnswer(context.content, groupId, isGroup=True)
        del taskMap[groupId]

        return Reply(ReplyType.TEXT, answer)

    messageMap.setdefault(groupId, [])
    messageMap[groupId].append(f'用户「{msg.actual_user_nickname}」说: {msg.content}')

    if (len(messageMap[groupId]) > MESSAGE_LIMIT):
        if (taskMap.get(groupId)): return
        taskMap[groupId] = '系统任务'

        content = json.dumps(messageMap[groupId], ensure_ascii=False)
        content = f"""
            注意，我在一个聊天群里，我会给你群里最近的一些聊天记录，
            你需要根据聊天记录，帮我给出一个合理的高质量的回复，我回复后，要么是能活跃群里的气氛，
            要么能够解释聊天中的一些疑问点，要么是能够给与一个中肯的结论。
            总之，给出回复后，参与聊天的人，要么能够获得一些快乐，要么能够获得一些知识，要么能够提高一些认知，
            就是能够有所收获。
            当然，如果感觉不需要参与回复，你就回复「无需回答」四个字。
            好了，下面是具体的聊天记录，我之前可能也给了你一些之前的聊天记录，你可以结合之前的聊天记录一起分析，
            目前最新的聊天记录如下（json 格式内容）：
            {content}
        """
        answer = getAnswer(content, groupId, isGroup=True)
        messageMap[groupId].append(f'用户「{msg.to_user_nickname}」说：{answer}')

        del messageMap[groupId]
        del taskMap[groupId]

        return Reply(ReplyType.TEXT, answer)
    
