def getPrompt(msg):
    return f"""
        请把「{msg.content}」翻译成英语，注意要口语化，不要使用书面语（如果已经是英语了，就看看语法有啥问题，或者有没有更好的表达方式）。
    """