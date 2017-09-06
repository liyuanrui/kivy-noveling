#coding=utf-8
#qpy:kivy

import os
import re
import urllib2
import urllib
import thread
import time
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.graphics import *
from kivymd.theming import ThemeManager
from kivy.core.text import LabelBase
from zt import Zhetian
LabelBase.register(name='Roboto',fn_regular='droid.ttf')

def encode(string):
    try:string=string.encode('utf-8')
    except:pass
    return string

def decode(string):
    try:string=string.decode('utf-8')
    except:pass
    return string

class MyLayout(BoxLayout):
    #接收property
    novelname=ObjectProperty()
    author=ObjectProperty()
    noveldir=ObjectProperty()
    novelshow=ObjectProperty()
    noveldown=ObjectProperty()
    #这3个是判断是否查询完毕/是否停止线程/是否在下载的阀值
    chapterurl=False
    status=False
    download=False
    z=Zhetian()

    #查询函数，创建保存路径
    def checknovel(self):
        try:
            self.novelshow.text=''
            name=encode(self.novelname.text)
            author=encode(self.author.text)


            nlist=self.z.novellist(author=author)
            nlist=[i for i in nlist if name == i[1]]
            for i in nlist:
                novelnotice='小说名: %s\n作者: %s\n最新章节:%s (%s)\n\n%s'%(i[1],i[2],i[5],i[6],i[4])
                self.chapterurl=i[0]

            self.novelshow.text=novelnotice

            with open('rename.txt','w') as rename:
                rename.write(encode(self.novelname.text)+'.'+encode(self.author.text))
            dirs=decode(self.noveldir.text).split('/')
            dirs=[i for i in dirs if i]
            #创建下载目录
            downdir=encode('/'+'/'.join(dirs))
            if not os.path.exists(downdir):
                os.makedirs(downdir)
            #全局downdir
            self.downdir=downdir+'/'+encode(self.novelname.text)+'.txt'
            if os.path.exists(self.downdir):
                self.noveldown.text='更新'
            else:
                self.noveldown.text='下载'
        except Exception as e:
            e=str(traceback.format_exc())
            self.novelshow.text=e if not 'local variable' in e else '源站未收录此书'
            Logger.info(traceback.format_exc())

    #开始函数，结束按钮也在这里判断
    def start(self):
        if self.chapterurl:
            if encode(self.noveldown.text) != '结束':
                dirs=decode(self.noveldir.text).split('/')
                dirs=[i for i in dirs if i]
                #创建下载目录
                downdir=encode('/'+'/'.join(dirs))
                if not os.path.exists(downdir):
                    os.makedirs(downdir)
                #全局downdir
                self.downdir=downdir+'/'+encode(self.novelname.text)+'.txt'
                self.novelshow.text=self.downdir+'\n'
                self.noveldown.text='结束'
                thread.start_new_thread(self.newthread,())
            else:
                self.stop()

        else:
            self.novelshow.text='请先查询再下载'

    #结束函数
    def stop(self):
        if self.download:
            self.status=True
        else:
            self.novelshow.text='还没开始下载呢\n'

    #线程开始，不阻塞
    def newthread(self):
        try:
            self.action()
        except Exception as e:
            exc=traceback.format_exc()
            warm ='发生错误，已保存进度，请重试\n%s\n\n'%exc +encode(self.novelshow.text)
            warm = warm.split('\n')[:51]
            warm = '\n'.join(warm)
            self.novelshow.text = warm
        finally:
            self.f.close()
            self.chapterurl=False
            self.download=False
            self.status=False
            if os.path.exists(self.downdir):
                self.noveldown.text='更新'
            else:
                self.noveldown.text='下载'

    #爬虫函数
    def action(self):
        self.download=True
        start=time.clock()
        #文本协调区------------
        if os.path.exists(self.downdir):
            with open(self.downdir) as rrr:
                rload=rrr.read()
            self.f=open(self.downdir,'a')
        else:
            self.f=open(self.downdir,'w')
            rload=''

        #获取章节列表区---------
        a=self.z.chapterlist(self.chapterurl)
        chapterlist=[]
        for i in a:
            if i[1] not in rload:
                chapterlist.append(i)
        end=time.clock()

        #获取正文区--------------
        for i in range(len(chapterlist)):
            if self.status:break
            url,chapter=chapterlist[i]
            while True:
                try:
                    body=self.z.body(url)
                    break
                except Exception as e:
                    #self.novelshow.text=str(traceback.format_exc())
                    self.novelshow.text = '网络异常，将在10秒后重试\n' + encode(self.novelshow.text)
                    time.sleep(10)

            #写入文本区--------------
            self.f.write('%s\n%s\n\n\n\n'%(encode(chapter),encode(body)))
            self.f.flush()
            warm = encode(self.novelshow.text)
            warm = warm.split('\n')[:51]
            try:warm.pop(0)
            except:pass
            warm = [j for j in warm if j]
            warm = '\n'.join(warm)
            warm = time.ctime()[11:19]+' '+chapter+'\n'+warm

            percent=float(i)/len(chapterlist)*100
            percent='下载进度 %.2f'%percent+'%'
            self.novelshow.text = percent+'\n\n'+warm
        if self.status:
            warm = '已结束，返回键退出\n\n'+encode(self.novelshow.text)
            warm = warm.split('\n')[:51]
            warm = '\n'.join(warm)
            self.novelshow.text = warm
        else:
            warm ='下载完成，enjoy!\n\n'+encode(self.novelshow.text)
            warm = warm.split('\n')[:51]
            warm = '\n'.join(warm)
            self.novelshow.text = warm





class MainApp(App):
    theme_cls=ThemeManager()

    def build(self):
        self.theme_cls.theme_style='Dark'
        return MyLayout()

    #记住书名的实现
    def on_start(self):
        ff=open('rename.txt')
        title=ff.read()
        name=title.split('.')[0]
        author=title.split('.')[-1]
        ff.close()
        self.root.ids.novelname.text=name
        self.root.ids.author.text=author


MainApp().run()
