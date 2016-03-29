# -*- coding: utf-8 -*-

import irc.bot
import sys
import os
import time
import re
import random
import traceback
import threading
from pprint import pprint
from ts_api.printer import *
from ts_api.parsejson import *
from ts_api.botstrings import *
from ts_api.moduleloader import *

class TextSiri(irc.bot.SingleServerIRCBot):
    def __init__(self):
        print_info("Welcome to {} {}!".format(BOTNAME, VERSION), )
        print_info("Reading config file at \"{}\"...".format(str(os.path.join(os.getcwd(), "config.cfg"))))
        self.config = ParseJSON("config.cfg")
        if self.config["config"] == {}:
            print_warn("Config file at {} is empty!".format(str(os.path.join(os.getcwd(), "config.cfg"))))
            self.config['config'] = {
                "general": { # General bot settings.
                    "nickname": "TextSiri",
                    "realname": "Your digital assistant on IRC.",
                    "authmethod": "nickserv", # TODO add sasl method
                    "password": "",
                    "triggertype": "1", # Modes are: 1- Regexp, 2-Single char, 3-Text at the beginning of message. Any other will give a FATAL error.
                    "trigger": "^{botnick}[^a-zA-Z0-9]\s?" # Available replacements: {botnick} = Bot's nick.
                },
                "server": { # Server settings.
                    "address": "irc.freenode.net",
                    "port": "6667" # TODO add ssl support
                },
                "channels": [
                    {
                        "name": "#botters",
                        "key": "", # Leave empty for no key.
                        "joincommands": [] # MUST BE RFC2812 COMPLIANT!
                    }
                ],
                "modules": {
                    # Space for module settings. Each module that needs a config should have its own dictionary with its own name here.
                }
            }
            print_info("Writing sample info to config file...")
            self.config.write()
            print_info("Config file is written. Closing filestream.")
            self.config.close()
            print_info("Hi! It seems like this is the first time you are using {}. Please edit \"config.cfg\" found in \"{}\" and restart this bot.".format(BOTNAME, str(os.getcwd())))
            sys.exit(0)
        else:
            print_info("---------- PRE-INITIALIZATION ----------")
            print_info("Config file loading complete. Loading modules...")
            self.info = {
                "about": {},
                "triggers": {},
                "command_help": {},
                "hooks": {
                    "join": [],
                    "part": [],
                    "pubmsg": [],
                    "privmsg": [],
                    "pubnotice": [],
                    "privnotice": [],
                    "action": [],
                    "nick": [],
                    "quit": [],
                    "kick": [],
                    "mode": []
                },
                "hostmasks": {},
                "message_buffer": [],
                "bot_instance": self
            }
            load_all_modules("modules", self.info, self.config)
            print_info("------------ INITIALIZATION ------------")
            print_custom("Connecting to {} on port {}...".format(self.config["config"]["server"]["address"], self.config["config"]["server"]["port"]), "conn")
            irc.bot.SingleServerIRCBot.__init__(self, [(self.config["config"]["server"]["address"], int(self.config["config"]["server"]["port"]))], self.config["config"]["general"]["nickname"], self.config["config"]["general"]["realname"])
            self.connection.buffer_class = irc.buffer.LenientDecodingLineBuffer
            print_info("Starting message sender...")
            self.message_counter = 0
            self.message_slowmode_lock = 0
            self.msgThread = threading.Thread(target=self.msgLoop, args=(self.connection,))
            self.msgThread.setDaemon(True)
            self.msgThread.start()
            # Jumps from here to on_welcome

    # When the bot's selected nickname is already used.
    def on_nicknameinuse(self, c, e):
        print_warn("Nickname {} is already in use! Retrying with {}_...".format(c.get_nickname(), c.get_nickname()))
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        print_custom("Successfully connected to server.", "conn")
        if self.config["config"]["general"]["authmethod"] == "nickserv" and self.config["config"]["general"]["password"] != "":
            print_info("Attempting to identify via NickServ...")
            c.privmsg("NickServ", "IDENTIFY {}".format(self.config["config"]["general"]["password"]))
        print_info("---------- POSTINITIALIZATION ----------")
        print_info("Waiting for authentication to join channels.")

    def join_chans(self, c, e):
        print_info("Sending server connection to module instances...")
        for module in self.info["about"].keys():
            self.info["about"][module]["instance"].get_connection(c)
        print_info("Joining channels...")
        for channel in self.config["config"]["channels"]:
            print_info("|---- Joining {}...".format(channel["name"]))
            c.join(channel["name"], channel["key"])
            print_info("| |---- Sending WHO to {}".format(channel["name"]))
            c.who(channel["name"])
            if channel["joincommands"] != []:
                print_info("| |---- Issuing join commands on {}...".format(channel["name"]))
                for command in channel["joincommands"]:
                    c.send_raw(command)
        print_info("Joining channels complete.")
        print_info("--------------- BOT READY ---------------")

    """Logging and other miscallenous shit"""

    def on_kick(self, c, e):
        for those in self.info["hooks"]["kick"]:
            self.info["about"][those]["instance"].respond_hook(e, "kick")
        if e.arguments[0] != c.get_nickname():
           self.info["hostmasks"][e.source.nick] = e.source
           print("[{}] [\x1b[31mKICK\x1b[0m] {} was kicked by {} on {} ({})".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(e.arguments[0]) + e.arguments[0] + "\x1b[0m", self.gen_color_for_nick(e.source.nick) + e.source.nick + "\x1b[0m", e.target, e.arguments[1]))
        else:
           print("[{}] [\x1b[31;1mKICK\x1b[0m] I was kicked by {} on {}! ({})".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(e.source.nick) + e.source.nick + "\x1b[0m", e.target, e.arguments[1]))

    def on_join(self, c, e):
        # send the message to hooked modules
        for those in self.info["hooks"]["join"]:
            self.info["about"][those]["instance"].respond_hook(e, "join")
        if e.source.nick != c.get_nickname():
           self.info["hostmasks"][e.source.nick] = e.source
           print("[{}] [\x1b[32mJOIN\x1b[0m] {} joined {}".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(e.source.nick) + e.source.nick + "\x1b[0m", e.target))


    def on_part(self, c, e):
        # relay the msg to hooked modules
        for those in self.info["hooks"]["part"]:
            self.info["about"][those]["instance"].respond_hook(e, "part")
        if e.source.nick != c.get_nickname():
           self.info["hostmasks"][e.source.nick] = e.source
           print("[{}] [\x1b[31mPART\x1b[0m] {} parted from {} ({})".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(e.source.nick) + e.source.nick + "\x1b[0m", e.target, "".join(e.arguments)))
        
    def on_quit(self, c, e):
        # relay the msg to hooked modules
        for those in self.info["hooks"]["quit"]:
            self.info["about"][those]["instance"].respond_hook(e, "quit")
        if e.source.nick != c.get_nickname():
           self.info["hostmasks"][e.source.nick] = e.source
           print("[{}] [\x1b[30;1mQUIT\x1b[0m] {} quit ({})".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(e.source.nick) + e.source.nick + "\x1b[0m", "".join(e.arguments)))
 
    def on_nick(self, c, e):
        # relay the msg to hooked modules
        for those in self.info["hooks"]["nick"]:
            self.info["about"][those]["instance"].respond_hook(e, "nick")
        if e.source.nick != c.get_nickname():
           self.info["hostmasks"][e.target] = self.info["hostmasks"][e.source.nick]
           del self.info["hostmasks"][e.source.nick]
           print("[{}] [\x1b[34;1mNICK\x1b[0m] {} changed nick to {}".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(e.source.nick) + e.source.nick + "\x1b[0m", self.gen_color_for_nick(e.target) + e.target + "\x1b[0m"))

    # When we get a reply from the WHO issued above
    def on_whoreply(self, c, e):
        try:
            chan, username, hostmask, server, nick, HereOrGone, realname = e.arguments
        except ValueError:
            print_error("A user had an unparsable whois return.")
            return ""
        self.info["hostmasks"][nick] = "{}!{}@{}".format(nick, username, hostmask)
    

    def process_message(self, c, e, return_type):
        nick     = e.source.nick
        chan     = e.target
        msg      = ' '.join(e.arguments)
        splitted = e.arguments[0].split(' ')
        mynick   = c.get_nickname()
        for regex in self.info["triggers"].keys():
            if not re.compile(regex).search(msg) is None:
                try:
                    returned = self.info["about"][self.info["triggers"][regex]]["instance"].respond(e)
                except Exception as err:
                    returned = "\x02\x0304Python error!\x0F {}.".format(err)
                if not returned:
                    break
                else:
                    if type(returned) is list:
                        for message in returned:
                            self.info["message_buffer"].append([e.target if return_type == "channel" else e.source.nick, message])
                    else:
                        self.info["message_buffer"].append([e.target if return_type == "channel" else e.source.nick, returned])
                    break

    def msgLoop(self, c):
        while True:
            time.sleep(0.01)
            if len(self.info["message_buffer"]):
                lst = self.info["message_buffer"].pop(0)
                if len("PRIVMSG {} :{}".format(lst[0],lst[1])) > 302:
                    lst[1] = lst[1][:302 - (len("PRIVMSG {} :".format(lst[0])) + len("... (truncated)")-2)] + "\x02... (truncated)\x02"
                    c.privmsg(lst[0],lst[1])
                else:
                    c.privmsg(lst[0],lst[1])
                self.message_counter += 1
            if self.message_counter > 9:
                if self.message_slowmode_lock == 0:
                    self.message_slowmode_lock = 1
            if self.message_slowmode_lock == 1 and self.message_counter > 0:
                time.sleep(1)
                self.message_counter -= 1
            if self.message_counter == 0:
                if self.message_slowmode_lock == 1:
                    self.message_slowmode_lock = 0


    def on_privnotice(self, c, e):
        sender = e.source.nick
        msg = ' '.join(e.arguments)
        splitted = e.arguments[0].split(' ')
        mynick   = c.get_nickname()
        print(self.replace_colors("[{}] [\x1b[34mNOTICE\x1b[0m] <{}> {}".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(sender) + sender + '\x1b[0m', decode(msg))))
        if sender == "NickServ" and msg.find(" now ") != -1:
            self.join_chans(c, e)
        self.process_message(c, e, "notice")

    def on_pubmsg(self, c, e):
        for those in self.info["hooks"]["pubmsg"]:
            self.info["about"][those]["instance"].respond_hook(e, "pubmsg")
        sender = e.source.nick
        msg = ' '.join(e.arguments)
        splitted = e.arguments[0].split(' ')
        mynick   = c.get_nickname()
        print(self.replace_colors("[{}] [\x1b[32mCHAN\x1b[0m] ({}) <{}> {}".format(time.strftime("%y-%m-%d %H:%M:%S"), e.target, self.gen_color_for_nick(sender) + sender + '\x1b[0m', decode(msg))))
        if self.config["config"]["general"]["triggertype"] == "1":
            if not re.compile(self.config["config"]["general"]["trigger"].format(botnick=mynick).lower()).search(splitted[0].lower()) is None and sender != mynick:
                if "&&" in splitted:
                    for command in e.arguments[0].split(" && "):
                        e.arguments[0] = command
                        self.process_message(c, e, "channel")
                else:     
                    self.process_message(c, e, "channel")
        elif self.config["config"]["general"]["triggertype"] == "2":
            if msg[:1] == self.config["config"]["general"]["trigger"][:1] and sender != mynick:
                if "&&" in splitted:
                   for command in e.arguments[0].split(" && "):
                       e.arguments[0] = command
                       self.process_message(c, e, "channel")
                else:
                    self.process_message(c, e, "channel")
        elif self.config["config"]["general"]["triggertype"] == "3":
            if msg.startswith(self.config["config"]["general"]["trigger"]) and sender != mynick:
                if "&&" in splitted:
                   for command in e.arguments[0].split(" && "):
                       e.arguments[0] = command
                       self.process_message(c, e, "channel")
                else:
                    self.process_message(c, e, "channel")


    # ANSI colors for color replacement. Damn you Windows and your not supporting of any standards.
    ansi_colors = {
        '\x030': '\x1b[37;1m',
        '\x031': '\x1b[30m',
        '\x032': '\x1b[34m',
        '\x033': '\x1b[32m',
        '\x034': '\x1b[31m',
        '\x035': '\x1b[31;1m',
        '\x036': '\x1b[35m',
        '\x037': '\x1b[33m',
        '\x038': '\x1b[33;1m',
        '\x039': '\x1b[32;1m',
        '\x0310': '\x1b[36m',
        '\x0311': '\x1b[36;1m',
        '\x0312': '\x1b[34;1m',
        '\x0313': '\x1b[35;1m',
        '\x0314': '\x1b[30;1m',
        '\x0315': '\x1b[30;1m',
        '\x0F': '\x1b[0m'
    }

    def on_privmsg(self, c, e):
        sender = e.source.nick
        msg = ' '.join(e.arguments)
        splitted = e.arguments[0].split(' ')
        mynick   = c.get_nickname()
        print(self.replace_colors("[{}] [\x1b[33mPRIV\x1b[0m] <{}> {}".format(time.strftime("%y-%m-%d %H:%M:%S"), self.gen_color_for_nick(sender) + sender + '\x1b[0m', decode(msg))))
        if "&&" in splitted:
            for command in e.arguments[0].split(" && "):
                 e.arguments[0] = command
                 self.process_message(c, e, "private")
        else:     
            self.process_message(c, e, "private")
    
    def replace_colors(self, message):
        for irc in self.ansi_colors.keys():
            message = message.replace(irc, self.ansi_colors[irc])
        return '\x1b[0m' + message

    def gen_color_for_nick(self, nick):
        sum = 0
        for char in nick:
            sum += ord(char)
        return list(self.ansi_colors.values())[sum%15 + 1]
    
    def handle_interrupt(self):
        self.die("CTRL+C from terminal!")




if __name__ == '__main__':
    bot = TextSiri()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.handle_interrupt()
    except UnicodeDecodeError:
        print_error("Couldn't print 1 line so it was ignored.")
        pass
