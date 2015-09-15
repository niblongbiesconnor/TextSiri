#!/usr/bin/python2.7
#-*- coding: UTF-8 -*-
from __future__ import division
import irc.bot
from pprint import pprint
from configobj import ConfigObj
import os
import requests
import re
import sys
import random
import compiler
from math import *
import parser
import imp
import glob


 
class TextSiri(irc.bot.SingleServerIRCBot):
    def __init__(self, server='', nick='somerandombotxyyz', realname='bot', port=6667):
        self.conf = ConfigObj("config.cfg")
        self.commands = {}
        if server=='':
            if 'settings' in self.conf and self.conf['settings']['server']!='':
                self.settings = self.conf['settings']
                nick = self.settings['nickname']
                realname = self.settings['realname']
                server = self.settings['server']
                port = self.settings['port']
                irc.bot.SingleServerIRCBot.__init__(self, [(server, int(port))], nick, realname)
            else:
                conf['settings'] = {'server': '','port': '6667', 'nickname': '', 'realname': '','password': '', 'authusers': ['your nick']}
                conf['channels'] = ['#chan1','#chan2']
                conf.write()
                print 'A config file has been created named "config.cfg". Go edit it.'
                sys.exit()
        else:
            irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nick, nick)
            self.settings = self.conf['settings']
            nick = self.settings['nickname']
            realname = self.settings['realname']
            server = self.settings['server']
            port = self.settings['port']
            self.conf['settings'] = {'server': server,'port': port, 'nickname': nick, 'realname': realname}
            self.conf.write()
        self.reload_plugins(True)
        print "Welcome to TextSiri v1.0.\nConnecting to {server}:{port}...".format(server=self.settings['server'],
                                                                                   port=self.settings['port'])

    def reload_plugins(self, init=False):
        plugins_folder = [os.path.join(os.getcwd(), 'plugins')]
        plugins = set(glob.glob(os.path.join("plugins", "*.py")))
        for plugin in plugins:
            _plugin = os.path.join(os.getcwd(), plugin)
            # print(plugin.split("/")[1].split(".")[0], plugins_folder)
            try:
                moduleinfo = imp.find_module(plugin.split("/")[1].split(".")[0], plugins_folder)
                pl = imp.load_source(plugin, moduleinfo[1])
            except ImportError as e:
                if str(e).startswith('No module named'):
                    log.error('Failed to load plugin %r: the plugin could not be found.', plugin)
                else:
                    log.error('Failed to load plugin %r: import error %s', plugin, str(e))
                    if init:
                        sys.exit(1)
            except BaseException as e:
                print '[ERROR]'+str(e)
                pass
            else:
                if hasattr(pl, 'main'):
                    functions = pl.main()
                    self.commands.update(functions)
            print "(Re)Loaded %s"%_plugin
    """
    e.target    = "TextSiri" or "##mission712"
    e.source    = "asimov.freenode.net" or "mission712!~missio@unaffiliated/mission712"
    e.type      = "privmsg", "ctcp", "join" etc.
    e.arguments = "this","is","a","test"
    """
    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")
 
    def on_welcome(self, c, e):
        print "Connected."
        if 'password' in self.conf['settings'] and self.conf['settings']['password']!='':
            print "Attempting to identify via NickServ..."
            c.privmsg("NickServ","IDENTIFY "+self.conf['settings']['password'])
        for a in self.conf['channels']:
            print("Joining "+a+"...")
            c.join(a)

    def on_kick(self, c, e):
        nick     = e.source.nick
        hostmask = e.source
        chan     = e.target
        msg      = ' '.join(e.arguments)
        splitted = msg.split(' ')
        mynick   = c.get_nickname()
        if splitted[0]==self.conf['settings']['nickname']:
            del splitted[0]
            print "[KICKED] "+nick+" kicked me from "+chan+" for "+(' '.join(splitted))+"!"
            if chan in self.conf['channels']:
                z = self.conf['channels']
                z.remove(chan)
                self.conf['channels'] = z
                self.conf.write()
        else:
            kicked = splitted[0]
            del splitted[0]
            print "[KICKED] "+nick+" kicked "+kicked+" from "+chan+" for "+(' '.join(splitted))+"!"


 
    def on_pubmsg(self, c, e):
        nick     = e.source.nick
        hostmask = e.source
        chan     = e.target
        msg      = ' '.join(e.arguments)
        splitted = e.arguments[0].split(' ')
        mynick   = c.get_nickname()
        print "("+chan+") <"+nick+"> "+msg
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

        nametest = re.search(mynick.lower()+"?", splitted[0].lower())
        if not nametest is None:
            try:
                del splitted[0]
                if msg.find("reload")!=-1:
                    self.reload_plugins(False)
                else:
                    for a,i in self.commands.iteritems():
                        if msg.find(a)!=-1:
                            i(c, e)
            except Exception, e:
                c.privmsg(chan,nick+": \x02\x0304Python error!\x02 "+str(e))

    def on_privmsg(self, c, e):
        nick     = e.source.nick
        hostmask = e.source
        chan     = e.target
        msg      = ' '.join(e.arguments)
        splitted = e.arguments[0].split(' ')
        mynick   = c.get_nickname()
        print "(PRIVATE) <"+nick+"> "+msg
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




def main():
    bot = TextSiri()
    bot.start()
 
if __name__ == "__main__":
    main()

