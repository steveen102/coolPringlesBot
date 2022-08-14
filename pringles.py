import requests
import re
from capmonster_python import RecaptchaV2Task
from time import sleep
from requests.auth import HTTPProxyAuth
from requests.auth import HTTPBasicAuth
import multiprocessing
import time

#                      DETAILS
#------------------------------------------------------------
taskNumber = 10
apiKey = ""
proxy = ""
currID = 0
emailJig = "test"
catchall = "catchall.com"
#per task
timesToLoop = 100

#-------------------------------------------------------------



homeURL = 'https://pringlessweepstakes.com/'
playUrl = "https://pringlessweepstakes.com/play.php"
validateUrl = "https://pringlessweepstakes.com/validate_info.php"
finalUrl = 'https://pringlessweepstakes.com/final.php'

pringlesParams = {
    
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer' : 'https://pringlessweepstakes.com/',
    'Host': 'pringlessweepstakes.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'
}


def main(taskID, loopNum):
    
    
    for index in range(loopNum):
        try:
            
            proxies = {
                'http' : proxy,
                'https' : proxy
            }

            jar = requests.cookies.RequestsCookieJar()

            jar.update(sendHome(taskID=taskID, proxies=proxies))

            captchaResp = solve()

            print(str(taskID)+" : done getting captcha")
            timeout = time.time() + 60*2   # 2 minutes from now
            
            temp = sendValidation(taskID=taskID, captcha=captchaResp, id=index, cookies=jar, proxies=proxies, timeout=timeout)
            if (temp == -1):
                continue
            else:
                jar.update(temp)

            temp2 = sendPlay(taskID=taskID, captcha=captchaResp, id=index, cookies=jar, proxies=proxies, timeout=timeout)
            if (temp == -1):
                continue
            else:
                jar.update(temp2)
        
            getResult(taskID=taskID, proxies=proxies, cookies=jar)
        except Exception as e: 
            print(e)
            

    
    

def solve():
    test = RecaptchaV2Task(apiKey)
    task_id = test.create_task("https://pringlessweepstakes.com/", "6Lfw-8ggAAAAAPik2G5fnc7cie4cOl4VrD7UOSk1")
    result = test.join_task_result(task_id)
    return result['gRecaptchaResponse'] 
def sendHome (taskID, proxies):
    jar = requests.cookies.RequestsCookieJar()
    notsent = True
    while (notsent):
        print(str(taskID)+ " : Grabbing Home")
        home = requests.post(homeURL, params=pringlesParams, cookies=jar, proxies=proxies)
        print(str(taskID)+ " : Done: "+ str(home.status_code))
        jar.update(home.cookies)        
        if(home.status_code == 200):
            notsent = False
    return jar
def sendValidation(taskID, captcha, id, cookies, proxies, timeout):
    pringlesData = {
    'email' : str(id)+emailJig+str(taskID)+"@"+catchall,
    'email_confirm' : str(id)+emailJig+str(taskID)+"@"+catchall,
    'month' : 4,
    'day' : 22,
    'year' : 1998,
    'agreement' : "on",
    'g-recaptcha-response': captcha
    }

    jar = requests.cookies.RequestsCookieJar()
    notsent = True
    while (notsent):
        if(time.time() > timeout):
            print(str(taskID) + " : TIMEOUT")
            return -1
        print(str(taskID)+ " : Validating Info")
        req = requests.post(validateUrl, params=pringlesParams, data=pringlesData, cookies=cookies, proxies=proxies)
        jar.update(req.cookies)
        print(str(taskID)+ " : Done Validating : "+ str(req.status_code))
        
        if(req.status_code == 200):
            notsent = False
    return jar
def sendPlay(taskID, captcha, id, cookies, proxies, timeout):
    pringlesData = {
    'email' : str(id)+emailJig+str(taskID)+"@"+catchall,
    'email_confirm' : str(id)+emailJig+str(taskID)+"@"+catchall,
    'month' : 4,
    'day' : 22,
    'year' : 1998,
    'agreement' : "on",
    'g-recaptcha-response': captcha
    }

    jar = requests.cookies.RequestsCookieJar()
    notsent = True
    while (notsent):
        if(time.time() > timeout):
            print(str(taskID) + " : TIMEOUT")
            return 1
        print(str(taskID)+ " : Playing Game")
        req = requests.post(playUrl, params=pringlesParams, data=pringlesData, cookies=cookies, proxies=proxies)
        jar.update(req.cookies)
        print(str(taskID)+ " : Done Playing : "+ str(req.status_code))
        
        if(req.status_code == 200):
            notsent = False
        elif (req.status_code == 302):
            print(cookies)
    return jar
def getResult(taskID, proxies, cookies):
    jar = requests.cookies.RequestsCookieJar()
    notsent = True
    while (notsent):
        print("sending")
        final = requests.post(finalUrl, params=pringlesParams, cookies=cookies, proxies=proxies)
        print("done sending")

        jar.update(final.cookies)
        
        lose = bool(re.search("(AWWW\.\.\. SORRY, YOU DIDN\'T WIN\.)",final.text))
        
        if(lose):
            print(str(taskID)+" : LOST")
        else:
            print(str(taskID)+" : -----------------WINNER--------------")

        if(final.status_code == 200):
            notsent = False
        




if __name__ == "__main__":
    d = {}
    for i in range(taskNumber):
        d['task{0}'.format(i)] =  multiprocessing.Process(target=main, args=[i, timesToLoop])
        d['task{0}'.format(i)].start()
    for i in range(taskNumber+1):
        d['task{0}'.format(i)].join()
        
        

    



