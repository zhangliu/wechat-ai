import os
import requests
from zlExt.utils import logger

from zlExt.utils.imgHelper import toBase64
from zlExt.utils.runHelper import runTimes

apiKey = os.environ.get('API_KEY')
aiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent'
headers = {'Content-Type': 'application/json'}

def getAnswer(msg):
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
        response = runTimes(3, 30, requests.post, f'{aiUrl}?key={apiKey}', json=body, headers=headers)
        data = response.json()
        answer = data['candidates'][0]['content']['parts'][0]['text']
        return answer
    except Exception as e:
        logger.log(f'getAnswer error: {str(e)}')
        raise e