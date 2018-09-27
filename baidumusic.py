#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import  json
import redis
import time

allMusicInfo = {
                "海阔天空":"Beyond",
                "第一次爱的人":"王心凌",
                "鬼迷心窍":"李宗盛",
                "理想":"赵雷",
                "成都":"赵雷",
                "一路向北":"周杰伦",
                "十年":"陈奕迅",
                "我被青春撞了一下腰":"张真",
                "失恋阵线联盟":"草蜢",
                "Rolling In The Deep":"Done Again",
                }

allMusicData = []

def deal_ByName(Name):
    jsonurl = 'http://tingapi.ting.baidu.com/v1/restserver/ting?method=baidu.ting.search.catalogSug&query=%s' % Name
    jsonhtml = requests.get(jsonurl).text

    jsondata = eval(jsonhtml)
    listdata = jsondata['song']
    #print(listdata)

    songID = matched_Music(listdata,Name)

    deal_ByID(songID)



 #匹配歌曲
def matched_Music(listdata,Name):
    singer = allMusicInfo[Name]

    for i in listdata:
        # print(i)
        artistname = i["artistname"]
        # print(artistname)
        if  singer == artistname:
            return i["songid"]
        if singer in i["songname"]:
            return i["songid"]

    # 找不到匹配的返回第一个
    for i in listdata:
        return i["songid"]

    return ''


def deal_ByID(ID):
    jsonurl = 'http://tingapi.ting.baidu.com/v1/restserver/ting?method=baidu.ting.song.play&songid=%s' % ID
    jsonhtml = requests.get(jsonurl).text

    jsondata = json.loads(jsonhtml)

    songInfo = jsondata["songinfo"]

    bitrateInfo = jsondata["bitrate"]

    freeFlag = bitrateInfo["free"]

    if  freeFlag != 1:
        return


    songData = {}
    songData["author"] = songInfo["author"]
    songData["song_id"] = songInfo["song_id"]
    songData["title"] = songInfo["title"]
    songData["lrclink"] = songInfo["lrclink"]     #歌词有的有有的没有
    songData["pic_big"] = songInfo["pic_big"]
    songData["bitrate_fee"] = songInfo["bitrate_fee"]
    songData["all_rate"] = songInfo["all_rate"]
    songData["pic_small"] = songInfo["pic_small"]

    songData["show_link"] = bitrateInfo["show_link"]
    songData["file_size"] = bitrateInfo["file_size"]
    songData["file_extension"] = bitrateInfo["file_extension"]
    songData["file_duration"] = bitrateInfo["file_duration"]
    songData["file_bitrate"] = bitrateInfo["file_bitrate"]
    songData["file_link"] = bitrateInfo["file_link"]

    allMusicData.append(songData)


if __name__ == "__main__":
    # print(allMusicInfo)
    for i in allMusicInfo:
        deal_ByName(i)

    try:
        r = redis.Redis(host = "119.23.168.219",port = 6380,decode_responses = True)

           # 数据库插入
        print(allMusicData)
        key = "w:carMusic:List"
        for x in allMusicData:
             strScore = x["song_id"]
             # print(type(strScore))
             valueList = r.zrangebyscore(key,strScore,strScore)
             # print(type(valueList))

             if len(valueList) > 0:
                 r.zremrangebyscore(key,strScore,strScore)
                 print("delete")

             jsonData = json.dumps(x,ensure_ascii=False)
             print(jsonData)
             r.zadd(key,jsonData,strScore)

        pass
    except Exception as err:
        print(err)
        pass











