#!/usr/bin/python3
import requests
import time
import xlsxwriter
from bs4 import BeautifulSoup

url = "http://www.beimai.com"


# 返回一个字典{信息名:信息，信息名：信息}
def fetchInfo(name, urlInfo):
    info1 = {"商品名称": name, "单位": "*", "生产地": "*"}

    soupInfo = fetch(urlInfo)
    if  None == soupInfo:
        return None
    emPrice = soupInfo.find_all('em', attrs={'class': 'f30 fB'}, limit=1)
    price = "面议"
    for i in emPrice:
        price = i.get_text()

    div = soupInfo.find_all('div', attrs={'class': 'posR z10'}, limit=1)
    listApply = []
    for i in div:
        a = i.select("div > a")
        for j in a:
            carApply = j.get_text()
            listApply.append(carApply)

    div = soupInfo.find_all('div', attrs={'class': 'swiper-wrapper'}, limit=1)
    listPicture = []
    for i in div:
        img = i.select("div > img")
        for j in img:
            imglink = j.get('src')
            listPicture.append(imglink)

    info1["价格"] = price
    info1["适用车型"] = listApply
    info1["图片"] = listPicture
    return info1


# 返回字典{具体商品：{信息}}
def getInfo(linkDiction):
    # linkDiction = {小类：链接，小类：链接}
    listInfo = []
    for k in linkDiction:
        # print(k, linkDiction[k])
        info = fetchInfo(k, linkDiction[k])
        if None == info:
            continue
        listInfo.append(info)
    return listInfo


def getSecondUrsls(urlSecond):
    urlDictionTemp = {}
    urlDictionTemp.clear()
    soupSecond = fetch(urlSecond)
    if None == soupSecond:
        return None
    div = soupSecond.find_all('div', attrs={'class': 'bmnew-zsxmdiv-listc f_l'})
    for p in div:
        try:
            ps = p.select("p > a")
            for a in ps:
                name = a.get_text()
                name = "".join(name.split())
                link = a.attrs['href']
                # print(name, url + link)
                urlDictionTemp[name] = url + link
        except Exception:
            print("异常",urlSecond)
            print(p)
            continue
    return urlDictionTemp


def getFirstUrls(soup):
    urlDiction1 = {}
    urlDiction1.clear()
    aa = soup.find_all('ul', attrs={'class': 'newindex-pjdiv-topluldivul'})
    for ul in aa:
        lis = ul.select("li")
        for li in lis:
            a = li.select("a")[0]
            name = a.get_text()
            link = a.attrs['href']
            # print(name,link)
            urlDiction1[name] = url + link
    return urlDiction1


def fetch(url1):
    time.sleep(1)
    res = requests.get(url1)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup


# 生成excel文件
def generate_excel(name, expenses):
    name = name.replace("/","")
    name = name.replace("\\", "")
    workbook = xlsxwriter.Workbook('./info/' + name + '.xlsx')
    worksheet = workbook.add_worksheet()

    # 设定格式，等号左边格式名称自定义，字典中格式为指定选项
    # bold：加粗，num_format:数字格式
    bold_format = workbook.add_format({'bold': True})
    # money_format = workbook.add_format({'num_format': '$#,##0'})
    # date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})

    # 将二行二列设置宽度为15(从0开始)
    worksheet.set_column(1, 1, 15)

    # 用符号标记位置，例如：A列1行
    worksheet.write('A1', '商品名称', bold_format)
    worksheet.write('B1', '单位', bold_format)
    worksheet.write('C1', '图片', bold_format)
    worksheet.write('D1', '价格', bold_format)
    worksheet.write('E1', '适用车型', bold_format)
    worksheet.write('F1', '生产地', bold_format)

    row = 1
    for dic in expenses:
        col = 0
        # 使用write_string方法，指定数据格式写入数据
        worksheet.write_string(row, col, dic['商品名称'])
        worksheet.write_string(row, col + 1, dic['单位'])
        worksheet.write_string(row, col + 2, ";".join(dic['图片']))
        worksheet.write_string(row, col + 3, dic['价格'])
        worksheet.write_string(row, col + 4, ";".join(dic['适用车型']))
        worksheet.write_string(row, col + 5, dic['生产地'])
        row += 1
    workbook.close()


if __name__ == "__main__":
    print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    soup1 = fetch(url + "/quanchepeijian.html")

    # 一级字典{大类：链接}
    urlFirstDiction = getFirstUrls(soup1)
    # print(urlDiction)

    # !二级字典{大类：{小类：链接}}
    urlSecondDiction = {}
    for i in urlFirstDiction:
        SecondTemp = {}
        SecondTemp.clear()
        SecondTemp = getSecondUrsls(urlFirstDiction[i])
        if None == SecondTemp:
            continue
        #print(SecondTemp)
        urlSecondDiction[i] = SecondTemp

    # 二级字典{大类：[info]}
    infoDiction = {}
    for i in urlSecondDiction:
        infoList = getInfo(urlSecondDiction[i])
        infoDiction[i] = infoList

    print(infoDiction)
    # #写入Ecxel
    for i in infoDiction:
        generate_excel(i, infoDiction[i])
        print(i,infoDiction[i])
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))