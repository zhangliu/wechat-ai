def getPrompt(msg):
    return f"""
        请把「{msg.content}」翻译成英语，注意要口语化，不要使用书面语。
    """