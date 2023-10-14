import requests
from zlExt.config import zlConfig

def getAnswer(question: str):
    try:
        url = "https://openai.api2d.net/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {zlConfig.fkey}' # <-- 把 fkxxxxx 替换成你自己的 Forward Key，注意前面的 Bearer 要保留，并且和 Key 中间有一个空格。
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}]
        }

        response = requests.post(url, headers=headers, json=data)
        data = response.json()
        return data['choices'][0]['message']['content']
    except:
        return f'[错误]: 获取答复失败！'