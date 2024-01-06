import base64

def toBase64(imgPath):
    with open(imgPath, 'rb') as imgFile:
        return base64.b64encode(imgFile.read()).decode()