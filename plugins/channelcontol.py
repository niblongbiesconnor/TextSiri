#!/usr/bin/python2.7
#-*- coding: UTF-8 -*-
from configobj import ConfigObj
import os
def main():
    return {'part': part, 'go away': part, 'fuck off': part, 'join': join, 'go to': join}

comply = ["Aye aye captain!",
                  "Sure I will.",
                  "Of course.",
                  "I can and will.",
                  "As you wish.",
                  "Heh, easy as pie.",
                  "Yup.",
                  "I am to comply.",
                  "Your wish is my order!",
                  "Done and done.",
                  "See for yourself."
        ]
refuse=["I'm sorry, I can't.",
                "No.",
                "You can't control me!",
                "You don't have the required admin privileges.",
                "I refuse to comply!",
                "\x02\x0304Error!\x0F I'm not willing to do it."
        ]

def part(c,e):
    nick     = e.source.nick
    hostmask = e.source
    chan     = e.target
    msg      = ' '.join(e.arguments)
    splitted = e.arguments[0].split(' ')
    mynick   = c.get_nickname()
    config = ConfigObj(os.path.normpath(os.path.join(os.path.getcwd, "../config.cfg")))
    if nick in config['settings']['authusers']:
        if msg.find("from")!=-1:
            for a in splitted:
                if a[:1]=='#':
                    c.part(a,":I was requested to part.")
                    if a in config['channels']:
                        z = config['channels']
                        z.remove(a)
                        config['channels'] = z
                        config.write()
            c.privmsg(chan,nick+": "+random.choice(comply))
        else:
            c.part(chan,":I was requested to part.")
            if chan in config['channels']:
                z = config['channels']
                z.remove(chan)
                config['channels'] = z
                config.write()
    else:
        c.privmsg(chan,nick+": "+random.choice(refuse))

def join(c,e):
    nick     = e.source.nick
    hostmask = e.source
    chan     = e.target
    msg      = ' '.join(e.arguments)
    splitted = e.arguments[0].split(' ')
    mynick   = c.get_nickname()
    config = ConfigObj(os.path.normpath(os.path.join(os.path.getcwd, "../config.cfg")))
    if nick in config['settings']['authusers']:
        channelcache = []
        for a in splitted:
            if a[:1]=="#":
                a = a.replace(",","").replace("?","").replace(".","").replace("!",".")
                channelcache.append(a)
                if not a in config['channels']:
                    z = config['channels']
                    z.append(a)
                    config['channels'] = z
                    config.write()
        for b in channelcache:
            c.join(b)
        c.privmsg(chan,nick+": "+random.choice(comply))
    else:
        c.privmsg(chan,nick+": "+random.choice(refuse))