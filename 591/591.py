#!/usr/bin/python

import json
import codecs
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# better to use full path
configFile = "591.config"
outputFile = "items.json"
dbFile = "db.json"

def saveFile(filename, content):
    fp = codecs.open(filename, 'w+', 'utf-8')
    fp.write(content)
    fp.close()

def loadJsonFile(filename):
    fp = codecs.open(filename, 'r', 'utf-8')
    content = json.loads(fp.read())
    fp.close()
    return content

def getJsonURL(url):
    return json.loads(rs.get(url, verify = False).text)

def getItems(soup):
    global domain
    global db
    items = []
    for entry in soup.select('.shList .shInfo'):
        if entry.select('.pattern .isNew'):
            itemId = entry.select('.left')[0]['data-bind']
            if db.count(itemId) > 0:
                continue
            db.append(itemId)
            item = {}
            item['id'] = itemId
            item['img'] = entry.select('.left a img')[0]['src']
            item['title'] = entry.select('.right .title a')[0].text
            item['link'] = domain + entry.select('.right .title a')[0]['href']
            item['addr'] = entry.select('.right p:nth-of-type(2)')[0].text
            item['layout'] = entry.select('.right p:nth-of-type(3)')[0].text
            item['area'] = entry.select('.area')[0].text.strip(" \r\n\t")
            item['price'] = entry.select('.price')[0].text.strip("\n")
            items.append(item)
    return items

def setFirstRow(page):
    global firstRow
    firstRow = page * 20
    return firstRow

configs = loadJsonFile(configFile)
db = loadJsonFile(dbFile)

rs = requests.session()

output = {}
for index, config in configs.items():
    domain = config['domain']
    uri = config['uri']
    items = []
    for param in config['params']:
        del param['_comment']
        
        queryParams = ""
        for key, value in param.items():
            query = key + "=" + value + "&"
            queryParams += query
        
        link = domain + uri + queryParams[:-1]
        res = getJsonURL(link)
        count = int(res['count'])
        
        if not count or count <= 0 or not res['main']:
            continue

        mains = []
        mains.append(res['main'])

        page = 1
        firstRow = 0
        while setFirstRow(page) < count:
            newLink = link + "&firstRow=" + str(firstRow)
            res = getJsonURL(newLink)
            if res['main']:
                mains.append(res['main'])
            page += 1

        for main in mains:
            items += getItems(BeautifulSoup(main, 'lxml'))

    output[index] = items

saveFile(outputFile, json.dumps(output))
saveFile(dbFile, json.dumps(db))
