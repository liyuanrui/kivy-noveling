#coding=utf-8

from urllib2 import urlopen
from urllib import quote
from contextlib import closing
import re
import random

def encode(string):
    try:string=string.encode('utf-8')
    except:pass
    return string

def decode(string):
    try:string=string.decode('utf-8')
    except:pass
    return string

class Zhetian:
    def __init__(self):
        self.hosturl='http://www.zhetian.org'
        self.nameurl='http://www.zhetian.org/search.html?searchtype=novelname&searchkey='
        self.authorurl='http://www.zhetian.org/search.html?searchtype=author&searchkey='
    def novellist(self,name=None,author=None):
        '''搜索结果列表'''
        if name:url=self.nameurl+quote(encode(name))
        else:url=self.authorurl+quote(encode(author))
        with closing(urlopen(url,timeout=20)) as h:
            r=h.read()
        msg=re.findall('<div class="pt-ll-r">.*?a href="(.*?)" class="novelname" title="(.*?)">.*?title="(.*?) 作品列表".*?分类：<a href=.*?title=".*?">(.*?)</a>.*?<p class="intro">(.*?)</p>.*?<p class="last">.*?target="_blank">(.*?)</a>\((.*?)\).*?<div class="clear"></div>',r,re.S)
        if msg:
            results=[]
            for i in range(len(msg)):
                href=msg[i][0];title=msg[i][1];author=msg[i][2];cage=msg[i][3];desc=msg[i][4].strip();last=msg[i][5];update=msg[i][6]
                results.append([href,title,author,cage,desc,last,update])
            return results
        else:return []
    def chapterlist(self,chapterurl):
        '''章节列表'''
        url=self.hosturl+chapterurl
        with closing(urlopen(url,timeout=20)) as h:
            r=h.read()
        msg=re.findall('<li><a href="(.*?)" title=".*?" target="_blank">(.*?)</a></li>',r)
        msg=[i for i in msg if chapterurl in i[0]]
        return msg
    def body(self,bodyurl):
        '''正文'''
        url=self.hosturl+bodyurl
        #print url
        while True:
            with closing(urlopen(url,timeout=20)) as h:
                r=h.read()
            msg=re.findall(u"\$\.get\('(.*?)',{},",r)
            with closing(urlopen(self.hosturl+msg[0],timeout=20)) as h:
                rr=h.read()
            msg=eval(rr)
            body=msg['info']
            body=body.replace('<br\/>','\n')
            if len(decode(body))<=33:
                all=re.findall('换源阅读.*?<ul class="chapterlist">.*?<a href=".*?" target="_self".*?</article>',r,re.S)[0]
                link=re.findall('<a href="(.*?)"',all)
                bodyurl=link[random.randrange(len(link))]
                url=self.hosturl+bodyurl
            else:
                break

        return body
