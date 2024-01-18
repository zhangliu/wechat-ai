import requests
import os

# 如果运行在mac电脑本地，就用云上的服务，否则在云上，就用本地的服务
# domain = 'http://3.26.152.17' if os.environ.get('USER') == 'bytedance' else 'http://localhost:3000'
domain = 'http://localhost:3000'

def getBardAnswer(prompt: str, chatName, aiName='', isGroup=False):
    try:
        url = f"{domain}/bot/bard/prompt?chatName=*{chatName}&aiName={aiName}&isGroup={int(isGroup)}"
        headers = { 'Content-Type': 'application/json' }
        body = { "prompt": prompt }
        response = requests.post(url, json=body, headers=headers)
        data = response.json()
        return data['data']
    except Exception as e:
        return f'[错误]: 获取答复失败！{str(e)}'
    
def postUUID(uuid):
    return # TODO zl 临时注释掉，因为现在微信助手很稳定了，不需要利用 uuid 经常登录
    try:
        url = f"{domain}/wechat/uuid"
        headers = { 'Content-Type': 'application/json' }
        body = { "uuid": uuid }
        requests.post(url, json=body, headers=headers)
        print("[zlExt] success set uuid:", uuid)
    except Exception as e:
        print("[zlExt] postUUID error:", e)

def deleteUUID():
    try:
        url = f"{domain}/wechat/uuid"
        requests.delete(url)
    except Exception as e:
        print("[zlExt] deleteUUID error:", e)