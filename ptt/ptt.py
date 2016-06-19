#!/usr/bin/python

import re
import json
import codecs
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def loadJsonFile(filename):
    fp = codecs.open(filename, 'r', 'utf-8')
    content = json.loads(fp.read())
    fp.close()
    return content

def saveFile(filename, content):
    fp = codecs.open(filename, 'w+', 'utf-8')
    fp.write(content)
    fp.close()

def saveJsonFile(filename, content):
    fp = codecs.open(filename, 'w+', 'utf-8')
    fp.write(json.dumps(content))
    fp.close()

def initPage(config):
    payload = {
	'from': config['board'],
	'yes': 'yes'
    }
    res = rs.post('https://www.ptt.cc/ask/over18', verify = False, data = payload, headers = ua)
    res = rs.get('https://www.ptt.cc' + config['board'], verify = False, headers = ua)
    return BeautifulSoup(res.text, 'lxml')

def getPrevPage():
    global soup
    try:
        previousPage = soup.select('.action-bar .btn-group.btn-group-paging a.btn.wide')[1]['href']
    except:
	    # file path to save your error log
        saveFile("", soup.prettify())
        return False
    res = rs.get('https://www.ptt.cc' + previousPage, verify = False, headers = ua)
    return BeautifulSoup(res.text, 'lxml')

def getArticle():
    global soup
    global latest
    global current
    global articles
    p = re.compile('\.(\d{10,})\.')
    data = []
    for entry in soup.select('.r-ent'):
        obj = {}
        link = entry.select('.title a')
        if not link or not link[0]['href']: 
            continue
        obj['link'] = link[0]['href']
        m = p.search(obj['link'])
        if m :
            timestamp = int(m.group(1)) 
            current = timestamp if timestamp < current else current
            if timestamp <= articles['latest']:
                continue
        else:
            continue
        count = entry.select('.nrec .hl.f1, .nrec .hl.f3')
        if count and (count[0].text == '\u7206' or int(count[0].text) >= threshold):
            if timestamp > latest:
                latest = timestamp
            obj['count'] = count[0].text
            obj['title'] = entry.select('.title')[0].text
            obj['date'] = entry.select('.date')[0].text
            obj['author'] = entry.select('.author')[0].text
            data.append(obj)
    return data


ua = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36'
}

# add full path for loading ptt.config
configs = loadJsonFile("ptt.config")
rs = requests.session()

for config in configs:
    current = 99999999999
    output = {}
    datum = []
    threshold = config['threshold']
    articles = loadJsonFile(config['output'])
    latest = articles['latest']
    soup = initPage(config)
    soup = getPrevPage()
    while soup and current > articles['latest']:
        soup = getPrevPage()
        if soup:
            data = getArticle()
            if data:
                datum += data
    output['latest'] = latest
    output['data'] = datum
    saveJsonFile(config['output'], output)

