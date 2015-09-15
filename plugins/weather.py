#!/usr/bin/python2.7
#-*- coding: UTF-8 -*-
import requests

def main():
    return {'weather': weather, 'umbrella': umbrella}

def weather(c, e):
    nick     = e.source.nick
    hostmask = e.source
    chan     = e.target
    msg      = ' '.join(e.arguments)
    splitted = e.arguments[0].split(' ')
    mynick   = c.get_nickname()
    if 'in' in splitted:
        r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=%s'%(splitted[-1].replace("?","").replace("!","").replace(".","")))
        a = r.json()
        if a['cod']==200:
            c.privmsg(chan,nick+': Today is \x02'+a['weather'][0]['main'].lower()+'\x02 in \x02'+a['name']+'\x02 with a temperature of \x02'+str(int(a['main']['temp']) - 273)+'C\x02.')
        else:
            c.privmsg(chan,nick+': \x02\x0304Error!\x02 I couldn\'t find \x02'+splitted[-1].replace("?","").replace("!","").replace(".","")+'\x02.')
    else:
        c.privmsg(chan,nick+': \x02\x0304Error!\x0F No city specified. \x02Usage\x02: "'+mynick+', what\'s the weather like in London?"')


def umbrella(c,e):
    nick     = e.source.nick
    hostmask = e.source
    chan     = e.target
    msg      = ' '.join(e.arguments)
    splitted = e.arguments[0].split(' ')
    mynick   = c.get_nickname()
    if 'in' in splitted:
            r = requests.get('http://api.openweathermap.org/data/2.5/weather?q=%s'%(splitted[-1].replace("?","").replace("!","").replace(".","")))
            a = r.json()
            if a['cod']==200:
                if a['weather'][0]['main'].lower() == 'rain':
                    c.privmsg(chan,nick+': You should. Today is \x02'+a['weather'][0]['main'].lower()+'y\x02 in \x02'+a['name']+'\x02 with a temperature of \x02'+str(int(a['main']['temp']) - 273)+'C\x02.')
                else:
                    c.privmsg(chan,nick+': You shouldn\'t. Today is \x02'+a['weather'][0]['main'].lower()+'\x02 in \x02'+a['name']+'\x02 with a temperature of \x02'+str(int(a['main']['temp']) - 273)+'C\x02.')
            else:
                c.privmsg(chan,nick+': \x02\x0304Error!\x02 I couldn\'t find \x02'+splitted[-1].replace("?","").replace("!","").replace(".","")+'\x02.')
    else:
        c.privmsg(chan,nick+': \x02\x0304Error!\x0F No city specified. \x02Usage\x02: "'+mynick+', should I use an umbrella in London?"')