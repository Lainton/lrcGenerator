import os
import re
import requests
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#匹配的文件后缀
endList = ['ncm', 'mp3', 'ape', 'flac']

#chrome 驱动下载
## http://chromedriver.storage.googleapis.com/index.html
chromeDriver = './chromedriver'
driver = webdriver.Chrome(chromeDriver)

#歌曲所在与保存路径
localDir = '../'


#网易云音乐 歌词下载接口api
cloudApiUrl = 'https://api.imjad.cn/cloudmusic/'

#获取歌名列表
def getSongs():
    global localDir
    global endList
    songList = []
    songNames = []
    songFiles = []

    #获取歌曲文件保存的绝对路径
    localPath = os.path.abspath(localDir)+'/'

    #遍历文件 根目录，当前路径下文件夹， 当前路径下文件
    for root, dirs, files in os.walk(localDir):
        for file in files:
            #匹配文件在 指定结尾后缀列表中
            try:
                if file.rsplit('.', 1)[1] in endList: # rsplit 表示从right开始分割 第1个.
                    songList.append(localPath+file)
                    songFiles.append(file)
                    songNames.append(file.rsplit('.', 1)[0])

            except Exception as e:
                print(file)

    return songList, songFiles, songNames

#获取一首歌的id
def getSongId(song):
    global driver
    id = ''

    #加载搜索页面
    driver.get("https://music.163.com/#/search/m/")
    #等待页面加载完成
    try:
        #切换frame
        frame1 = driver.find_element_by_css_selector(".g-iframe")
        driver.switch_to.frame(frame1)

        #查找搜索框
        inputElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "m-search-input"))
        )


        # inputElement = driver.find_element_by_id("m-search-input")

        #清空输入框
        inputElement.clear()

        #输入歌名 回车
        inputElement.send_keys(song)
        inputElement.send_keys(Keys.RETURN)

        #等待搜索歌曲
        WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_class_name("srchsongst"))

        #正则匹配歌曲，获取id
        pattern = re.compile(r'<div cla.*?song_(.*?)" cla.*?b title="(.*?)">.*?artist.*?>(.*?)</a>.*?album.*?le="(.*?)">.*?</div>')
        #返回查询结果第一个元组
        song = pattern.findall(driver.page_source, re.S)[0]

        #判断歌名和原来的匹配

        #赋值给id
        id = song[0]
    except Exception as e:
        print(e)


    return id


#获取所有歌的id
def getSongsId(songNames):
    songsId = []

    #将歌名传入 getSongId()
    for song in songNames:
        songsId.append(getSongId(song))

    #打印出获取到到 名字 对应 id
    for i in range(songNames.__len__()):
        print(songNames[i]+'----'+songsId[i])

    return songsId


#获取歌词
def getLrc(songId):
    lrc = ''
    tlyric = ''

    #参数列表
    payload = {'type': 'lyric', 'id': songId}

    #获取返回值
    request = requests.get(cloudApiUrl, params=payload)

    #解析收到的json数据
    jsonDic = json.loads(request.text)

    #判断是否收到歌词（lrc 或 tlyric是否为key)
    if 'lrc' in jsonDic:
        #获取英文歌词部分
        lrc = jsonDic['lrc']['lyric']
    elif 'tlyric' in jsonDic:
        #获取中文歌词
        tlyric = jsonDic['tlyric']['lyric']

    return [lrc, tlyric]



#写入lrc['lrc','tlyric']
def writeLrc(file, lrc):
    file = file.rsplit('.', 1)[0]+'.lrc'
    try:
        with open(file, 'wt') as f:
            for l in lrc:
                f.write(l)
        return True
    except Exception as e:
        print(e)
        return False


#下载lrc并写入文件
def downloadLrc(songNames, songsId, songsList):
    global cloudApiUrl

    #遍历执行每一首歌
    for id in songsId:
        #判断id为空 跳过
        if not id.__len__():
            continue

        #获取lrc[]
        lrc = getLrc(id)

        #获取id对应的名字
        songIndex = songsId.index(id)

        #判断lrc有没有 如果lrc['','']就跳过这首歌
        if not (len(lrc[0]) or len(lrc[1])):
            print(songNames[songIndex]+'---!!!!--' + 'NO LYRIC!')
            continue


        #写入文件
        if writeLrc(songsList[songIndex], lrc):
            print(songNames[songIndex]+'----->' + 'success')
        else:
            print(songNames[songIndex]+'---!!!!--' + 'FAIL!')



if __name__ == '__main__':

    #歌曲绝对路径名字
    songsList = []
    #歌曲文件名字
    songFiles = []
    #歌曲的名字 没有后缀
    songNames = []
    #歌曲id号
    songsId = []

    #遍历目录获取歌名列表
    songsList, songFiles, songNames = getSongs()
    print(songsList)

    try:
        #网易云查询序号
        songsId = getSongsId(songNames)

        #lrc歌词网站查询获取lrc
        #写入 歌名.lrc文件
        downloadLrc(songNames, songsId, songsList)

    except Exception as e:
        print(e)

    finally:
        #关闭浏览器
        driver.close()