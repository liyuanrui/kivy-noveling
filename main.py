#coding=utf-8
#qpy:kivy

import os
import re
import urllib2
import urllib
import thread
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

hosturl='http://m.biqudao.com'

class MyLayout(BoxLayout):
    novelname=ObjectProperty()
    noveldir=ObjectProperty()
    novelshow=ObjectProperty()
    noveldown=ObjectProperty()
    chapterurl=False
    status=False
    download=False
    
    def checknovel(self):
        try:
            self.novelshow.text=''
            novelnotice,self.chapterurl=self.searchtitle(self.novelname.text)
            self.novelshow.text=novelnotice
            with open('rename.txt','w') as rename:
                rename.write(self.novelname.text.encode('utf-8'))
            dirs=self.noveldir.text.split('/')
            dirs=[i for i in dirs if i]
            #创建下载目录
            downdir='/'+'/'.join(dirs)
            if not os.path.exists(downdir):
                os.makedirs(downdir)
            #全局downdir
            self.downdir=downdir+'/'+self.novelname.text+'.txt'
            if os.path.exists(self.downdir):
                self.noveldown.text=u'更新'
            else:
                self.noveldown.text=u'下载'
        except Exception,e:
            self.novelshow.text=u'查询失败，点多几次一定行\n%s\n'%e
            
    def start(self):
        if self.chapterurl:
            dirs=self.noveldir.text.split('/')
            dirs=[i for i in dirs if i]
            #创建下载目录
            downdir='/'+'/'.join(dirs)
            if not os.path.exists(downdir):
                os.makedirs(downdir)
            #全局downdir
            self.downdir=downdir+'/'+self.novelname.text+'.txt'
            self.novelshow.text=self.downdir+'\n'
            thread.start_new_thread(self.newthread,())
        else:
            self.novelshow.text=u'请先查询再下载'  
    
    def stop(self):
        if self.download:
            self.status=True
        else:
            self.novelshow.text=u'还没开始下载呢\n'

    
    def newthread(self):
        try:
            self.action()
        except Exception as e:
            warm = u'发生错误，已保存进度，请重试\n%s\n\n'%e +self.novelshow.text
            warm = warm.split('\n')[:51]
            warm = '\n'.join(warm)
            self.novelshow.text = warm
        finally:
            self.f.close()
            self.chapterurl=False
            self.download=False
            self.status=False
        
    def action(self):
        self.download=True
        #文本协调区------------
        if os.path.exists(self.downdir):
            with open(self.downdir) as rrr:
                rload=rrr.read()
            self.f=open(self.downdir,'a')
        else:
            self.f=open(self.downdir,'w')
            rload=''
            
        #获取章节列表区---------
        h=urllib2.urlopen(self.chapterurl)
        html=h.read()
        h.close()
        chapterlist=[]
        a=re.findall('<p> <a style="" href="(.*?)">(.*?)</a></p>',html)
        for i in a:
            if i[1] not in rload:
                chapterlist.append(i)
        
        #获取正文区--------------
        for i in chapterlist:
            if self.status:break
            url,chapter=i
            url=hosturl+'/'+url
            h=urllib2.urlopen(url)
            r=h.read()
            h.close()
            a=re.findall('</a></p>.*?\n<p ',r)[0]
            a2=a.replace('</a></p>','')
            a3=a2.replace('<p ','')
            a4=a3.replace('<br/>','\n')
            a5=a4.replace('&nbsp;',' ')
             
            #写入文本区--------------
            self.	f.write('%s\n%s\n\n\n\n'%(chapter,a5))
            self.f.flush()
            warm = chapter.decode('utf-8')+'\n'+self.novelshow.text
            warm = warm.split('\n')[:51]
            warm = '\n'.join(warm)
            self.novelshow.text = warm
        if self.status:
            warm = u'已结束，返回键退出\n\n'+self.novelshow.text
            warm = warm.split('\n')[:51]
            warm = '\n'.join(warm)
            self.novelshow.text = warm
        else:
            warm =u'下载完成，enjoy!\n\n'+self.novelshow.text
            warm = warm.split('\n')[:51]
            warm = '\n'.join(warm)
            self.novelshow.text = warm
             	
        
        
    def searchtitle(self,title):
        try:
            url='http://zhannei.baidu.com/cse/search?s=3654077655350271938&q=%s'%urllib.quote(title.encode('utf-8'))
        except:
            url='http://zhannei.baidu.com/cse/search?s=3654077655350271938&q=%s'%urllib.quote(title)
        h=urllib2.urlopen(url)
        r=h.read()
        h.close()
        a=re.findall('<a cpos="title" href="(.*?)" title="(.*?)" class="result-game-item-title-link" target="_blank">',r)[0]
        titleurl=a[0]
        titlename=a[1]
        #全局书名
        self.novelname.text=titlename
        author=re.findall('作者：</span>.*?<span>(.*?)</span>',r,re.S)[0].strip()
        author=author.replace('<em>','').replace('</em>','')
        updatetime=re.findall('更新时间：.*?<span class="result-game-item-info-tag-title">(.*?)</span>',r,re.S)[0].strip()
        lastchapter=re.findall('最新章节：.*?class="result-game-item-info-tag-item" target="_blank">(.*?)</a>',r,re.S)[0].strip()
        novelnotice='书名: %s\n作者: %s\n更新时间: %s\n最新章节: %s\n'%(titlename,author,updatetime,lastchapter)
        chapterurl=titleurl.replace('www','m')+'all.html'
        return novelnotice,chapterurl

#class Down(object):
    #def __init__()


class MainApp(App):
    def build(self):
        return MyLayout()
    def on_start(self):
        ff=open('rename.txt')
        titlename=ff.read()
        ff.close()
        self.root.ids.novelname.text=titlename.decode('utf-8')

MainApp().run()
