import pickle
from newspaper import Article
import os
import requests
import json
import ast
from urllib.request import urlopen
from PIL import Image
from io import StringIO

ARTICLE_ENDPOINT = "https://master.stage.binarysages.com/api/Articles/upsertArticle"
PUBLISH_ENDPOINT = "https://master.stage.binarysages.com/api/Articles/publishArticle"
IMAGE_ENDPOINT = "https://teast.stage.binarysages.com/api/Images/upload"
LOGIN_ENDPOINT = "https://master.stage.binarysages.com/api/CoreUsers/login?include=user"

credentials = {
				"email": "vTlVNITVjWDMPEq@test.test",
				"password": "123456789"
			}
auth = requests.post(LOGIN_ENDPOINT, credentials)
authHeader = json.loads(auth.text).get('id')
headers = {'content-type': 'application/json', 'Authorization': authHeader}

def tohtml(strToConvert):
    return ''.join("<p>%s</p>" % line
          for line in strToConvert.splitlines()
          if line)
count = 0
target = 'result.pickle'
if os.path.getsize(target) > 0:      
    with open(target, "rb") as f:
        unpickler = pickle.Unpickler(f)
        articles = unpickler.load()
        for category in articles:
            for article in articles[category]:
                data = {
                        "article" : {
                        "draftTitle": article.get('title'),
                        "draftContent": tohtml(article.get('content')),
                        "draftImageId": None,
                        "image": "",
                        "categories": []
                    }
                } 
                if article.get('image'):
                    image = requests.get(article.get('image'))
                    with open('temp.jpg', 'wb') as file:
                        file.write(image.content)
                    with open('temp.jpg', 'rb') as file:
                        r = requests.post(url = IMAGE_ENDPOINT, files = {'image': file}) 
                        data["article"]["draftImageId"] = str(json.loads(r.text).get('id'))
                print(data)
                r = requests.post(url = ARTICLE_ENDPOINT, data = json.dumps(data), headers = headers) 
                print(json.loads(r.text).get('id'))
                publishData = {
                    "articleId": str(json.loads(r.text).get('id'))
                }
                r2 = requests.post(url = PUBLISH_ENDPOINT, data = json.dumps(publishData), headers = headers) 
                print(r2.text)
                if r2.status_code == 200:
                    count += 1
print(count)
