'''
VkBot
'''
import vk
from time import sleep
import requests as req
import re
import os
import json


class NotContainFromInsta(Exception):
    def __str__(self):
        return 'No photo or video from Instagram'


def parseJson(jsonFile='C://Server/www/tokenowner.json'):
    try:
        jsObj = open(jsonFile, "r")
        pObj = json.load(jsObj)
    except ValueError as VErr:
        print(VErr)
    except IOError as IOErr:
        print(IOErr)
    finally:
        jsObj.close()
    return (pObj['access_token'], pObj['owner_id'])


def loadF(newUrl, filename, pathToSave='C://Server/www/phv/'):
    try:
        response = req.get(newUrl, stream=True)
        with open(pathToSave+filename, "wb") as fileToSave:
            fileToSave.write(response.content)
    except IOError as IOErr:
        print(IOErr)
    except req.exceptions.RequestException as ReqErr:
        print(ReqErr)    


def listOfContent(body):
    regEx = re.compile(r'(("display_url"|"video_url"):\"https://(.*?).(jpg|mp4)")')
    result = regEx.finditer(body)

    content = []
    for ma in result:
        if str(ma.group(0)) not in content:
            content.append(str(ma.group(0)))

    return content


def getAttachment(typeContent, filename, pathToSave='C://Server/www/phv/'):
    attach = ""
    if typeContent == "photo":
            try:
                placeUp = vkapi.photos.getMessagesUploadServer.json()
                upload = req.post(url=placeUp['upload_url'], 
                                  files={typeContent: open(pathToSave+filename, 'rb')}).json()
                savePhoto = vkapi.photos.saveMessagesPhoto(photo=upload['photo'], 
                                                           server=upload['server'],
                                                           hash=upload['hash'])[0]
                attach = str(savePhoto['id'])
            except req.exceptions.RequestException as ReqErr:
                print (ReqErr)    
            except Exception as err:
                print(err)
    else:
        try:
            placeVideo = vkapi.video.save(is_private=1)
            file_ = {'video_file': (filename, open(pathToSave+filename, 'rb'))}
            reqUpVideo = req.post(placeVideo['upload_url'], files=file_).json()
            attach = 'video'+owner_id+'_'+str(reqUpVideo['video_id'])
        except req.exceptions.RequestException as ReqErr:
            print (ReqErr)
        except Exception as err:
            print(err)
    return attach


def loadInst(body, uid):
    delUnusedFiles()
    vkapi.messages.setActivity(type='typing', user_id=uid)    
    headers = {'User-Agent': 'Mozilla/5.0\
               (Macintosh; Intel Mac OS X 10.9; rv:45.0)\
               Gecko/20100101 Firefox/45.0'}
    try:
        body = str(req.get(body, headers=headers).text) 
    except req.exceptions.RequestException as ReqErr:
        print(ReqErr)
        raise NotContainFromInsta       
    content = listOfContent(body)            
    if len(content) == 0:
        print(len(content))
        raise NotContainFromInsta
    
    delSize = 0
    typeContent = "" 
    for newUrl in content:
        if "video" in newUrl:
            delSize = 13
            typeContent = "video"
        else:
            delSize = 15
            typeContent = "photo"       
        newUrl = newUrl[delSize:len(newUrl)-1]    
        filename = newUrl[newUrl.rfind('/')+1:]   
        loadF(newUrl, filename)    
        attach = getAttachment(typeContent, filename)          
        vkapi.messages.send(user_id=uid, message='Прямая сслыка: '+newUrl, 
                            attachment=attach)


def delUnusedFiles(path='C://Server/www/phv/'):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            try:
                os.remove(os.path.join(path, file))
            except OSError as OSErr:
                print(OSErr)
                continue


token, owner_id = parseJson()    
session = vk.AuthSession(access_token=token) 
vkapi = vk.API(session)


def main():
    while True:
        delUnusedFiles()
        try:
            msg = vkapi.messages.get()[1:]
        except Exception as err:
            print(err)
            continue

        if len(msg) == 0:
            sleep(4)
            continue

        for message in msg:
            uid = message['uid']
            mid = message['mid']
            body = message['body']
            try:
                loadInst(body, uid)
            except NotContainFromInsta as err:
                vkapi.messages.send(user_id=uid, message="Некорректная ссылка")
            finally:
                vkapi.messages.delete(message_ids=mid)
            sleep(4)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
