import requests
import urllib.parse
# from zlExt.config import zlConfig

# def getAnswer(question: str):
#     try:
#         url = "https://openai.api2d.net/v1/chat/completions"
#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {zlConfig.fkey}' # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格。
#         }
#         data = {
#             "model": "gpt-3.5-turbo",
#             "messages": [{"role": "user", "content": question}]
#         }

#         response = requests.post(url, headers=headers, json=data)
#         data = response.json()
#         return data['choices'][0]['message']['content']
#     except Exception as e:
#         return f'[错误]: 获取答复失败！'

domain = 'http://localhost:3030'

def getAnswer(prompt: str, userId, isGroup: bool):
    try:
        url = f"{domain}/wechat/prompt?prompt={urllib.parse.quote(prompt)}&userId={userId}&isGroup={int(isGroup)}"
        headers = { 'Content-Type': 'application/json' }
        response = requests.get(url, headers=headers)
        data = response.json()
        return data['data']
    except Exception as e:
        return f'[错误]: 获取答复失败！{str(e)}'
    
def postUUID(uuid):
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