import os
import requests
from zlExt.utils import logger

from zlExt.utils.imgHelper import toBase64
from zlExt.utils.runHelper import runTimes

apiKey = os.environ.get('API_KEY')

imgAiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent'
textAiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
headers = {'Content-Type': 'application/json'}

def getImgAnswer(msg):
    try:
        content = msg['content']
        imgData = toBase64(msg['img'])
        logger.log('start to handle msg:', msg)
        body = { 
            "contents": [
                {
                    "parts": [
                        {"text": content},
                        {"inline_data": {"mime_type": "image/png", "data": imgData}}
                    ]
                }
            ]
        }
        response = runTimes(3, 30, requests.post, f'{imgAiUrl}?key={apiKey}', json=body, headers=headers)
        data = response.json()
        answer = data['candidates'][0]['content']['parts'][0]['text']
        return answer
    except Exception as e:
        logger.log(f'getAnswer error: {str(e)}')
        raise e
    
def getTextAnswer(msg, history=[]):
    try:
        content = msg['content']
        logger.log('start to handle msg:', msg)
        contents = history
        contents.append({
            "role": "user",
            "parts": [{"text": content}]
        })
        body = { 
            "contents": contents
        }
        response = runTimes(3, 30, requests.post, f'{textAiUrl}?key={apiKey}', json=body, headers=headers)
        data = response.json()

        if ('error' in data): raise Exception(data['error'])
        if ('candidates' not in data): raise Exception(data)

        answer = data['candidates'][0]['content']['parts'][0]['text']
        return answer
    except Exception as e:
        logger.log(f'getAnswer error: {str(e)}')
        raise e