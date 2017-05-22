#coding=utf-8
#qpy:kivy

import os
import re
import urllib2
import urllib
import thread
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.graphics import *

hosturl='http://m.biqudao.com'

class MyLayout(BoxLayout):
    #接收property
    novelname=ObjectProperty()
    noveldir=ObjectProperty()
    novelshow=ObjectProperty()
    noveldown=ObjectProperty()
    #这3个是判断是否查询完毕/是否停止线程/是否在下载的阀值
    chapterurl=False
    status=False
    download=False
    
    #查询函数，创建保存路径
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
            self.downdir=downdir+'/'+self.novelnametext+'.txt'
            if os.path.exists(self.downdir):
                self.noveldown.text=u'更新'
            else:
                self.noveldown.text=u'下载'
        except Exception,e:
            self.novelshow.text=u'查询失败，点多几次一定行\n%s\n'%e
            Logger.info(traceback.format_exc())
    
    #开始函数，结束按钮也在这里判断
    def start(self):
        if self.chapterurl:
            if self.noveldown.text != u'结束':
                dirs=self.noveldir.text.split('/')
                dirs=[i for i in dirs if i]
                #创建下载目录
                downdir='/'+'/'.join(dirs)
                if not os.path.exists(downdir):
                    os.makedirs(downdir)
                #全局downdir
                self.downdir=downdir+'/'+self.novelnametext+'.txt'
                self.novelshow.text=self.downdir+'\n'
                self.noveldown.text=u'结束'
                thread.start_new_thread(self.newthread,())
            else:
                self.stop()
        else:
            self.novelshow.text=u'请先查询再下载'  
    
    #结束函数
    def stop(self):
        if self.download:
            self.status=True
        else:
            self.novelshow.text=u'还没开始下载呢\n'

    #线程开始，不阻塞
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
            if os.path.exists(self.downdir):
                self.noveldown.text=u'更新'
            else:
                self.noveldown.text=u'下载'
    
    #爬虫函数
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
             	
        
    #查询函数
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
        self.novelnametext=titlename.decode('utf-8')
        author=re.findall('作者：</span>.*?<span>(.*?)</span>',r,re.S)[0].strip()
        author=author.replace('<em>','').replace('</em>','')
        updatetime=re.findall('更新时间：.*?<span class="result-game-item-info-tag-title">(.*?)</span>',r,re.S)[0].strip()
        lastchapter=re.findall('最新章节：.*?class="result-game-item-info-tag-item" target="_blank">(.*?)</a>',r,re.S)[0].strip()
        novelnotice='书名: %s\n作者: %s\n更新时间: %s\n最新章节: %s\n'%(titlename,author,updatetime,lastchapter)
        chapterurl=titleurl.replace('www','m')+'all.html'
        return novelnotice,chapterurl



class MainApp(App):
    pitures=['11.jpg','22.jpg','33.jpg','44.jpeg']
    if os.path.exists('/sdcard/noveling'):
        dirs=[i[0]+'/'+j for i in os.walk('/sdcard/noveling') for j in i[2]]
        pitures.extend(dirs)

    def build(self):
        return MyLayout()
    
    #记住书名和记住背景图的实现
    def on_start(self):
        ff=open('rename.txt')
        titlename=ff.read()
        ff.close()
        self.root.ids.novelname.text=titlename.decode('utf-8')
        self.root.ids.zt.on_press=self.stylecc

        fs=open('style.txt')
        ss=fs.read()
        ss=ss.decode('utf-8')
        fs.close()
        if not os.path.exists(ss):
            ss=self.pitures.pop(0)
            self.pitures.append(ss)
        with self.root.canvas.before:
            Rectangle(source=ss,pos=self.root.pos,size=self.root.size)

    #切换背景实现
    def stylecc(self):
        fs=open('style.txt')
        ss=fs.read()
        try:
            ss=ss.decode('utf-8')
        except:
            pass
        fs.close()

        if os.path.exists(ss):
            ols=self.pitures.pop(self.pitures.index(ss))
            self.pitures.append(ols)

        source=self.pitures.pop(0)
        #切换背景
        with self.root.canvas.before:
            Rectangle(source=source,pos=self.root.pos,size=self.root.size)
        self.pitures.append(source)

        fs=open('style.txt','w')
        try:
            fs.write(source.encode('utf-8'))
        except:
            fs.write(source)
        fs.close()
        










MainApp().run()
