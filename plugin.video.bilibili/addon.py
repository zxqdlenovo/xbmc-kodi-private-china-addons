#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import hashlib
import HTMLParser
import json
import random
import re
import string
import sys
import time
import urllib2

import requests
#import xbmcgui
from bs4 import BeautifulSoup
from xbmcswift2 import Plugin, xbmcgui, xbmc, xbmcaddon,xbmcplugin
import danmuku
import os

class BPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def onAVStarted(self):
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('错误提示', 'arcurl')


def random_sentence(size):
    char_lists = string.ascii_lowercase + string.digits
    return ''.join(random.choice(char_lists) for _ in range(size))

def unescape(string):
    string = urllib2.unquote(string).decode('utf8')
    quoted = HTMLParser.HTMLParser().unescape(string).encode('utf-8')
    #转成中文
    return re.sub(r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: unichr(int(m.group(1), 16)), quoted)


plugin = Plugin()

# uuid = xbmcplugin.getSetting(int(sys.argv[1]),'baipiao')
# if uuid == 'true':
#     dialog = xbmcgui.Dialog()
#     dialog.textviewer('错误提示', str(uuid))


#超过10000换算
def zh(num):
    if int(num) >= 100000000:
        p = round(float(num)/float(100000000), 1)
        p = str(p) + '亿'
    else:
        if int(num) >= 10000:
            p = round(float(num)/float(10000), 1)
            p = str(p) + '万'
        else:
            p = str(num)
    return p

#白嫖计算
def bp(li):
    li = sorted(li)
    minnum = li[0]
    v = 0
    for index in range(len(li)):
        v += li[index] - minnum
    v += minnum
    return v

    
his = plugin.get_storage('his')
cache = plugin.get_storage('cache')

headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'}
mheaders = {'user-agent' : 'Mozilla/5.0 (Linux; Android 10; Z832 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36'}

def chushihua(key,default):
    if key in cache:
        switch = cache[key]
    else:
        cache[key] = default
        switch = cache[key]
    if switch == 1:
        value = '开'
    else:
        value = '关'
    return value

#仿b站随机输出主播正在xx
def rd_live_gz():
    gz = ['思考人生','抠脚丫','俯卧撑热身','卖萌','打滚','换女装','觅食','海扁小电视','成为魔法少女','修电锯','跳广播体操','吸猫','渡劫中','学习','梳妆打扮','撩妹','逛漫展','拔腿毛','逛b站']
    return '主播正在' + gz[random.randint(0,(len(gz)-1))] + '...'

#b站二级目录tid反查一级目录名字，没有api，只能自己造轮子
def two_one(tid):
    #动画区
    douga = [1,24,25,47,86,27]
    #番剧区
    anime = [51,152]
    #音乐区
    music = [3,28,31,30,194,59,193,29,130]
    #国创区
    guochuang = [153,168,169,195,170]
    #舞蹈区
    dance = [129,20,198,199,200,154,156]
    #游戏区
    game = [4,17,171,172,65,173,121,136,19]
    #科技区
    technology = [36,124,122,39,96,98,176]
    #数码区
    digital = [188,95,189,190,191]
    #生活区
    life = [160,138,21,76,75,161,162,163,174]
    #鬼畜区
    kichiku = [119,22,26,126,127]
    #时尚区
    fashion = [155,157,158,164,159,192]
    #广告区
    ad = [165,166]
    #娱乐区
    ent = [5,71,137,131]
    #影视区
    cinephile = [181,182,183,85,184]
    re = ''
    if int(tid) in douga:
        re = '动画'
    if int(tid) in anime:
        re = '番剧'
    if int(tid) in music:
        re = '音乐'
    if int(tid) in guochuang:
        re = '国创'
    if int(tid) in dance:
        re = '舞蹈'
    if int(tid) in game:
        re = '游戏'
    if int(tid) in technology:
        re = '科技'
    if int(tid) in digital:
        re = '数码'
    if int(tid) in life:
        re = '生活'
    if int(tid) in kichiku:
        re = '鬼畜'
    if int(tid) in fashion:
        re = '时尚'
    if int(tid) in ad:
        re = '广告'
    if int(tid) in ent:
        re = '娱乐'
    if int(tid) in cinephile:
        re = '影视'
    if re == '':
        re = '未知'
    return re

#显示等级颜色
def level_color(level):
    if int(level) == 0:
        lev = '  [COLOR grey]Lv.' + str(level) +'[/COLOR]'
    if int(level) == 1:
        lev = '  [COLOR grey]Lv.' + str(level) +'[/COLOR]'
    if int(level) == 2:
        lev = '  [COLOR green]Lv.' + str(level) +'[/COLOR]'
    if int(level) == 3:
        lev = '  [COLOR blue]Lv.' + str(level) +'[/COLOR]'
    if int(level) == 4:
        lev = '  [COLOR yellow]Lv.' + str(level) +'[/COLOR]'
    if int(level) == 5:
        lev = '  [COLOR orange]Lv.' + str(level) +'[/COLOR]'
    if int(level) == 6:
        lev = '  [COLOR red]Lv.' + str(level) +'[/COLOR]'
    return lev
def sessdata(mode=''):
    vipstatus = xbmcplugin.getSetting(int(sys.argv[1]),'vipstatus')
    if mode == 'vip' and vipstatus == 'true':
        sessdata = xbmcplugin.getSetting(int(sys.argv[1]),'vipsessdata')
    else:
        sessdata = xbmcplugin.getSetting(int(sys.argv[1]),'sessdata')
    sessdata = 'SESSDATA=' + sessdata
    # dialog = xbmcgui.Dialog()
    # dialog.textviewer('错误提示', str(sessdata))
    # if 'sessdata' in cache:
    #     sessdata = 'SESSDATA=' + cache['sessdata']
    # else:
    #     sessdata = ''
    return sessdata

@plugin.cached(TTL=1)
def get_up_roomold(uid):
    r = requests.get('https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid='+str(uid), headers=headers)
    r.encoding = 'UTF-8'
    return r.text

@plugin.cached(TTL=60)
def get_up_baseinfo(uid):
    r = requests.get('https://api.bilibili.com/x/space/acc/info?mid='+str(uid)+'&jsonp=jsonp', headers=headers)
    r.encoding = 'UTF-8'
    return r.text

@plugin.cached(TTL=60)
def get_upinfo(uid):
    
    j = json.loads(get_up_baseinfo(uid))
    u = j['data']
    #up数据
    di = up_allnum(uid)
    #最新数据
    new = up_sort_vid(uid,'')
    #热门数据
    click = up_sort_vid(uid,'click')
    #热门数据
    stow = up_sort_vid(uid,'stow')
    text = ''
    #大会员判断
    vip = u''
    if u['vip']['status'] == 1:
        if u['vip']['type'] == 2:
            vip += u'[COLOR pink][年度大会员][/COLOR]'
        else:
            vip += u'[COLOR pink][大会员][/COLOR]'
    #性别判断
    if u['sex'] == u'男':
        sex = u'[COLOR blue][♂][/COLOR]'
    else:
        if u['sex'] == u'女':
            sex = u'[COLOR pink][♀][/COLOR]'
        else:
            sex = u'?'
    text += u'UP主:' + u['name'] + u'  性别:'  + sex + u'  '+ level_color(u['level']) + vip +'\n'
    

    if u['official']['role'] != 0:
        text += u['official']['title'] +'\n'
    if u['sign'] == '':
        sign = u'这个人很懒，什么都没有写'
    else:
        sign = u['sign']
    text += u'个性签名:' + sign + '\n'
    text += u'生日:' + u['birthday'] + '\n'


    text += u'----------'*5 + u'up主大数据' + u'----------'*5 + '\n\n'
    if u['official']['role'] != 0:
        text += u'「'+u['name']+ u'」是经过认证的「'+u['official']['title']+ u'」。' +'\n'
    else:
        text += u'「'+u['name']+ u'」是一个不太出名的up主。' +'\n'
    tlist = new['list']['tlist']
    try:
        tt = list(tlist.keys())
        ttt = []
        for index in range(len(tt)):
            ttt.append(tlist[tt[index]])
        hotp = sorted(ttt,key=lambda x:x['count'],reverse=True)
        text += u'TA是主要活跃在「'+ hotp[0]['name'] + u'区」的UP主，在该分区共投稿「'+ str(hotp[0]['count']) + u' 个稿件」'+'\n'

        if two_one(click['list']['vlist'][0]['typeid']) != hotp[0]['name'].encode('utf-8'):
            text += u'然而TA在「' + two_one(click['list']['vlist'][0]['typeid']).decode('utf-8') + u'」拥有着表现最好的作品'+'\n'
        text += u'代表作是《 ' + click['list']['vlist'][0]['title'] + u'》。'+'\n'

        jinqi = []
        for index in range(len(new['list']['vlist'])):
            jinqi.append(two_one(new['list']['vlist'][index]['typeid']))
        jinqi2 =[]
        for index in range(len(jinqi)):
            if jinqi[index] != max(jinqi, key=jinqi.count):
                jinqi2.append(jinqi[index])
        if jinqi2 != []:
            if jinqi2.count(max(jinqi2, key=jinqi2.count)) < jinqi.count(max(jinqi, key=jinqi.count)):
                text += u'近期，TA的投稿仍然大多在「'+max(jinqi, key=jinqi.count).decode('utf-8') + u'区」。'  + '\n\n'
            else:
                text += u'虽然TA的投稿仍然大多在「'+max(jinqi, key=jinqi.count).decode('utf-8')+u'」,不过TA有向「'+max(jinqi2, key=jinqi2.count).decode('utf-8')+u'」转型的可能性。'  + '\n\n'
        else:
            text += u'近期，TA的投稿1000%在「'+max(jinqi, key=jinqi.count).decode('utf-8') + u'区」。'  + '\n\n'
    except AttributeError:
        text += u'没有更多关于TA的情报信息了\n\n'
    text += u'----------'*5 + u'up主最新数据' + u'----------'*5 + '\n\n'
    text += u'粉丝总数:' + zh(di['follower']).decode('utf-8') + u'     播放总数:' + zh(di['archive']).decode('utf-8') + u'     获赞总数:' + zh(di['likes']).decode('utf-8') + u'     专栏阅读:' + zh(di['article']).decode('utf-8') + '\n\n'
    
    try:
        text += u'----------'*5 + u'up主投稿分区' + u'----------'*5 + '\n\n'
        for index in range(len(hotp)):
            co = u'|'*int((float(hotp[index]['count'])/float(new['page']['count']))*100)
            if len(hotp[index]['name']) == 2:
                name = hotp[index]['name'] +u'区'
            else:
                name = hotp[index]['name']
            text += name + u':' + str(co) + u' ' + str(round((float(hotp[index]['count'])/float(new['page']['count']))*100,2)) + u'% - ' +str(hotp[index]['count']) + u'个投稿\n'
    except UnboundLocalError:
        text += u'没有更多关于TA的情报信息了'
    return text

#最新投稿 ‘’ 播放最多 click 收藏最多stow
@plugin.cached(TTL=10)
def up_sort_vid(uid,sort):
    if sort == '':
        so = ''
    else:
        so = '&order=' +sort
    r = requests.get('https://api.bilibili.com/x/space/arc/search?mid='+uid+'&pn=1&ps=25'+so+'&jsonp=jsonp', headers=headers)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    return j['data']


#up播放数据
@plugin.cached(TTL=10)
def up_allnum(uid):
    di = {}
    r = requests.get('https://api.bilibili.com/x/relation/stat?vmid='+uid+'&jsonp=jsonp', headers=headers)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #关注
    di['following'] = j['data']['following']
    #粉丝
    di['follower'] = j['data']['follower']
    
    r = requests.get('https://api.bilibili.com/x/space/upstat?mid='+uid+'&jsonp=jsonp', headers=headers)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #播放量
    di['archive'] = j['data']['archive']['view']
    #专栏
    di['article'] = j['data']['article']['view']
    #获赞数
    di['likes'] = j['data']['likes']

    return di
    
@plugin.cached(TTL=10)
def get_search(keyword,page):
    serachUrl = 'https://api.bilibili.com/x/web-interface/search/all/v2?keyword=' + keyword + '&page=' + str(page)

    r = requests.get(serachUrl, headers=headers)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #视频
    k = j['data']['result'][8]['data']
    #番剧
    bgm = j['data']['result'][3]['data']
    #影视
    mov = j['data']['result'][4]['data']
    videos = []
    for index in range(len(bgm)):
        surl = 'https://www.bilibili.com/bangumi/play/ss' + str(bgm[index]['season_id'])
        title = '[COLOR pink][' + bgm[index]['season_type_name'] + '] ' + bgm[index]['title'] + '[/COLOR]'
        pic = bgm[index]['cover']
        #清除b站api数据污染
        title = title.replace('<em class="keyword">', '')
        title = title.replace('</em>', '')
        
        videoitem = {}
        videoitem['name'] = title
        videoitem['href'] = surl
        videoitem['thumb'] = 'http:'+pic
        videos.append(videoitem)
    for index in range(len(mov)):
        surl = 'https://www.bilibili.com/bangumi/play/ss' + str(mov[index]['season_id'])
        title = '[COLOR pink][' + mov[index]['season_type_name'] + '] ' +  mov[index]['title'] + '[/COLOR]'
        pic = mov[index]['cover']
        #清除b站api数据污染
        title = title.replace('<em class="keyword">', '')
        title = title.replace('</em>', '')
        
        videoitem = {}
        videoitem['name'] = title
        videoitem['href'] = surl
        videoitem['thumb'] = 'http:'+pic
        videos.append(videoitem)
    #k = k.encode('utf-8')
    #dialog = xbmcgui.Dialog()
    #ok = dialog.ok('错误提示', arcurl)

    for index in range(len(k)):
        arcurl = 'http://www.bilibili.com/video/' + k[index]['bvid']
        title = '[' + k[index]['typename'] + ']' + k[index]['title']
        pic = k[index]['pic']
        #duration = k[index]['duration']
        #清除b站api数据污染
        title = title.replace('<em class="keyword">', '')
        title = title.replace('</em>', '')
        
        videoitem = {}
        videoitem['name'] = title
        videoitem['href'] = arcurl
        videoitem['thumb'] = 'http://'+pic
        videoitem['genre'] = '喜剧片'
        videos.append(videoitem)
    if int(j['data']['numResults']) == 1000:
        numResults = str(j['data']['numResults']) + '+'
    else:
        numResults = str(j['data']['numResults'])
    dialog = xbmcgui.Dialog()
    dialog.notification('当前'+ str(page) + '/' + str(j['data']['numPages']) + '页', '总共'+ numResults + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return videos

@plugin.cached(TTL=10)
def get_vidsearch(keyword,page):
    serachUrl = 'https://api.bilibili.com/x/web-interface/search/type?context=&search_type=video&order=&keyword=' + keyword + '&page=' + str(page) +'&duration=&category_id=&tids_1=&tids_2=&__refresh__=true&_extra=&highlight=1&single_column=0&jsonp=jsonp'
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://search.bilibili.com/all?keyword=' + keyword
    }
    r = requests.get(serachUrl, headers=apiheaders)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #
    videos = []
    try:
        bgm = j['data']['result']
    
        #k = k.encode('utf-8')
        #dialog = xbmcgui.Dialog()
        #ok = dialog.ok('错误提示', arcurl)
        for index in range(len(bgm)):
            

            vurl = 'https://www.bilibili.com/video/' + str(bgm[index]['bvid'])
            title = bgm[index]['title']
            pic = bgm[index]['pic']
            #清除b站api数据污染
            title = title.replace('<em class="keyword">', '')
            title = title.replace('</em>', '')
        
            videoitem = {}
            videoitem['name'] = title
            videoitem['href'] = vurl
            videoitem['thumb'] = 'http:'+pic
            videos.append(videoitem)
        if int(j['data']['numResults']) == 1000:
            numResults = str(j['data']['numResults']) + '+'
        else:
            numResults = str(j['data']['numResults'])
        dialog = xbmcgui.Dialog()
        dialog.notification('当前'+ str(page) + '/' + str(j['data']['numPages']) + '页', '总共'+ numResults + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    except KeyError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '搜索结果为空', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return videos

@plugin.cached(TTL=10)
def get_bgsearch(keyword,page):
    serachUrl = 'https://api.bilibili.com/x/web-interface/search/type?context=&search_type=media_bangumi&order=&keyword=' + keyword + '&page=' + str(page) +'&category_id=&__refresh__=true&_extra=&highlight=1&single_column=1&jsonp=jsonp'
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://search.bilibili.com/all?keyword=' + keyword
    }
    r = requests.get(serachUrl, headers=apiheaders)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #
    videos = []
    try:
        bgm = j['data']['result']
    
        #k = k.encode('utf-8')
        #dialog = xbmcgui.Dialog()
        #ok = dialog.ok('错误提示', arcurl)
        for index in range(len(bgm)):
            if bgm[index]['ep_size'] != 0:
                title = bgm[index]['title'] + ' [更新到第'.decode('utf-8') + str(bgm[index]['ep_size']) + '集]'.decode('utf-8')
            else:
                title = bgm[index]['title'] + ' [未开播]'.decode('utf-8')

            surl = 'https://www.bilibili.com/bangumi/play/ss' + str(bgm[index]['season_id'])
         
            pic = bgm[index]['cover']
            #清除b站api数据污染
            title = title.replace('<em class="keyword">', '')
            title = title.replace('</em>', '')
        
            videoitem = {}
            videoitem['name'] = title
            videoitem['href'] = surl
            videoitem['thumb'] = 'http:'+pic
            videos.append(videoitem)
        if int(j['data']['numResults']) == 1000:
            numResults = str(j['data']['numResults']) + '+'
        else:
            numResults = str(j['data']['numResults'])
        dialog = xbmcgui.Dialog()
        dialog.notification('当前'+ str(page) + '/' + str(j['data']['numPages']) + '页', '总共'+ numResults + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    except KeyError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '搜索结果为空', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return videos

@plugin.cached(TTL=10)
def get_movsearch(keyword,page):
    
    serachUrl = 'https://api.bilibili.com/x/web-interface/search/type?context=&search_type=media_ft&order=&keyword=' + keyword + '&page=' + str(page) +'&category_id=&__refresh__=true&_extra=&highlight=1&single_column=0&jsonp=jsonp'
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://search.bilibili.com/all?keyword=' + keyword
    }
    r = requests.get(serachUrl, headers=apiheaders)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #
    videos = []
    try:
        bgm = j['data']['result']
    
        #k = k.encode('utf-8')
        #dialog = xbmcgui.Dialog()
        #ok = dialog.ok('错误提示', arcurl)
        for index in range(len(bgm)):
            if bgm[index]['ep_size'] != 0:
                title = bgm[index]['title'] + ' [更新到第'.decode('utf-8') + str(bgm[index]['ep_size']) + '集]'.decode('utf-8')
            else:
                title = bgm[index]['title'] + ' [未开播]'.decode('utf-8')

            surl = 'https://www.bilibili.com/bangumi/play/ss' + str(bgm[index]['season_id'])
        
            pic = bgm[index]['cover']
            #清除b站api数据污染
            title = title.replace('<em class="keyword">', '')
            title = title.replace('</em>', '')
        
            videoitem = {}
            videoitem['name'] = title
            videoitem['href'] = surl
            videoitem['thumb'] = 'http:'+pic
            videos.append(videoitem)
        if int(j['data']['numResults']) == 1000:
            numResults = str(j['data']['numResults']) + '+'
        else:
            numResults = str(j['data']['numResults'])
        dialog = xbmcgui.Dialog()
        dialog.notification('当前'+ str(page) + '/' + str(j['data']['numPages']) + '页', '总共'+ numResults + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    except KeyError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '搜索结果为空', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return videos

@plugin.cached(TTL=10)
def get_livesearch(keyword,page):
    serachUrl = 'https://api.bilibili.com/x/web-interface/search/type?context=&keyword=' + keyword + '&page=' + str(page) +'&order=&category_id=&duration=&user_type=&order_sort=&tids_1=&tids_2=&search_type=live&changing=id&cover_type=user_cover&__refresh__=true&__reload__=false&_extra=&highlight=1&single_column=0&jsonp=jsonp'
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://search.bilibili.com/all?keyword=' + keyword
    }
    r = requests.get(serachUrl, headers=apiheaders)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #
    videos = []
    try:
        bgm = j['data']['result']['live_room']
    
        #k = k.encode('utf-8')
        #dialog = xbmcgui.Dialog()
        #ok = dialog.ok('错误提示', arcurl)
        for index in range(len(bgm)):
            title = bgm[index]['title']
            if int(bgm[index]['live_status']) == 1:
                title += u' [COLOR pink][LIVE][/COLOR]'
            title += u' [在线' +  zh(bgm[index]['online']).decode('utf-8') + u']'
            pic = bgm[index]['cover']
            #清除b站api数据污染
            title = title.replace('<em class="keyword">', '')
            title = title.replace('</em>', '')
        
            videoitem = {}
            videoitem['name'] = title
            videoitem['href'] = bgm[index]['roomid']
            videoitem['thumb'] = 'http:'+pic
            videos.append(videoitem)
        if int(j['data']['numResults']) == 1000:
            numResults = str(j['data']['numResults']) + '+'
        else:
            numResults = str(j['data']['numResults'])
        dialog = xbmcgui.Dialog()
        dialog.notification('当前'+ str(page) + '/' + str(j['data']['numPages']) + '页', '总共'+ numResults + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    except KeyError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '搜索结果为空', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return videos

@plugin.cached(TTL=10)
def get_upsearch(keyword,page):
    
    serachUrl = 'https://api.bilibili.com/x/web-interface/search/type?context=&search_type=bili_user&order=&keyword=' + keyword + '&page=' + str(page) +'&category_id=&user_type=&order_sort=&changing=mid&__refresh__=true&_extra=&highlight=1&single_column=0&jsonp=jsonp'
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://search.bilibili.com/all?keyword=' + keyword
    }
    r = requests.get(serachUrl, headers=apiheaders)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #
    videos = []
    try:
        bgm = j['data']['result']
    
        #k = k.encode('utf-8')
        #dialog = xbmcgui.Dialog()
        #ok = dialog.ok('错误提示', arcurl)
        for index in range(len(bgm)):
            title = bgm[index]['uname'].encode('utf-8') 
            pic = bgm[index]['upic']
            #清除b站api数据污染
            title = title.replace('<em class="keyword">', '')
            title = title.replace('</em>', '')
            if int(bgm[index]['gender']) == 1:
                title += ' [COLOR blue][♂][/COLOR]'
            if int(bgm[index]['gender']) == 2:
                title += ' [COLOR pink][♀][/COLOR]'
            title += ' ' + level_color(bgm[index]['level'])
            if int(bgm[index]['is_live']) == 1:
                title += ' [COLOR pink][LIVE][/COLOR]'
            videoitem = {}
            videoitem['name'] = title  + '  - ' + zh(bgm[index]['videos']) + '投稿 · ' + zh(bgm[index]['fans']) + '粉丝'
            videoitem['href'] = bgm[index]['mid']
            videoitem['thumb'] = 'http:'+pic
            videos.append(videoitem)
        if int(j['data']['numResults']) == 1000:
            numResults = str(j['data']['numResults']) + '+'
        else:
            numResults = str(j['data']['numResults'])
        dialog = xbmcgui.Dialog()
        dialog.notification('当前'+ str(page) + '/' + str(j['data']['numPages']) + '页', '总共'+ numResults + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    except KeyError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '搜索结果为空', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return videos

@plugin.cached(TTL=10)
def get_up(uid,page):
    r = requests.get('https://api.bilibili.com/x/space/arc/search?mid='+uid+'&ps=30&tid=0&pn='+page+'&keyword=&order=pubdate&jsonp=jsonp', headers=headers)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    #
    videos = []
    vlist = j['data']['list']['vlist']
    for index in range(len(vlist)):
        videoitem = {}
        videoitem['name'] = vlist[index]['title']
        videoitem['href'] = 'https://www.bilibili.com/video/' + vlist[index]['bvid']
        videoitem['thumb'] = 'http:'+vlist[index]['pic']
        videos.append(videoitem)
    dialog = xbmcgui.Dialog()
    dialog.notification('当前'+ str(page) + '/' + str(int(int(j['data']['page']['count']) / 30) + 1) + '页', '总共'+ str(j['data']['page']['count']) + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return videos
    
@plugin.cached(TTL=60)
def get_bangumiinfo(url):
    r = requests.get(url,headers=headers)
    rtext = r.text
    str1 = rtext.find('window.__INITIAL_STATE__=')
    str2 = rtext.find(';(function(){var s')
    vjson = rtext[str1+25:str2]
    j = json.loads(vjson)
    r1 = requests.get('https://www.bilibili.com/bangumi/media/md' + str(j['mediaInfo']['id']),headers=headers)
    rt = r1.text
    str1 = rt.find('window.__INITIAL_STATE__=')
    str2 = rt.find(';(function(){var s')
    mjson = rt[str1+25:str2]
    j2 = json.loads(mjson)


    stat = j['mediaInfo']['stat']
    mp4info = {}
    jianjie =  zh(stat['views']) + '播放 · ' + zh(stat['danmakus']) + '弹幕 · ' + zh(stat['reply']) +'评论\n'
    jianjie += str(j['mediaInfo']['rating']['score']) + '分('+ str(j['mediaInfo']['rating']['count']) + '人评) · ' + zh(stat['coins']) + '投币 · ' + zh(stat['favorites'])  + '追番\n'
    
    #bpnum = j2['mediaInfo']['stat']['danmakus'] + j2['mediaInfo']['stat']['series_follow'] + stat['reply'] +j['mediaInfo']['rating']['count'] + stat['coins']
    #jianjie += '白嫖率：' + str(100-round((float(bpnum)/float(j2['mediaInfo']['stat']['views']))*100,2)) +'% \n'

    jianjie += '--------------------------\n'
    jianjie += j2['mediaInfo']['publish']['release_date_show'].encode('utf-8') + '\n'
    jianjie += j2['mediaInfo']['publish']['time_length_show'].encode('utf-8') +'\n'
    jianjie += '--------------------------\n'
    try:
        mp4info['plot'] = jianjie  + j['mediaInfo']['evaluate'].encode('utf-8')
    except AttributeError:
        mp4info['plot'] = jianjie
    mp4info['title'] = j['mediaInfo']['title']
    mp4info['img'] = 'http:' + j['mediaInfo']['cover']
    mp4info['rating'] = j['mediaInfo']['rating']['score']
    mp4info['userrating'] = j['mediaInfo']['rating']['score']
    mp4info['aired'] = j2['mediaInfo']['publish']['pub_date']

    areas = []
    for index in range(len(j2['mediaInfo']['areas'])):
        areas.append(j2['mediaInfo']['areas'][index]['name'])
    mp4info['country'] = areas

    staff = j2['mediaInfo']['staff']
    staff1 = staff.split('\n')
    # dialog = xbmcgui.Dialog()
    # dialog.textviewer('错误提示', str(staff.encode('utf-8')))
    st12 = []
    st13 = []
    for index in range(len(staff1)):
        
        if staff1[index].find('编剧'.decode('utf-8')) and staff1[index].find('设计'.decode('utf-8')) != -1:
            st10 = staff1[index].split(':'.decode('utf-8'))
            if st10[1].find(',') != -1:
                st11 = st10[1].split(',')
            else:
                st11 = [st10[1]]
            #print(st11)
            for index in range(len(st11)):
                st12.append(st11[index])
            #dialog = xbmcgui.Dialog()
            #ok = dialog.ok('错误提示', str(st12))
            mp4info['writer'] = st12
        if staff1[index].find('导演'.decode('utf-8')) and staff1[index].find('监督'.decode('utf-8')) != -1:
            
            st10 = staff1[index].split(':'.decode('utf-8'))
            # dialog = xbmcgui.Dialog()
            # dialog.textviewer('错误提示', str(st10[1].encode('utf-8')))
            if st10[1].find(',') != -1:
                st11 = st10[1].split(',')
            else:
                st11 = [st10[1]]
            
            for index in range(len(st11)):
                st13.append(st11[index])
            mp4info['director'] = st13
            

    cast = []
    cast1 = j2['mediaInfo']['actors']
    cast1 = cast1.split('\n')
    for index in range(len(cast1)):
        if cast1[index].find('：'.decode('utf-8')) != -1:
            cast2 = cast1[index].split('：'.decode('utf-8'))
            cast.append((cast2[0],cast2[1]))
        else:
            cast.append(cast1[index])
    mp4info['cast'] = cast

    tag = []
    for index in range(len(j2['mediaInfo']['styles'])):
        tag.append(j2['mediaInfo']['styles'][index]['name'])
    mp4info['genre'] = tag

    mp4info['mediatype'] = 'video'
    mp4info['reply'] = zh(stat['reply'])
    return mp4info

@plugin.cached(TTL=60)
def get_mp4info(url):
    r = requests.get(url,headers=headers)
    r.encoding = 'utf-8'
    rtext = r.text
    str1 = rtext.find('window.__INITIAL_STATE__=')
    str2 = rtext.find(';(function(){var s')
    vjson = rtext[str1+25:str2]
    j = json.loads(vjson)
    uptime = j['videoData']['ctime']
    #转换成localtime
    time_local = time.localtime(uptime)
    #转换成新的时间格式(2016-05-05 20:28:54)
    uptime = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
    data = time.strftime("%Y-%m-%d",time_local)
    
    sr = requests.get('https://api.bilibili.com/x/web-interface/archive/stat?aid='+str(j['aid']),headers=headers)
    sj = json.loads(sr.text)
    stat = sj['data']
    mp4info = {}
    jianjie =  zh(stat['view']) + '播放 · ' + zh(stat['danmaku']) + '弹幕 · ' + zh(stat['reply']) +'评论\n'
    jianjie += zh(stat['like']) + '赞 · ' + zh(stat['coin']) + '投币 · ' + zh(stat['favorite'])  + '收藏\n'
    mp4info['reply'] = zh(stat['reply'])
    if stat['now_rank'] != 0:
        jianjie += '今日全站日排行第' + str(stat['now_rank']) + '名\n'
    if stat['his_rank'] != 0:
        jianjie += '最高全站日排行第' + str(stat['his_rank']) + '名\n'
    if stat['copyright'] == 1:
        jianjie += '[COLOR red]未经作者许可，禁止转载[/COLOR]\n'
    # if 'bq' in cache:
    #     if cache['bq'] == 1:
    baipiaosetting = xbmcplugin.getSetting(int(sys.argv[1]),'baipiao')
    if baipiaosetting == 'true':
        bpnum = bp([stat['like'],stat['coin'],stat['favorite']])
        jianjie += '白嫖率：' + str(100-round(((float(bpnum) + float(stat['danmaku']) + float(stat['reply']) + float(stat['share']))/float(stat['view']))*100,2)) +'% \n'
    jianjie += '--------------------------\n'
    jianjie += 'av' + str(j['aid']) +' · ' + j['bvid'].encode('utf-8') +'\n'
    jianjie += '发布时间：' + uptime +'\n'
    jianjie += '--------------------------\n'
    try:
        mp4info['plot'] = jianjie  + j['videoData']['desc'].encode('utf-8')
    except AttributeError:
        mp4info['plot'] = jianjie

    mp4info['title'] = j['videoData']['title']
    mp4info['img'] = j['videoData']['pic']

    tag = []
    for index in range(len(j['tags'])):
        tag.append(j['tags'][index]['tag_name'])
    mp4info['genre'] = tag
    mp4info['tag'] = tag

    cast = []
    if j['staffData'] != []:
        for index in range(len(j['staffData'])):
            up = j['staffData'][index]['name'] + '[' +j['staffData'][index]['title'] +']'
            fan = zh(j['staffData'][index]['follower']) + '粉丝'
            cast.append((up,fan))
    else:
        up = j['upData']['name']
        fan = zh(j['upData']['fans']) + '粉丝'
        cast.append((up,fan))
    mp4info['cast'] = cast
    
    mp4info['dateadded'] = uptime
    mp4info['aired'] = data
    mp4info['duration'] = j['videoData']['duration']

    mp4info['mediatype'] = 'video'

    #传递uid
    mp4info['upname'] = j['videoData']['owner']['name']
    mp4info['uid'] = j['videoData']['owner']['mid']
    mp4info['face'] = j['videoData']['owner']['face']
    return mp4info

#评论区
@plugin.cached(TTL=60)
def get_comm(url,sort):
    if re.match('https://',url) == None:
        if re.match('http://',url) != None:
            url = 'https://'+url[7:]
        else:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('错误提示', '非法url')

    ifbangumiurl = re.match('https://www.bilibili.com/bangumi/play/ep',url)
    ifvideourl = re.match('https://www.bilibili.com/video/',url)
    if ifbangumiurl or ifvideourl != None:
        if ifbangumiurl != None:
            epid = re.search(r'ep[0-9]+', url)
            epid = epid.group()
            epid = epid[2:]
            r = requests.get(url,headers=headers)
        
            rtext = r.text
            str1 = rtext.find('window.__INITIAL_STATE__=')
            str2 = rtext.find(';(function(){var s')
            vjson = rtext[str1+25:str2]
            j = json.loads(vjson)
            elist = j['epList']
            aid = ''
            for index in range(len(elist)):
                if int(elist[index]['id']) == int(epid):
                    aid = elist[index]['aid']
            if aid == '':
                slist = j['sections']
                if slist != []:
                    for index in range(len(slist)):
                        ##
                        sslist = slist[index]['epList']
                        for i in range(len(sslist)):
                            if int(sslist[i]['id']) == int(epid):
                                aid = sslist[index]['aid']
            if aid == '':
                dialog = xbmcgui.Dialog()
                #dialog.textviewer('tt',epid)
        if ifvideourl != None:
            bvid = re.search(r'BV[a-zA-Z0-9]+', url)
            bvurl = 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid.group()
            r = requests.get(bvurl,headers=headers)
            j = json.loads(r.text)
            aid = j['data']['aid']
            mid = j['data']['owner']['mid']
    
    #apiurl = 'http://api.bilibili.com/x/reply?type=1&oid='+str(aid)+'&sort=' + sort
    apiurl = 'https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type=1&oid='+str(aid)+'&sort=' + sort
    apiheaders = {'user-agent' : 'Mozilla/5.0 (Linux; Android 10; Z832 Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Mobile Safari/537.36','referer':'https://www.bilibili.com/video/BV1Ze411W7EL'}

    r = requests.get(apiurl,headers=apiheaders)
    j = json.loads(r.text)
    rep = j['data']['replies']
    text = ''
    for index in range(len(rep)):
        text += '-----'*12 +'\n'
        #时间处理
        ctime = int(rep[index]['ctime'])
        #转换成localtime
        time_local = time.localtime(ctime)
        #转换成新的时间格式(2016-05-05 20:28:54)
        ctime = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
        #判断大会员
        if rep[index]['member']['vip']['vipType'] == 2:
            #是大会员，加上粉色名字
            text += '[COLOR pink]' + rep[index]['member']['uname'].encode('utf-8') + '[/COLOR]'
        else:
            text += rep[index]['member']['uname'].encode('utf-8')
        #加上等级后缀
        text += level_color(rep[index]['member']['level_info']['current_level'])
        #判断是否up主
        if ifvideourl != None:
            if int(mid) == int(rep[index]['member']['mid']):
                text += ' [COLOR pink][UP主][/COLOR]' 
        text += '\n'

        text += rep[index]['content']['message'].encode('utf-8') +'\n'
        text += str(ctime) + ' · ' + str(rep[index]['like']) + '赞 · 共' + str(rep[index]['count']) +'条回复\n'
        rrep = rep[index]['replies']
        text += '-----'*12 +'\n\n'
        if rrep:
            for i in range(len(rrep)):
                #时间处理
                ctime = int(rrep[i]['ctime'])
                #转换成localtime
                time_local = time.localtime(ctime)
                #转换成新的时间格式(2016-05-05 20:28:54)
                ctime = time.strftime("%Y-%m-%d %H:%M:%S",time_local)

                if rrep[i]['member']['vip']['vipType'] == 2:
                    #大会员
                    text += ' '*5 + '[COLOR pink]' +  rrep[i]['member']['uname'].encode('utf-8') + '[/COLOR]'
                else:
                    text += ' '*5 + rrep[i]['member']['uname'].encode('utf-8')
                #加上等级后缀
                text += level_color(rrep[i]['member']['level_info']['current_level'])
                #判断是否up主
                if ifvideourl != None:
                    if int(mid) == int(rep[index]['member']['mid']):
                        text += ' [COLOR pink][UP主][/COLOR]' 
                text += '\n'
                text += ' '*5 + rrep[i]['content']['message'].encode('utf-8') +'\n'
                text += ' '*5 + str(ctime) + ' · ' + str(rrep[i]['like']) + '赞 · 共' + str(rrep[i]['count']) +'条回复\n'
                if len(rrep)-1 != i:
                    text += ' '*5 + '-----'*10 +'\n'
  
    return text

@plugin.cached(TTL=60)
def get_bangumijson(url):
    cutep = url.find('y/ep')
    epnum = url[cutep+4:]
    epnum = re.sub(r'\D','',epnum)
    apiurl = 'https://api.bilibili.com/pgc/player/web/playurl/html5?ep_id='
    rec = requests.get(apiurl+epnum,headers=mheaders)
    #rec.encoding = 'utf-8'
    rectext = rec.text
    rectext = rectext.encode('utf-8')
    j = json.loads(rec.text)
    return j



@plugin.cached(TTL=10)
def get_api1(url,quality):
    if re.search(r'[Bb]{1}[Vv]{1}[a-zA-Z0-9]+', url):
        bvid = re.search(r'[Bb]{1}[Vv]{1}[a-zA-Z0-9]+', url)
        vurl = 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid.group()
    if re.search('[aA]{1}[vV]{1}[0-9]+', url):
        aid = re.search(r'[aA]{1}[vV]{1}[0-9]+', url)
        aid = aid.group()
        aid = aid[2:]
        vurl = 'https://api.bilibili.com/x/web-interface/view?aid='+aid
    
    if '?p=' in url:
        # 单独下载分P视频中的一集
        p = int(re.search(r'\?p=(\d+)',url).group(1)) -1
    else:
        p = 0
    r = requests.get(vurl,headers=headers)
    j = json.loads(r.text)
    cid = j['data']['pages'][int(p)]['cid']

    if xbmcplugin.getSetting(int(sys.argv[1]),'damakustatus') == 'true':
        dpath = xbmcplugin.getSetting(int(sys.argv[1]),'damakufolder')
        danmuku.Danmuku(cid,dpath)
    #print(cid)


    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    tmp = params + sec
    tmp = tmp.encode('utf-8')
    chksum = hashlib.md5(bytes(tmp)).hexdigest()
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    apiheaders = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
    }
    # print(url_api)
    html = requests.get(url_api, headers=apiheaders).json()
    # print(json.dumps(html))
    video_list = []
    for i in html['durl']:
        video_list.append(i['url'])
    # print(video_list)
    return video_list

@plugin.cached(TTL=10)
def get_api2(url):
    mp4 = ''
    if re.match('https://',url) == None:
        if re.match('http://',url) != None:
            url = 'https://'+url[7:]
        else:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('错误提示', '非法url')
    ifvideourl = re.match('https://www.bilibili.com/video/',url)
    if ifvideourl != None:
        bvid = ''
        aid = ''
        if re.search(r'[Bb]{1}[Vv]{1}[a-zA-Z0-9]+', url):
            bvid = re.search(r'[Bb]{1}[Vv]{1}[a-zA-Z0-9]+', url)
            bvid = bvid.group()
            vurl = 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid
        if re.search('[aA]{1}[vV]{1}[0-9]+', url):
            aid = re.search(r'[aA]{1}[vV]{1}[0-9]+', url)
            aid = aid.group()
            aid = aid[2:]
            vurl = 'https://api.bilibili.com/x/web-interface/view?aid='+aid
        r = requests.get(vurl,headers=headers)
        j = json.loads(r.text)
        aid = j['data']['aid']
        if '?p=' in url:
            # 单独下载分P视频中的一集
            p = int(re.search(r'\?p=(\d+)',url).group(1)) -1
        else:
            p = 0
        cid = j['data']['pages'][p]['cid']
        if xbmcplugin.getSetting(int(sys.argv[1]),'damakustatus') == 'true':
            dpath = xbmcplugin.getSetting(int(sys.argv[1]),'damakufolder')
            danmuku.Danmuku(cid,dpath)

        apiurl = 'https://www.xbeibeix.com/api/bilibiliapi.php?url=https://www.bilibili.com/&aid='+str(aid)+'&cid=' + str(cid)
        r = requests.get(apiurl,headers=headers)
        j = json.loads(r.text)
        if str(j['url']) != 'null':
            mp4 = j['url']
            dialog = xbmcgui.Dialog()
            dialog.textviewer('错误提示', str(mp4))
        else:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('错误提示', '视频不存在')
    else:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('错误提示', '不支持的url格式')
    return mp4

@plugin.cached(TTL=10)
def get_api3(url, quality):
    if re.match('https://',url) == None:
        if re.match('http://',url) != None:
            url = 'https://'+url[7:]
        else:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('错误提示', '非法url')

    ifbangumiurl = re.match('https://www.bilibili.com/bangumi/play/ep',url)
    ifvideourl = re.match('https://www.bilibili.com/video/',url)
    if ifbangumiurl or ifvideourl != None:
        if ifbangumiurl != None:
            epid = re.search(r'ep[0-9]+', url)
            epid = epid.group()
            epid = epid[2:]
            r = requests.get(url,headers=headers)
        
            rtext = r.text
            str1 = rtext.find('window.__INITIAL_STATE__=')
            str2 = rtext.find(';(function(){var s')
            vjson = rtext[str1+25:str2]
            j = json.loads(vjson)
            elist = j['epList']
            bvid = ''
            cid = ''
            for index in range(len(elist)):
                if int(elist[index]['id']) == int(epid):
                    bvid = elist[index]['bvid']
                    cid = elist[index]['cid']
            if bvid == '' or cid == '':
                slist = j['sections']
                if slist != []:
                    for index in range(len(slist)):
                        ##
                        sslist = slist[index]['epList']
                        for i in range(len(sslist)):
                            if int(sslist[i]['id']) == int(epid):
                                bvid = sslist[index]['bvid']
                                cid = sslist[index]['cid']
            if bvid == '' or cid == '':
                dialog = xbmcgui.Dialog()
                #dialog.textviewer('tt',epid)
            else:
                if xbmcplugin.getSetting(int(sys.argv[1]),'damakustatus') == 'true':
                    dpath = xbmcplugin.getSetting(int(sys.argv[1]),'damakufolder')
                    danmuku.Danmuku(cid,dpath)

        if ifvideourl != None:
            bvid = ''
            aid = ''
            if re.search(r'[Bb]{1}[Vv]{1}[a-zA-Z0-9]+', url):
                bvid = re.search(r'[Bb]{1}[Vv]{1}[a-zA-Z0-9]+', url)
                bvid = bvid.group()
                vurl = 'https://api.bilibili.com/x/web-interface/view?bvid='+bvid
            if re.search('[aA]{1}[vV]{1}[0-9]+', url):
                aid = re.search(r'[aA]{1}[vV]{1}[0-9]+', url)
                aid = aid.group()
                aid = aid[2:]
                vurl = 'https://api.bilibili.com/x/web-interface/view?aid='+aid
            r = requests.get(vurl,headers=headers)
            j = json.loads(r.text)
            #bvid = j['data']['pages'][0]['bvid']
            if '?p=' in url:
                # 单独下载分P视频中的一集
                p = int(re.search(r'\?p=(\d+)',url).group(1)) -1
            else:
                p = 0
            cid = j['data']['pages'][p]['cid']
            if xbmcplugin.getSetting(int(sys.argv[1]),'damakustatus') == 'true':
                dpath = xbmcplugin.getSetting(int(sys.argv[1]),'damakufolder')
                danmuku.Danmuku(cid,dpath)
    
    if bvid != '':
        url_api = 'https://api.bilibili.com/x/player/playurl?cid={}&bvid={}&qn={}'.format(cid, bvid, quality)
    else:
        url_api = 'https://api.bilibili.com/x/player/playurl?cid={}&aid={}&qn={}'.format(cid, aid, quality)
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Cookie': sessdata(mode='vip'), # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
        'Host': 'api.bilibili.com'
    }
    html = requests.get(url_api, headers=apiheaders).json()
    video_list = []
    #dialog = xbmcgui.Dialog()
    #dialog.textviewer('评论区',str(html['data']['durl']))
    if 'data' in html:
        for i in html['data']['durl']:
            video_list.append(i['url'])
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok('提示','无法解析视频')
    
    return video_list

@plugin.cached(TTL=10)
def get_api4(url,quality):
    epid = re.search(r'ep[0-9]+', url)
    epid = epid.group()
    epid = epid[2:]
    r = requests.get(url,headers=headers)
        
    rtext = r.text
    str1 = rtext.find('window.__INITIAL_STATE__=')
    str2 = rtext.find(';(function(){var s')
    vjson = rtext[str1+25:str2]
    j = json.loads(vjson)
    elist = j['epList']
    bvid = ''
    cid = ''
    for index in range(len(elist)):
        if int(elist[index]['id']) == int(epid):
            bvid = elist[index]['bvid']
            cid = elist[index]['cid']
    if bvid == '' or cid == '':
        slist = j['sections']
        if slist != []:
            for index in range(len(slist)):
                ##
                sslist = slist[index]['epList']
                for i in range(len(sslist)):
                    if int(sslist[i]['id']) == int(epid):
                        bvid = sslist[index]['bvid']
                        cid = sslist[index]['cid']
    if bvid == '' or cid == '':
        dialog = xbmcgui.Dialog()
        #dialog.textviewer('tt',epid)
    else:
        if xbmcplugin.getSetting(int(sys.argv[1]),'damakustatus') == 'true':
            dpath = xbmcplugin.getSetting(int(sys.argv[1]),'damakufolder')
            danmuku.Danmuku(cid,dpath)
    #hk9ho2af5hdw20wewf4ahqovwp79kq2z
    
    #https://www.biliplus.com/BPplayurl.php?cid=181007115&bvid=BV1fK4y1r7sT&qn=80&module=bangumi&otype=json
    url_api = 'https://www.biliplus.com/BPplayurl.php?cid={}&qn={}&module=bangumi&otype=json&bvid={}'.format(cid,quality,bvid)
    
    r = requests.get(url_api, headers=headers)
    html = json.loads(r.text)
    #video_list = []
    
    # if 'durl' in html:
    #     videolist = []
    #     for i in html['durl']:
    #         videolist.append(i['url'])
    #     #video_list = video_list[0]
    # if 'dash' in html:
    #     videolist = {}
    #     videolist['video'] = html['dash']['video'][0]['base_url']
    #     videolist['audio'] = html['dash']['audio'][0]['base_url']
    #     #video_list = video_list[0]
    #dialog = xbmcgui.Dialog()
    #dialog.textviewer('评论区',str(html))
    video_list = []
    if 'durl' in html:
        for i in range(len(html['durl'])):
            video_list.append(html['durl'][i]['url'])
        #video_list = video_list[0]
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok('提示','无法解析视频')
    #dialog = xbmcgui.Dialog()
    #dialog.textviewer('评论区',str(video_list))
    return video_list

@plugin.cached(TTL=10)
def get_api5(url,quality,api):
    epid = re.search(r'ep[0-9]+', url)
    epid = epid.group()
    epid = epid[2:]
    r = requests.get(url,headers=headers)
        
    rtext = r.text
    str1 = rtext.find('window.__INITIAL_STATE__=')
    str2 = rtext.find(';(function(){var s')
    vjson = rtext[str1+25:str2]
    j = json.loads(vjson)
    elist = j['epList']
    bvid = ''
    cid = ''
    for index in range(len(elist)):
        if int(elist[index]['id']) == int(epid):
            bvid = elist[index]['bvid']
            cid = elist[index]['cid']
    if bvid == '' or cid == '':
        slist = j['sections']
        if slist != []:
            for index in range(len(slist)):
                ##
                sslist = slist[index]['epList']
                for i in range(len(sslist)):
                    if int(sslist[i]['id']) == int(epid):
                        bvid = sslist[index]['bvid']
                        cid = sslist[index]['cid']
    if bvid == '' or cid == '':
        dialog = xbmcgui.Dialog()
        #dialog.textviewer('tt',epid)
    else:
        if xbmcplugin.getSetting(int(sys.argv[1]),'damakustatus') == 'true':
            dpath = xbmcplugin.getSetting(int(sys.argv[1]),'damakufolder')
            danmuku.Danmuku(cid,dpath)
    if int(api) == 1:
        apihead = 'https://bilibili-tw-api.kghost.info/'
    if int(api) == 2:
        apihead = 'https://bilibili-hk-api.kghost.info/'
    url_api = apihead + 'x/player/playurl?cid={}&bvid={}&qn={}'.format(cid, bvid, quality)
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        #'Cookie': sessdata, # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
        #'Host': 'api.bilibili.com'
    }
    html = requests.get(url_api, headers=apiheaders).json()
    video_list = []
    #dialog = xbmcgui.Dialog()
    #dialog.textviewer('评论区',str(html))
    if html['data']:
        for i in html['data']['durl']:
            video_list.append(i['url'])
        video_list = video_list[0]
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok('提示','无法解析视频')
    return video_list

@plugin.cached(TTL=10)
def get_live(page):
    videos = []
    r = requests.get('https://api.live.bilibili.com/room/v1/room/get_user_recommend?page=' +str(page), headers=headers)
    r.encoding = 'UTF-8'
    
    j = json.loads(r.text)
    llist = j['data']
    for index in range(len(llist)):
        videoitem = {}
        videoitem['name'] = llist[index]['title']
        videoitem['href'] = llist[index]['roomid']
        videoitem['thumb'] = llist[index]['user_cover']
        videos.append(videoitem)
    return videos

@plugin.cached(TTL=10)
def get_livemore(url,page):
    videos = []
    r = requests.get(url + '&page=' +str(page), headers=headers)
    r.encoding = 'UTF-8'
    
    j = json.loads(r.text)
    llist = j['data']['list']
    for index in range(len(llist)):
        videoitem = {}
        videoitem['name'] = '[' + llist[index]['area_name'] + ']' +llist[index]['title']
        videoitem['href'] = llist[index]['roomid']
        videoitem['thumb'] = llist[index]['cover']
        videos.append(videoitem)
    return videos

@plugin.cached(TTL=1)
def get_roominfo(id):
    flvdict = {}
    r = requests.get('https://api.live.bilibili.com/room/v1/Room/get_info?id='+str(id), headers=headers)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    
    
    ro = j['data']

    soup = BeautifulSoup(ro['description'], "html5lib")

    flvdict['title'] = ro['title']
    flvdict['img'] = ro['user_cover']

    jianjie = '房间号:' + str(ro['room_id']) + '\n'
    if ro['short_id'] != 0:
        jianjie += '短房间号:' + str(ro['short_id'])+ '\n'
    jianjie += '在线:' + zh(ro['online']) + '\n'
    
    if ro['live_status'] == 1:
        flvdict['status'] = '开播'
        jianjie += '开播时间:' + ro['live_time'].encode('utf-8') + '\n'
    else:
        flvdict['status'] = '未开播'
    jianjie += '--------------------------\n'
    jianjie += (soup.text).encode('utf-8')
    flvdict['plot'] = jianjie
    #time = 
    time = re.search('[\d]{4}-[\d]{2}-[\d]{2}',ro['live_time']).group()
    flvdict['aired'] = time
    genre = [ro['parent_area_name'],ro['area_name']]
    tag = ro['tags'].split(',')

    flvdict['genre'] = genre + tag
    flvdict['tag'] = genre + tag


    
    j = json.loads(get_up_baseinfo(ro['uid']))
    #up主 cast
    fan = zh(ro['attention']) + '粉丝'
    #fan = fan.decode('utf-8')
    flvdict['cast'] = [(j['data']['name'],fan)]

    flvdict['mediatype'] = 'video'
    return flvdict

@plugin.cached(TTL=1)
def get_roommp4(id):
    
    r = requests.get('https://api.live.bilibili.com/xlive/web-room/v1/index/getRoomPlayInfo?room_id='+str(id)+'&play_url=1&mask=0&qn=0&platform=web', headers=headers)
    r.encoding = 'UTF-8'
    j = json.loads(r.text)
    vlist = []
    try:
        flv = j['data']['play_url']['durl']
        for index in range(len(flv)):
            vlist.append(flv[index]['url'])
    except TypeError:
        dialog = xbmcgui.Dialog()
        dialog.notification('获取直播源地址失败', '可能房间号不存在未开播', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return vlist

def get_categories():
    return [{'name':'首页','link':'https://www.bilibili.com/ranking/all/0/0/1'},
            {'name':'[COLOR pink]新番[/COLOR]','link':'https://www.bilibili.com/ranking/bangumi/13/0/3'},
            {'name':'[COLOR pink]国产动画[/COLOR]','link':'https://www.bilibili.com/ranking/bangumi/167/0/3'},
            {'name':'动画','link':'https://www.bilibili.com/ranking/all/1/0/1'},
            {'name':'国创相关','link':'https://www.bilibili.com/ranking/all/168/0/1'},
            {'name':'音乐','link':'https://www.bilibili.com/ranking/all/3/0/1'},
            {'name':'舞蹈','link':'https://www.bilibili.com/ranking/all/129/0/1'},
            {'name':'游戏','link':'https://www.bilibili.com/ranking/all/4/0/1'},
            {'name':'知识','link':'https://www.bilibili.com/ranking/all/36/0/1'},
            {'name':'数码','link':'https://www.bilibili.com/ranking/all/188/0/1'},
            {'name':'生活','link':'https://www.bilibili.com/ranking/all/160/0/1'},
            {'name':'鬼畜','link':'https://www.bilibili.com/ranking/all/119/0/1'},
            {'name':'时尚','link':'https://www.bilibili.com/ranking/all/155/0/1'},
            {'name':'娱乐','link':'https://www.bilibili.com/ranking/all/5/0/1'},
            {'name':'影视','link':'https://www.bilibili.com/ranking/all/181/0/1'},
            {'name':'新人','link':'https://www.bilibili.com/ranking/rookie/0/0/3'},
            {'name':'[COLOR pink]纪录片[/COLOR]','link':'https://www.bilibili.com/ranking/cinema/177/0/3'},
            {'name':'[COLOR pink]电影[/COLOR]','link':'https://www.bilibili.com/ranking/cinema/23/0/3'},
            {'name':'[COLOR pink]电视剧[/COLOR]','link':'https://www.bilibili.com/ranking/cinema/11/0/3'}]

#@plugin.cached(TTL=10)
def get_videos(url):
#爬视频列表的
    r = requests.get(url, headers=headers)
    r.encoding = 'UTF-8'
    soup = BeautifulSoup(r.text, "html.parser")
    videos = []

    # videoelements = soup.find_all('li',class_='rank-item')
    rectext = r.text
    cutjson =str(rectext.encode('utf-8'))
    str1 = cutjson.find('window.__INITIAL_STATE__=')
    str2 = cutjson.find(';(function(){var s;')
    rankinfojson = cutjson[str1+25:str2]
    j = json.loads(rankinfojson)
    
    for index in range(len(j['rankList'])):
        if 'badge' in j['rankList'][index]:
            videoitem = {}
            videoitem['name'] = j['rankList'][index]['title'].encode('utf-8')
            videoitem['href'] = 'https://www.bilibili.com/bangumi/play/ss' + str(j['rankList'][index]['season_id'])
            videoitem['thumb'] = j['rankList'][index]['pic'].encode('utf-8')
            videoitem['info'] = {'plot':''}
            if j['rankList'][index]['badge'].encode('utf-8') != '':
                videoitem['info']['plot'] += '[COLOR pink]' + j['rankList'][index]['badge'].encode('utf-8') + '[/COLOR] · '
            if 'copyright' in j:
                if j['rankList'][index]['copyright'].encode('utf-8') == 'dujia':
                    videoitem['info']['plot'] += '[COLOR pink]Bilibili独占[/COLOR] · '
            videoitem['info']['plot'] += j['rankList'][index]['new_ep']['index_show'].encode('utf-8') + '\n'
            videoitem['info']['plot'] += zh(j['rankList'][index]['stat']['view']) + '播放 · ' + zh(j['rankList'][index]['stat']['danmaku']) + '弹幕 · ' + zh(j['rankList'][index]['stat']['follow']) + '追番'
            # videoitem['info']['plot'] += '\nAV' + j['rankList'][index]['aid'].encode('utf-8') + ' · BV' + j['rankList'][index]['bvid'].encode('utf-8')
            videoitem['mediatype'] = 'video'
            videos.append(videoitem)
        else:
            videoitem = {}
            videoitem['name'] = j['rankList'][index]['title'].encode('utf-8')
            videoitem['href'] = 'https://www.bilibili.com/video/' + j['rankList'][index]['bvid'].encode('utf-8')
            videoitem['thumb'] = j['rankList'][index]['pic'].encode('utf-8')
            videoitem['info'] = {'plot':'UP主: ' + j['rankList'][index]['author'].encode('utf-8') + '\n'}
            videoitem['info']['plot'] += zh(j['rankList'][index]['play']) + '播放 · ' + zh(j['rankList'][index]['video_review']) + '弹幕 · ' + zh(j['rankList'][index]['coins']) + '硬币'
            videoitem['info']['plot'] += '\nAV' + j['rankList'][index]['aid'].encode('utf-8') + ' · BV' + j['rankList'][index]['bvid'].encode('utf-8')
            videoitem['mediatype'] = 'video'
            videos.append(videoitem)
            
    return videos

    # if videoelements is None:
    #     dialog = xbmcgui.Dialog()
    #     ok = dialog.ok('错误提示', '没有播放源')
    # else:
    #     num = 0
    #     for videoelement in videoelements:
    #         videoitem = {}
    #         videoitem['name'] = videoelement.find('img')['alt']
    #         videoitem['href'] = videoelement.find('a')['href']
    #         videoitem['thumb'] = j['rankList'][num]['pic'].encode('utf-8')
    #         videos.append(videoitem)
    #         num = num+1
    #     return videos

@plugin.cached(TTL=10)
def get_sources(url):
    sources = []
    if re.match('https://',url) == None:
      if re.match('http://',url) != None:
        url = 'https://'+url[7:]
      else:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('错误提示', '非法url')

    ifbangumiurl = re.match('https://www.bilibili.com/bangumi/play/ss',url)
    ifvideourl = re.match('https://www.bilibili.com/video/',url)
    if ifbangumiurl or ifvideourl != None:
      if ifbangumiurl != None:
    
        r = requests.get(url,headers=headers)
        
        rtext = r.text
        str1 = rtext.find('window.__INITIAL_STATE__=')
        str2 = rtext.find(';(function(){var s')
        vjson = rtext[str1+25:str2]
        j = json.loads(vjson)
        #缓存标题，方便后续判断
        cache['bgtitle'] = j['h1Title']
        elist = j['epList']
        for index in range(len(elist)):
            videosource = {}
            if elist[index]['badge'] != '':
                if elist[index]['longTitle'] == '':
                    ename = '正片 : ' + str(elist[index]['title'].encode('utf-8')) + ' - ' + elist[index]['longTitle'].encode('utf-8') + ' [COLOR pink][' + elist[index]['badge'].encode('utf-8') + '][/COLOR]'
                else:
                    ename = '正片 : ' + str(elist[index]['title'].encode('utf-8')) + ' [COLOR pink][' + elist[index]['badge'].encode('utf-8') + '][/COLOR]'
            else:
                if elist[index]['longTitle'] != '':
                    ename = '正片 : ' + str(elist[index]['title'].encode('utf-8')) + ' - ' + elist[index]['longTitle'].encode('utf-8')
                else:
                    ename = '正片 : ' + str(elist[index]['title'].encode('utf-8'))
            href = 'https://www.bilibili.com/bangumi/play/ep' + str(elist[index]['id']) + '?https://www.bilibili.com/video/' + elist[index]['bvid']
            videosource['name'] = ename
            videosource['href'] = plugin.url_for('play',name=ename,url=href)
            sources.append(videosource)
        slist = j['sections']
        if slist != []:
            for index in range(len(slist)):
                title = slist[index]['title'].encode('utf-8')
                sslist = slist[index]['epList']
                for index in range(len(sslist)):
                    videosource = {}
                    if sslist[index]['epStatus'] == 13:
                        if sslist[index]['longTitle'].encode('utf-8') != '':
                            ssname = title + ' : ' + str(sslist[index]['title'].encode('utf-8')) + ' - ' + sslist[index]['longTitle'].encode('utf-8') + ' [COLOR pink][会员][/COLOR]'
                        else:
                            ssname = title + ' : ' + str(sslist[index]['title'].encode('utf-8')) + ' [COLOR pink][会员][/COLOR]'
                    else:
                        if sslist[index]['longTitle'].encode('utf-8') != '':
                            ssname = title + ' : ' + str(sslist[index]['title'].encode('utf-8')) + ' - ' + sslist[index]['longTitle'].encode('utf-8')
                        else:
                            ssname = title + ' : ' + str(sslist[index]['title'].encode('utf-8'))
                    #href = 'https://www.bilibili.com/bangumi/play/ep' + str(sslist[index]['id']) + '?https://www.bilibili.com/video/' + elist[index]['bvid']
                    href = 'https://www.bilibili.com/bangumi/play/ep' + str(sslist[index]['id'])
                    videosource['name'] = ssname
                    videosource['href'] = plugin.url_for('play',name=ssname,url=href)
                    sources.append(videosource)
            
        return sources

      else:
        #print('视频')
        r = requests.get(url,headers=headers)
        
        rtext = r.text
        str1 = rtext.find('window.__INITIAL_STATE__=')
        str2 = rtext.find(';(function(){var s')
        vjson = rtext[str1+25:str2]
        #print(vjson)
        j = json.loads(vjson)
        vlist = j['videoData']['pages']
        for index in range(len(vlist)):
            if len(vlist) == 1:
                href = url
            else:
                href = url + '?p=' + str(vlist[index]['page'])
            videosource = {}
            videosource['name'] = str(vlist[index]['page']) + ' - ' + vlist[index]['part']
            #videosource['thumb'] = j['videoData']['pic']
            videosource['href'] = plugin.url_for('play',name=(str(vlist[index]['page']) + ' - ' + vlist[index]['part']).encode('utf-8'),url=href)
            #
            sources.append(videosource)
        return sources

#收藏分类列表
@plugin.cached(TTL=10)
def get_collectlist(uid):
    clists = []
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Cookie': sessdata(), # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
        'Host': 'api.bilibili.com'
    }
    r = requests.get('https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid='+str(uid)+'&jsonp=jsonp',headers=apiheaders)
    j = json.loads(r.text)
    try:
        c = j['data']['list']
        for index in range(len(c)):
            source = {}
            source['name'] = c[index]['title']
            source['href'] = c[index]['id']
            clists.append(source)
    except TypeError:
        dialog = xbmcgui.Dialog()
        dialog.notification('获取不到收藏信息','可能是sessdata已经过期', xbmcgui.NOTIFICATION_INFO, 5000)
    return clists

#收藏分类下视频列表
@plugin.cached(TTL=10)
def get_collect(id,page):
    clists = []
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Cookie': sessdata(), # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
        'Host': 'api.bilibili.com'
    }
    r = requests.get('https://api.bilibili.com/x/v3/fav/resource/list?media_id='+str(id)+'&pn='+str(page)+'&ps=20&keyword=&order=mtime&type=0&tid=0&jsonp=jsonp',headers=apiheaders)
    j = json.loads(r.text)
    c = j['data']['medias']
    for index in range(len(c)):
        source = {}
        source['name'] = c[index]['title']
        source['thumb'] = c[index]['cover']
        source['href'] = 'https://www.bilibili.com/video/' + c[index]['bvid']
        clists.append(source)
    dialog = xbmcgui.Dialog()
    allnum = j['data']['info']['media_count']
    allpage = int(int(allnum)/20) + 1
    dialog.notification('第'+str(page)+'/'+str(allpage)+'页','共' + str(allnum) + '个视频', xbmcgui.NOTIFICATION_INFO, 5000,False)
    return clists

#追番/追剧 mode=1 是追番列表 2是追剧列表
@plugin.cached(TTL=10)
def get_zhui(uid,page,mode):
    clists = []
    apiheaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Cookie': sessdata(), # 登录B站后复制一下cookie中的SESSDATA字段,有效期1个月
        'Host': 'api.bilibili.com'
    }
    r = requests.get('https://api.bilibili.com/x/space/bangumi/follow/list?type='+str(mode)+'&follow_status=0&pn='+str(page)+'&ps=30&vmid='+str(uid),headers=apiheaders)
    j = json.loads(r.text)
    try:
        c = j['data']['list']
        for index in range(len(c)):
            source = {}
            if c[index]['badge'] != '':
                source['name'] = c[index]['title'] + ' [COLOR pink][' +c[index]['badge'] +'][/COLOR]'
            else:
                source['name'] = c[index]['title']
            source['thumb'] = c[index]['cover']
            source['href'] = 'https://www.bilibili.com/bangumi/play/ss' + str(c[index]['season_id'])
            clists.append(source)
        dialog = xbmcgui.Dialog()
        allnum = j['data']['total']
        allpage = int(int(allnum)/30) + 1
        dialog.notification('第'+str(page)+'/'+str(allpage)+'页','共' + str(allnum) + '个节目', xbmcgui.NOTIFICATION_INFO, 5000,False)
    except KeyError:
        dialog = xbmcgui.Dialog()
        dialog.notification('获取不到追番/追剧信息','可能是sessdata已经过期', xbmcgui.NOTIFICATION_INFO, 5000)
    return clists

@plugin.route('/play/<name>/<url>/')
def play(name,url):
    ifbangumiurl = re.match('https://www.bilibili.com/bangumi/play/ep',url)
    ifvideourl = re.match('https://www.bilibili.com/video/',url)
    if ifbangumiurl or ifvideourl != None:
      if ifbangumiurl != None:
        #番剧
        items = []
        if 'bgtitle' in cache:
            ti = cache['bgtitle']
            ti = ti.encode('utf-8')
            if re.search('僅限.*地區',ti):
                #gangaotai
                item = {'label': '[1080p]b站国外代理解析 [多谢 biliplus.com API]','path': plugin.url_for('api4', name=name,url=url,quality='80')}
                items.append(item)

                item = {'label': '[720p]b站国外代理解析 [多谢 biliplus.com API]','path': plugin.url_for('api4', name=name,url=url,quality='64')}
                items.append(item)

                item = {'label': '[480p]b站国外代理解析 [多谢 biliplus.com API]','path': plugin.url_for('api4', name=name,url=url,quality='32')}
                items.append(item)

                if re.search('僅限.*台.*地區',ti):
                    item = {'label': '[480p]b站台湾代理解析 [多谢 kghost.info API]','path': plugin.url_for('api5', name=name,url=url,quality='32',api=1)}
                    items.append(item)
                if re.search('僅限.*港.*地區',ti):
                    item = {'label': '[480p]b站香港代理解析 [多谢 kghost.info API]','path': plugin.url_for('api5', name=name,url=url,quality='32',api=2)}
                    items.append(item)
                
                item = {'label': '[320p]b站国外代理解析 [多谢 biliplus.com API]','path': plugin.url_for('api4', name=name,url=url,quality='16')}
                items.append(item)

                if re.search('僅限.*台.*地區',ti):
                    item = {'label': '[320p]b站台湾代理解析 [多谢 kghost.info API]','path': plugin.url_for('api5', name=name,url=url,quality='16',api=1)}
                    items.append(item)
                if re.search('僅限.*港.*地區',ti):
                    item = {'label': '[320p]b站香港代理解析 [多谢 kghost.info API]','path': plugin.url_for('api5', name=name,url=url,quality='16',api=2)}
                    items.append(item)
            else:
                #dalu
                if sessdata(mode='vip') != '':
                    #dialog = xbmcgui.Dialog()
                    #ok = dialog.ok('错误提示', sessdata())
                    item = {'label': '[1080p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=80)}
                    items.append(item)
                    item = {'label': '[720p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=64)}
                    items.append(item)
                else:
                    dialog = xbmcgui.Dialog()
                    dialog.notification('未设置sessdata','使用api2 720p以上解析，请在 高级功能 内填写sessdata', xbmcgui.NOTIFICATION_INFO, 5000)
                item = {'label': '[480p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=32)}
                items.append(item)
                item = {'label': '[320p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=16)}
                items.append(item)
                #item = {'label': '[480p][6分钟试看]使用 b站官方api3 解析','path': plugin.url_for('bangumiapi', name=name,url=url)}
                #items.append(item)
        return items
      else:
        
        #视频
        items = []
        item = {'label': '[1080p]使用 b站官方api1 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api1', name=name,url=url,quality=80)}
        items.append(item)
        item = {'label': '[1080p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=80)}
        items.append(item)
        item = {'label': '[原画]使用 xbeibeix.com api 解析','path': plugin.url_for('api2', name=name,url=url)}
        items.append(item)
        item = {'label': '[720p]使用 b站官方api1 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api1', name=name,url=url,quality=64)}
        items.append(item)
        item = {'label': '[720p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=64)}
        items.append(item)
        item = {'label': '[480p]使用 b站官方api1 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api1', name=name,url=url,quality=32)}
        items.append(item)
        item = {'label': '[480p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=32)}
        items.append(item)
        item = {'label': '[320p]使用 b站官方api1 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api1', name=name,url=url,quality=16)}
        items.append(item)
        item = {'label': '[320p]使用 b站官方api2 解析 [万分感谢 Henryhaohao]','path': plugin.url_for('api3', name=name,url=url,quality=16)}
        items.append(item)
        
        return items


@plugin.route('/bangumiapi/<name>/<url>/')
#解析番剧地址
def bangumiapi(name,url):
    j = get_bangumijson(url)
    items = []
    if j['code'] == 0:
        k = j['result']['durl']
        item = {'label': '[540P]'+name,'path': k[0]['url'],'is_playable': True}
        items.append(item)
    else:
        if j['code'] == -10403:
            #大会员错误码
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('错误提示', '此为大会员专享视频，无法解析')
        else:
            #
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('错误提示', '未知的api错误代码,可能是b站官方更改了接口')
    return items

# @plugin.route('/playvideo/<vlist>/')
# def playvideo(vlist):
#     vlist = eval(vlist)
#     playlist = xbmc.PlayList(1)
#     playlist.clear()
#     player = BPlayer()
#     for url in vlist:
#         list_item = xbmcgui.ListItem(u'播放')
#         playlist.add(url, listitem=list_item)
#     player.play(playlist)

# @plugin.route('/api1/<name>/<url>/<quality>/')
# #使用api1
# def api1(name,url,quality):
#     mp4url = get_api1(url,quality)
#     mp4info = get_mp4info(url)
#     img = mp4info['img']
#     items = []
#     head = '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36&Referer=https://www.bilibili.com&Range=bytes=0-&Connection=keep-alive&Origin=https://www.bilibili.com&Accept-Encoding=gzip, deflate, br'
#     vlist = []
#     for index in range(len(mp4url)):
#         vlist.append(mp4url[index]+head)
#     item = {'label': name+' - '+mp4info['title'].encode('utf-8'),'path': plugin.url_for('playvideo',vlist=str(vlist)),'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
#     items.append(item)

#     face = mp4info['face']
#     item = {'label': '查看 [COLOR yellow]'+mp4info['upname'].encode('utf-8') +'[/COLOR] 的主页','path': plugin.url_for('up',uid=mp4info['uid'],page=1),'thumbnail': face,'icon': face}
#     items.append(item)
#     item = {'label': '评论区 [COLOR yellow]' + mp4info['reply'] + '[/COLOR]','path': plugin.url_for('conn',url=url)}
#     items.append(item)
    
#     return items

@plugin.route('/api1/<name>/<url>/<quality>/')
#使用api1
def api1(name,url,quality):
    mp4url = get_api1(url,quality)
    mp4info = get_mp4info(url)
    img = mp4info['img']
    items = []
    head = '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36&Referer=https://www.bilibili.com&Range=bytes=0-&Connection=keep-alive&Origin=https://www.bilibili.com&Accept-Encoding=gzip, deflate, br'
    for index in range(len(mp4url)):
        item = {'label': name+' - '+mp4info['title'].encode('utf-8'),'path': mp4url[index]+head,'is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
        items.append(item)

    face = mp4info['face']
    item = {'label': '查看 [COLOR yellow]'+mp4info['upname'].encode('utf-8') +'[/COLOR] 的主页','path': plugin.url_for('up',uid=mp4info['uid'],page=1),'thumbnail': face,'icon': face}
    items.append(item)
    item = {'label': '评论区 [COLOR yellow]' + mp4info['reply'] + '[/COLOR]','path': plugin.url_for('conn',url=url)}
    items.append(item)
    
    return items

@plugin.route('/api2/<name>/<url>/')
#使用api2
def api2(name,url):
    mp4url = get_api2(url)
    dialog = xbmcgui.Dialog()
    dialog.textviewer('错误提示', str(mp4url))
    mp4info = get_mp4info(url)
    img = mp4info['img']
    items = []
    head = '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36&Referer=https://www.bilibili.com'
    item = {'label': name+' - '+mp4info['title'].encode('utf-8'),'path': str(mp4url)+head,'is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
    items.append(item)
    face = mp4info['face']
    item = {'label': '查看 [COLOR yellow]'+mp4info['upname'].encode('utf-8') +'[/COLOR] 的主页','path': plugin.url_for('up',uid=mp4info['uid'],page=1),'thumbnail': face,'icon': face}
    items.append(item)
    item = {'label': '评论区 [COLOR yellow]' + mp4info['reply'] + '[/COLOR]','path': plugin.url_for('conn',url=url)}
    items.append(item)
    
    return items

@plugin.route('/api3/<name>/<url>/<quality>/')
#
def api3(name,url,quality):
    ifbangumiurl = re.match('https://www.bilibili.com/bangumi/play/ep',url)
    ifvideourl = re.match('https://www.bilibili.com/video/',url)
    if ifbangumiurl or ifvideourl != None:
        if ifbangumiurl != None:
            mp4url = get_api3(url,quality)
            mp4info = get_bangumiinfo(url)
        if ifvideourl != None:
            mp4url = get_api3(url,quality)
            mp4info = get_mp4info(url)
    
    
    img = mp4info['img']
    items = []
    head = '|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36&Referer=https://www.bilibili.com'
    for index in range(len(mp4url)):
        item = {'label': name+' - '+mp4info['title'].encode('utf-8'),'path': mp4url[index]+head,'is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
        items.append(item)
    if ifvideourl != None:
        face = mp4info['face']
        item = {'label': '查看 [COLOR yellow]'+mp4info['upname'].encode('utf-8') +'[/COLOR] 的主页','path': plugin.url_for('up',uid=mp4info['uid'],page=1),'thumbnail': face,'icon': face}
        items.append(item)
    item = {'label': '评论区 [COLOR yellow]'+ mp4info['reply'] + '[/COLOR]','path': plugin.url_for('conn',url=url)}
    items.append(item)
    
    return items

#代理解析1
@plugin.route('/api4/<name>/<url>/<quality>/')
def api4(name,url,quality):
    mp4url = get_api4(url,quality)
    mp4info = get_bangumiinfo(url)
    mp4url =mp4url[0]
    #if mp4url.find('upos-hz-mirrorakam.akamaized.net') != -1:
        #mp4url = mp4url.replace('upos-hz-mirrorakam.akamaized.net','calm-meadow-79f1.zhengfan2014.workers.dev')
    img = mp4info['img']
    items = []
    item = {'label': name+' - '+mp4info['title'].encode('utf-8'),'path': mp4url,'is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
    items.append(item)
    item = {'label': '评论区 [COLOR yellow]'+ mp4info['reply'] + '[/COLOR]','path': plugin.url_for('conn',url=url)}
    items.append(item)
    return items

#代理解析2
@plugin.route('/api5/<name>/<url>/<quality>/<api>/')
def api5(name,url,quality,api):
    mp4url = get_api5(url,quality,api)
    #dialog = xbmcgui.Dialog()
    #dialog.textviewer('评论区',str(mp4url))
    mp4info = get_bangumiinfo(url)
    img = mp4info['img']
    items = []
    item = {'label': name+' - '+mp4info['title'].encode('utf-8'),'path': mp4url,'is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
    items.append(item)
    item = {'label': '评论区 [COLOR yellow]'+ mp4info['reply'] + '[/COLOR]','path': plugin.url_for('conn',url=url)}
    items.append(item)
    return items

@plugin.route('/sources/<url>/')
def sources(url):
    sources = get_sources(url)
    items = [{
        'label': source['name'],
        'path': source['href']
        #'is_playable': True
    } for source in sources]
    sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items


@plugin.route('/category/<url>/')
def category(url):
    #dialog = xbmcgui.Dialog()
    #ok = dialog.ok('错误提示', url)

    videos = get_videos(url)
    items = [{
        'label': video['name'],
        'path': plugin.url_for('sources', url=video['href']),
	'thumbnail': video['thumb'],
	'icon': video['thumb'],
    'info': video['info'],
    } for video in videos]

    sorted_items = items
    #sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items

@plugin.route('/collectlist')
def collectlist():
    #dialog = xbmcgui.Dialog()
    #ok = dialog.ok('错误提示', url)
    if 'uid' in cache:
        uid = cache['uid']
        clists = get_collectlist(uid)
        items = [{
            'label': clist['name'],
            'path': plugin.url_for('collect', id=clist['href'],page=1),
        } for clist in clists]
    else:
        items = []

    sorted_items = items
    #sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items

@plugin.route('/collect/<id>/<page>/')
def collect(id,page):
    #dialog = xbmcgui.Dialog()
    #ok = dialog.ok('错误提示', url)
    
    clists = get_collect(id,page)
    items = [{
        'label': clist['name'],
        'path': plugin.url_for('sources', url=clist['href']),
        'thumbnail': clist['thumb'],
        'icon': clist['thumb'],
    } for clist in clists]
    if len(clists) == 20:
        items.append({
            'label': u'[COLOR yellow]下一页[/COLOR]',
            'path': plugin.url_for('collect',page=int(page)+1,id=id),
        })
    
    sorted_items = items
    #sorted_items = sorted(items, key=lambda item: item['label'])
    return sorted_items

@plugin.route('/zhui/<page>/<mode>/')
def zhui(page,mode):
    #dialog = xbmcgui.Dialog()
    #ok = dialog.ok('错误提示', url)
    if 'uid' in cache:
        uid =cache['uid']
        clists = get_zhui(uid,page,mode)
        items = [{
            'label': clist['name'],
            'path': plugin.url_for('sources', url=clist['href']),
            'thumbnail': clist['thumb'],
            'icon': clist['thumb'],
        } for clist in clists]
        if len(clists) == 30:
            items.append({
                'label': u'[COLOR yellow]下一页[/COLOR]',
                'path': plugin.url_for('zhui',page=int(page)+1,mode=mode),
            })
    else:
        items =[]
    return items

@plugin.route('/')
def index():
    categories = get_categories()
    items = []
    for category in categories:
        items.append({
            'label': category['name'],
            'path': plugin.url_for('category', url=category['link']),
        })
    items.append({
        'label': u'[COLOR yellow]直播[/COLOR]',
        'path': plugin.url_for('live'),
    })
    items.append({
        'label': u'[COLOR yellow]收藏/追番[/COLOR]',
        'path': plugin.url_for('my'),
    })
    items.append({
        'label': u'[COLOR yellow]搜索/av/bv号[/COLOR]',
        'path': plugin.url_for('sea'),
    })
    # items.append({
    #     'label': u'[COLOR yellow]设置[/COLOR]',
    #     'path': plugin.url_for('vip'),
    # })
    return items

@plugin.route('/my/')
def my():
    items = []
    if 'uid' in cache and 'sessdata' in cache and cache['uid'] != '' and cache['sessdata'] != '':
        items.append({
            'label': u'收藏列表',
            'path': plugin.url_for('collectlist'),
        })
        items.append({
            'label': u'追番列表',
            'path': plugin.url_for('zhui',page=1,mode=1),
        })
        items.append({
            'label': u'追剧列表',
            'path': plugin.url_for('zhui',page=1,mode=2),
        })
        items.append({
            'label': u'投稿的视频',
            'path': plugin.url_for('up',page=1,uid=cache['uid']),
        })
    else:
        items.append({
            'label': u'请先设置uid和sessdata的值后，方可使用',
            'path': 'error',
        })
    return items

@plugin.route('/sea/')
def sea():
    items = []
    items.append({
        'label': u'综合搜索',
        'path': plugin.url_for('history',name='输入关键词搜索',url='search'),
    })
    items.append({
        'label': u'搜索视频',
        'path': plugin.url_for('history',name='输入关键词搜索视频',url='vidsearch'),
    })
    items.append({
        'label': u'输入av或者bv号或者链接',
        'path': plugin.url_for('history',name='输入av或者bv号或者链接打开视频',url='vid'),
    })
    items.append({
        'label': u'搜索番剧',
        'path': plugin.url_for('history',name='输入关键词搜索番剧',url='bgsearch'),
    })
    items.append({
        'label': u'搜索影视',
        'path': plugin.url_for('history',name='输入关键词搜索电影电视剧纪录片',url='movsearch'),
    })
    items.append({
        'label': u'搜索up主',
        'path': plugin.url_for('history',name='输入关键词搜索up主',url='upsearch'),
    })
    items.append({
        'label': u'搜索正在直播的直播间',
        'path': plugin.url_for('history',name='输入关键词搜索直播间（搜索主播名字进直播间请用搜索up主）',url='livesearch'),
    })
    
    items.append({
        'label': u'输入房间号进入直播间',
        'path': plugin.url_for('history',name='输入房间号进入直播间',url='roomid'),
    })
    return items

# @plugin.route('/vip/')
# def vip():
    

#     items = []
#     if 'uid' in cache and cache['uid'] != '':
#         items.append({
#             'label': u'设置uid (uid:'+cache['uid'] +')',
#             'path': plugin.url_for('input',key='uid',value='请输入uid：'),
#         })
#     else:
#         items.append({
#             'label': u'设置uid (uid为空)',
#             'path': plugin.url_for('input',key='uid',value='请输入uid：'),
#         })
#     if 'sessdata' in cache and cache['sessdata'] != '':
#         items.append({
#             'label': u'设置SESSDATA (SESSDATA:'+cache['sessdata'] +')',
#             'path': plugin.url_for('input',key='sessdata',value='请输入sessdata：(sessdata有效期30天，过期后只能解析480p的视频)'),
#         })
#     else:
#         items.append({
#             'label': u'设置SESSDATA (sessdata为空)',
#             'path': plugin.url_for('input',key='sessdata',value='请输入sessdata：(sessdata有效期30天，过期后只能解析480p的视频)'),
#         })
    
#     items.append({
#         'label': 'up主视频白嫖率计算 - 仅供娱乐 (状态:'+chushihua('bq',0) +')',
#         'path': plugin.url_for('switch',key='bq'),
#     })
#     return items

@plugin.route('/search/<value>/<page>/')
def search(value,page):
    items = []
    if value != 'null' and int(page) != 1:
        keyword = value
    else:
        keyboard = xbmc.Keyboard('', '请输入搜索内容')
        xbmc.sleep(1500)
        hi = his['search']
        if value != 'null':
            keyboard.setDefault(value)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()
            if keyword != '':
                hi[keyword] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    try:
        videos = get_search(keyword,page)
        items = [{
            'label': video['name'],
            'path': plugin.url_for('sources', url=video['href']),
            'thumbnail': video['thumb'],
            'icon': video['thumb']
        } for video in videos]
        if len(videos) >= 20:
            items.append({
                'label': u'[COLOR yellow]下一页[/COLOR]',
                'path': plugin.url_for('vidsearch',page=int(page)+1,value=value),
            })
        return items
    except UnboundLocalError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '您取消了搜索', xbmcgui.NOTIFICATION_INFO, 5000,False)
    

@plugin.route('/bgsearch/<value>/<page>/')
def bgsearch(value,page):
    items = []
    if value != 'null' and int(page) != 1:
        keyword = value
    else:
        keyboard = xbmc.Keyboard('', '请输入搜索内容')
        xbmc.sleep(1500)
        hi = his['bgsearch']
        if value != 'null':
            keyboard.setDefault(value)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()
            if keyword != '':
                hi[keyword] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        videos = get_bgsearch(keyword,page)
        items = [{
            'label': video['name'],
            'path': plugin.url_for('sources', url=video['href']),
            'thumbnail': video['thumb'],
            'icon': video['thumb']
        } for video in videos]
        if len(videos) >= 20:
            items.append({
                'label': u'[COLOR yellow]下一页[/COLOR]',
                'path': plugin.url_for('bgsearch',page=int(page)+1,value=value),
            })
        return items
    except UnboundLocalError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '您取消了搜索', xbmcgui.NOTIFICATION_INFO, 5000,False)
    

@plugin.route('/movsearch/<value>/<page>/')
def movsearch(value,page):
    items = []
    if value != 'null' and int(page) != 1:
        keyword = value
    else:
        keyboard = xbmc.Keyboard('', '请输入搜索内容')
        xbmc.sleep(1500)
        hi = his['movsearch']
        if value != 'null':
            keyboard.setDefault(value)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()
            if keyword != '':
                hi[keyword] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        videos = get_movsearch(keyword,page)
        items = [{
            'label': video['name'],
            'path': plugin.url_for('sources', url=video['href']),
            'thumbnail': video['thumb'],
            'icon': video['thumb']
        } for video in videos]
        if len(videos) >= 20:
            items.append({
                'label': u'[COLOR yellow]下一页[/COLOR]',
                'path': plugin.url_for('movsearch',page=int(page)+1,value=value),
            })
        return items
    except UnboundLocalError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '您取消了搜索', xbmcgui.NOTIFICATION_INFO, 5000,False)


@plugin.route('/vidsearch/<value>/<page>/')
def vidsearch(value,page):
    items = []
    if value != 'null' and int(page) != 1:
        keyword = value
    else:
        keyboard = xbmc.Keyboard('', '请输入搜索内容')
        xbmc.sleep(1500)
        hi = his['vidsearch']
        if value != 'null':
            keyboard.setDefault(value)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()
            if keyword != '':
                hi[keyword] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        videos = get_vidsearch(keyword,page)
        items = [{
            'label': video['name'],
            'path': plugin.url_for('sources', url=video['href']),
            'thumbnail': video['thumb'],
            'icon': video['thumb']
        } for video in videos]
        if len(videos) >= 20:
            items.append({
                'label': u'[COLOR yellow]下一页[/COLOR]',
                'path': plugin.url_for('vidsearch',page=int(page)+1,value=value),
            })
        return items
    except UnboundLocalError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '您取消了搜索', xbmcgui.NOTIFICATION_INFO, 5000,False)

@plugin.route('/livesearch/<value>/<page>/')
def livesearch(value,page):
    items = []
    if value != 'null' and int(page) != 1:
        keyword = value
    else:
        keyboard = xbmc.Keyboard('', '请输入搜索内容')
        xbmc.sleep(1500)
        hi = his['livesearch']
        if value != 'null':
            keyboard.setDefault(value)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()
            if keyword != '':
                hi[keyword] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        videos = get_livesearch(keyword,page)
        items = [{
            'label': video['name'],
            'path': plugin.url_for('room', id=video['href']),
            'thumbnail': video['thumb'],
            'icon': video['thumb']
        } for video in videos]
        if len(videos) >= 40:
            items.append({
                'label': u'[COLOR yellow]下一页[/COLOR]',
                'path': plugin.url_for('livesearch',page=int(page)+1,value=value),
            })
        return items
    except UnboundLocalError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '您取消了搜索', xbmcgui.NOTIFICATION_INFO, 5000,False)

@plugin.route('/upsearch/<value>/<page>/')
def upsearch(value,page):
    items = []
    if value != 'null' and int(page) != 1:
        keyword = value
    else:
        keyboard = xbmc.Keyboard('', '请输入搜索内容')
        xbmc.sleep(1500)
        hi = his['upsearch']
        if value != 'null':
            keyboard.setDefault(value)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()
            if keyword != '':
                hi[keyword] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        videos = get_upsearch(keyword,page)
        items = [{
            'label': video['name'],
            'path': plugin.url_for('up', uid=video['href'],page=1),
            'thumbnail': video['thumb'],
            'icon': video['thumb']
        } for video in videos]
        if len(videos) >= 20:
            items.append({
                'label': u'[COLOR yellow]下一页[/COLOR]',
                'path': plugin.url_for('upsearch',page=int(page)+1,value=value),
            })
        return items
    except UnboundLocalError:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '您取消了搜索', xbmcgui.NOTIFICATION_INFO, 5000,False)

@plugin.route('/vid/<value>/')
def vid(value):
    keyboard = xbmc.Keyboard('', '请输入av号或者bv号或者url：')
    xbmc.sleep(1500)
    if value != 'null':
        keyboard.setDefault(value)
    keyboard.doModal()
    hi = his['vid']
    if (keyboard.isConfirmed()):
        if re.search('[Bb]{1}[Vv]{1}[a-zA-Z0-9]+',keyboard.getText()) or re.search('[aA]{1}[vV]{1}[0-9]+',keyboard.getText()):
            if re.search('[Bb]{1}[Vv]{1}[a-zA-Z0-9]+',keyboard.getText()):
                keyword = re.search('[Bb]{1}[Vv]{1}[a-zA-Z0-9]+',keyboard.getText()).group()
                dialog = xbmcgui.Dialog()
                dialog.notification('BV号提取成功',keyword, xbmcgui.NOTIFICATION_INFO, 5000,False)
                hi[keyword] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if re.search('[aA]{1}[vV]{1}[0-9]+',keyboard.getText()):
                keyword = re.search('[aA]{1}[vV]{1}[0-9]+',keyboard.getText()).group()
                dialog = xbmcgui.Dialog()
                dialog.notification('AV号提取成功',keyword, xbmcgui.NOTIFICATION_INFO, 5000,False)
                hi[keyword] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            sources = get_sources('https://www.bilibili.com/video/'+str(keyword))
            items = [{
                'label': source['name'],
                'path': source['href'],
                #'thumbnail': source['thumb'],
                #'icon': source['thumb'],
            } for source in sources]
            #sorted_items = sorted(items, key=lambda item: item['label'])
            return items
    else:
        dialog = xbmcgui.Dialog()
        dialog.notification('提示', '您取消了输入', xbmcgui.NOTIFICATION_INFO, 5000,False)

@plugin.route('/roomid/<value>/')
def roomid(value):
    if value == 'null':
        keyboard = xbmc.Keyboard('', '请输入房间号(纯数字)：')
        xbmc.sleep(1500)
        keyboard.doModal()

        hi = his['roomid']
        if (keyboard.isConfirmed()):
            keyword = keyboard.getText()
            hi[keyword] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    else:
        keyword = value
    items = []
    id = int(keyword)
    mp4list = get_roommp4(id)
    mp4info = get_roominfo(id)
    img = mp4info['img']
    
    for index in range(len(mp4list)):
        title = ''
        if index == 0:
            title += '[主线]'
        else:
            title += '[备线'+str(index)+']'
        title += '[原画]' + mp4info['title'].encode('utf-8')
        item = {'label': title,'path':mp4list[index],'is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
        items.append(item)
    if mp4info['status'] == '未开播':
        item = {'label': '[未开播]' +rd_live_gz(),'path':'0','is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
        items.append(item)
    return items

@plugin.route('/live/')
def live():
    items = []
    items.append({'label': '全部','path': plugin.url_for('livelist', page=1)})
    videos = [{'name':'网游','url':plugin.url_for('livelistmore', url='https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=2&cate_id=0&area_id=0&sort_type=sort_type_124&page_size=30&tag_version=1',page=1)},
              {'name':'手游','url':plugin.url_for('livelistmore', url='https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=3&cate_id=0&area_id=0&sort_type=sort_type_121&page_size=30&tag_version=1',page=1)},
              {'name':'单机','url':plugin.url_for('livelistmore', url='https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=6&cate_id=0&area_id=0&sort_type=sort_type_150&page_size=30&tag_version=1',page=1)},
              {'name':'娱乐','url':plugin.url_for('livelistmore', url='https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=1&cate_id=0&area_id=0&sort_type=sort_type_152&page_size=30&tag_version=1',page=1)},
              {'name':'电台','url':plugin.url_for('livelistmore', url='https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=5&cate_id=0&area_id=0&sort_type=income&page_size=30&tag_version=1',page=1)},
              {'name':'绘画','url':plugin.url_for('livelistmore', url='https://api.live.bilibili.com/room/v3/area/getRoomList?platform=web&parent_area_id=4&cate_id=0&area_id=0&sort_type=sort_type_56&page_size=30&tag_version=1',page=1)}]
    for video in videos:
        items.append({'label': video['name'],'path': video['url']})
    
    return items

@plugin.route('/livelist/<page>/')
def livelist(page):
    items = []
    videos = get_live(page)
    items = [{
        'label': video['name'],
        'path': plugin.url_for('room', id=video['href']),
	'thumbnail': video['thumb'],
	'icon': video['thumb'],
    } for video in videos]
    if len(videos) == 30:
        items.append({
            'label': u'[COLOR yellow]下一页[/COLOR]',
            'path': plugin.url_for('livelist',page=int(page)+1),
        })
    return items

@plugin.route('/livelistmore/<url>/<page>/')
def livelistmore(url,page):
    items = []
    videos = get_livemore(url,page)
    items = [{
        'label': video['name'],
        'path': plugin.url_for('room', id=video['href']),
	'thumbnail': video['thumb'],
	'icon': video['thumb'],
    } for video in videos]
    if len(videos) == 30:
        items.append({
            'label': u'[COLOR yellow]下一页[/COLOR]',
            'path': plugin.url_for('livelistmore',url=url,page=int(page)+1),
        })
    return items

@plugin.route('/room/<id>/')
def room(id):
    items = []
    mp4list = get_roommp4(id)
    mp4info = get_roominfo(id)
    img = mp4info['img']
    for index in range(len(mp4list)):
        title = ''
        if index == 0:
            title += '[主线]'
        else:
            title += '[备线'+str(index)+']'
        title += '[原画]' + mp4info['title'].encode('utf-8')
        item = {'label': title,'path':mp4list[index],'is_playable': True,'info':mp4info,'info_type':'video','thumbnail': img,'icon': img}
        items.append(item)
    return items

@plugin.route('/up/<uid>/<page>/')
def up(uid,page):
    videos = get_up(uid,page)
    items = []
    if int(page) == 1:
        u = json.loads(get_up_baseinfo(uid))
        r = json.loads(get_up_roomold(uid))
        items.append({
            'label': u'关于[COLOR yellow]'+ u['data']['name'] + u'[/COLOR]目前已知的情报',
            'path': plugin.url_for(upinfo,uid=uid),
            'thumbnail': u['data']['face'],
            'icon': u['data']['face'],
        })
        if int(r['data']['liveStatus']) == 1:
            livename = u'通往[COLOR yellow]'+ u['data']['name'] +u'[/COLOR]的直播间:' + u'[COLOR red][·LIVE][/COLOR]' + r['data']['title']
        else:
            livename = u'[COLOR yellow]'+ u['data']['name'] +u'[/COLOR]的直播间:' + u'[在线' + zh(r['data']['online']).decode('utf-8') + u']' + u'[COLOR green][Close][/COLOR]' + r['data']['title']
        items.append({
            'label': livename,
            'path': plugin.url_for(room,id=r['data']['roomid']),
            'thumbnail': r['data']['cover'],
            'icon': r['data']['cover'],
        })
    for video in videos:
        items.append({'label': video['name'],'path': plugin.url_for('sources', url=video['href']),'thumbnail': video['thumb'],'icon': video['thumb']})
    if len(videos) == 30:
        items.append({
            'label': '[COLOR yellow]下一页[/COLOR]  ',
            'path': plugin.url_for(up,uid=uid,page=int(page)+1),
        })
    
    
    return items

# @plugin.route('/liveplay/<url>/<q>/')
# def liveplay(url,q):
#     items = []
#     q = eval(q)
#     for index in range(len(q)):
#         #qn = re.search('&qn=\d+',url).group()
#         #url = url.replace(qn,'&qn='+q[index]['qn'])
#         item = {'label': q[index]['name'],'path': url+'&qn='+str(q[index]['qn']),'is_playable': True}
#         items.append(item)
    
#     return items

@plugin.route('/input/<key>/<value>/')
def input(key,value):
    keyboard = xbmc.Keyboard('', value)
    xbmc.sleep(1500)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('确认该值正确吗？', keyboard.getText())
        if ret:
            cache[key] = keyboard.getText()
            dialog = xbmcgui.Dialog()
            dialog.notification('提示','保存成功', xbmcgui.NOTIFICATION_INFO, 5000,False)

@plugin.route('/switch/<key>/')
def switch(key):
    if cache[key] == 1:
        cache[key] = 0
    else:
        cache[key] = 1



@plugin.route('/conn/<url>/')
def conn(url):
    text = '********************热门评论********************\n'
    text += get_comm(url,'2')
    text += '\n********************最新评论********************\n'
    text += get_comm(url,'1')
    dialog = xbmcgui.Dialog()
    dialog.textviewer('评论区',text)

@plugin.route('/upinfo/<uid>/')
def upinfo(uid):
    text = get_upinfo(uid)
    dialog = xbmcgui.Dialog()
    dialog.textviewer('评论区',text)


@plugin.route('/labels/<label>/')
def show_label(label):
    # 写抓取视频类表的方法
    #
    items = [
        {'label': label},
    ]
    return items

def get_key (dict, value):
  return [k for k, v in dict.items() if v == value]

@plugin.route('/history/<name>/<url>/')
def history(name,url):
    items = []
    if url == 'search' or url =='bgsearch' or url == 'movsearch' or url == 'vidsearch' or url == 'livesearch' or url == 'upsearch':
        items.append({
            'label': '[COLOR yellow]'+ name +'[/COLOR]',
            'path': plugin.url_for(url,value='null',page=1),
        })
    else:
        items.append({
            'label': '[COLOR yellow]'+ name +'[/COLOR]',
            'path': plugin.url_for(url,value='null'),
        })
    #his[url] ={'aaa':'2019-01-23 10:00:00','bbb':'2019-01-23 09:01:00','ccc':'2019-01-23 09:00:59'}
    if url in his:
        hi = his[url]
        
    else:
        his[url] = {}
        hi = his[url]
        
    #hi = []
    if hi:
        val = list(hi.values())
        val = sorted(val,reverse=True)
        for index in range(len(val)):
            if url == 'search' or url == 'bgsearch' or url == 'vidsearch' or url == 'movsearch' or url == 'livesearch' or url == 'upsearch':
                items.append({
                    'label': name+ ':' +get_key(hi,val[index])[0] + ' - [查询时间：' + val[index] +']',
                    'path': plugin.url_for(url,value=get_key(hi,val[index])[0],page=1),
                })
            else:
                items.append({
                    'label': name+ ':' +get_key(hi,val[index])[0] + ' - [查询时间：' + val[index] +']',
                    'path': plugin.url_for(url,value=get_key(hi,val[index])[0]),
                })
        #for index in range(len(hi)):
            #items.append({
                #'label': name+ ':' +hi[index],
                #'path': plugin.url_for(url,value=hi[index]),
            #})
        items.append({
            'label': '[COLOR yellow]清除历史记录[/COLOR]',
            'path': plugin.url_for('cleanhis',url=url),
        })
    else:
        items.append({
            'label': '[COLOR yellow]历史记录为空[/COLOR]',
            'path': plugin.url_for(ok,value='历史记录为空'),
        })

    return items

@plugin.route('/ok/<value>/')
def ok(value):
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('提示', value)

@plugin.route('/cleanhis/<url>/')
def cleanhis(url):
    his[url] = {}
    dialog = xbmcgui.Dialog()
    ok = dialog.ok('提示', '清理历史记录成功')

if __name__ == '__main__':
    plugin.run()
