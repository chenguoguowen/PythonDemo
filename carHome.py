#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import  json
import time

AllBrandList = []
AllSeriesList = []
AllModelList = []

def deal_Func():
    nBrandID = 0
    for index in range(26):
        typeName = chr(ord('A') + index)
        url = 'http://www.autohome.com.cn/grade/carhtml/%s.html' % typeName
        req = requests.request(method='GET', url=url)
        html = req.content.decode('GBK')
        soup = BeautifulSoup(html, 'lxml')

        dls = soup.find_all('dl')

        for dl in dls:
            nBrandID += 1
            get_brand(dl,typeName,nBrandID)



def get_brand(dl,typeName,nBrandID):
    nSeriesID = 0
    dt = dl.find_all('dt')
    brandName = dt[0].get_text()
    img = 'https:' + dt[0].select('img')[0].attrs['src']

    brandDict = {}
    brandDict['root_id'] = nBrandID
    brandDict['root_name'] = brandName
    brandDict['logo'] = img
    brandDict['firstChar'] = typeName

    AllBrandList.append(brandDict)

    dd = dl.find('dd')
    lis = dd.find_all('li')
    for li in lis:
        if len(li) > 0:
            nSeriesID += 1
            get_Series(li,nBrandID,nSeriesID)



def get_Series(li,nBrandID,nSeriesID):
    seriesDict = {}
    seriesName = li.find_all('h4')[0].get_text()
    # print( seriesName)
    num = li.select('.js-che168link')[0].attrs['data-value']
    # print (num)
    seriesDict['root_id'] = nBrandID
    seriesDict['series_id'] = nSeriesID
    seriesDict['seriesName'] = seriesName
    AllSeriesList.append(seriesDict)

    # 嵌套查询车型(model)数据https://car.autohome.com.cn/duibi/ashx/specComparehandler.ashx?callback=jsonpCallback&type=1&seriesid=2745&format=json&_=1530078837399
    # 更换seriesid的值
    jsonurl = 'https://car.autohome.com.cn/duibi/ashx/specComparehandler.ashx?callback=jsonpCallback&type=1&seriesid=%s&format=json&_=1530078837399' % num
    get_Model(jsonurl,nSeriesID)


def get_Model(jsonurl,nSeriesID):
    jsonhtml = requests.get(jsonurl).text
    jsonhtml = jsonhtml.replace('jsonpCallback(', '')
    jsonhtml = jsonhtml.replace(')', '')

    jsondata = eval(jsonhtml)
    listdata = jsondata['List']

    modelId = 0
    for x in listdata:
        temp_list = x['List']
        for y in temp_list:
            seriesDict1 = {}
            modelId += 1
            seriesDict1['series_id'] = nSeriesID
            seriesDict1['model_id'] = modelId
            seriesDict1['modelName'] =  y['N']
            AllModelList.append(seriesDict1)



if __name__ == "__main__":
    AllBrandDict = {}
    AllSeriesDict = {}
    AllModelDict = {}

    deal_Func()
    AllBrandDict['AllBrand'] = AllBrandList
    allBrand = json.dumps(AllBrandDict)
    with open("Brand.json","w") as f1:
        f1.write(allBrand)

    AllSeriesDict['AllSeries'] = AllSeriesList
    allSeries = json.dumps(AllSeriesDict)
    with open("Series.json", "w") as f2:
        f2.write(allSeries)

    AllModelDict['AllModel'] = AllModelList
    allModel = json.dumps(AllModelDict)
    with open("modle.json", "w") as f3:
        f3.write(allModel)



