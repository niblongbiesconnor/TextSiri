#!/usr/bin/env python3

##########################
#                        #
#   TEXTSIRI NEO v1.0    #
#                        #
# Licensed under the MIT #
# license. Enjoy.        #
#                        #
##########################

# TextSiri.py = Main file.

import sys
import os
import subprocess
import irc.bot
import irc.buffer
import irc.connection
import requests
import threading
import time
import ssl
from utils import logger, botstrings, module_loader, json_parser


class TextSiri(irc.bot.SingleServerIRCBot):
    def __init__(self):
        logger.print_info("Welcome to TextSiri NEO.")
        logger.print_info("Starting engine, version {}".format(botstrings.VERSION))
        self.check_for_updates()
        logger.print_info("Starting config parser")
        logger.print_info("Config file is {}".format(botstrings.CONFIG_FILE))
        self.config = json_parser.JSONParser(botstrings.CONFIG_FILE)
        if self.config.is_empty:
            logger.print_warn("Config file is empty. Generating new config.")
            self.config["general"] = { # General bot settings.
                    "nickname": "TextSiri",
                    "realname": "Your digital assistant on IRC.",
                    "authmethod": "nickserv", # TODO add sasl method
                    "password": "",
                    "triggertype": "1", # Modes are: 1- Regexp, 2-Single char, 3-Text at the beginning of message. Any other will give a FATAL error.
                    "showmotd": True,
                    "trigger": "^{botnick}[^a-zA-Z0-9]\s(.+)" # Available replacements: {botnick} = Bot's nick.
            }
            self.config["server"] = { # Server settings.
                    "address": "irc.freenode.net",
                    "port": "6697",
                    "ssl": True
            }
            self.config["channels"] = [
                    {
                        "name": "#botters",
                        "key": "", # Leave empty for no key.
                        "joincommands": [] # MUST BE RFC2812 COMPLIANT!
                    }
            ]
            self.config["modules"] = {
                    # Space for module settings. Each module that needs a config should have its own dictionary with its own name here.
            }

            self.config.write()
            logger.print_warn("Config file is written.")
            logger.print_info("It looks like this is your first time running TextSiri NEO. Please edit {} in the current directory.".format(botstrings.CONFIG_FILE))
            sys.exit(1)
        else:
            logger.print_info("Config file successfully read.")
            server_info = self.config["server"]
            general_info = self.config["general"]
            logger.print_info("Attempting to connect to {} at port {} (SSL: {})".format(
                              server_info["address"], server_info["port"], "YES" if server_info["ssl"] else "NO"))
            if server_info["ssl"]:
                irc.bot.SingleServerIRCBot.__init__(self, [(server_info["address"], int(server_info["port"]))],
                                                    general_info["nickname"], general_info["realname"],
                                                    connect_factory=irc.connection.Factory(wrapper=ssl.wrap_socket))
            else:
                irc.bot.SingleServerIRCBot.__init__(self, [(server_info["address"], int(server_info["port"]))],
                                                    general_info["nickname"], general_info["realname"])
            self.connection.buffer_class = irc.buffer.LenientDecodingLineBuffer
            logger.print_info("Attempting to load modules.")
            self.modules = module_loader.load(self, logger, botstrings.MODULES_DIR)
            logger.print_info("Finished loading modules.")
            self.message_buffer = []
            self.message_counter = 0
            self.message_slowmode_lock = 0
            logger.print_info("Starting message sender.")
            self.msgThread = threading.Thread(target=self.message_loop, args=(self.connection,))
            self.msgThread.setDaemon(True)
            self.msgThread.start()
            logger.print_info("Started message sender.")
            logger.print_info("Reached Target Initialization.")

    def message_loop(self, c):
        sent_message = False
        while True:
            time.sleep(0.05)
            if len(self.message_buffer) > 0:
                if self.message_counter > 5:
                    self.message_slowmode_lock = 1
            if self.message_slowmode_lock:
                time.sleep(0.5)
            if len(self.message_buffer) > 0:
                command = self.message_buffer.pop(0)
                command_name = command.pop(0)
                try:
                    getattr(c, command_name)(command.pop(0), *command)
                    sent_message = True
                except Exception as e:
                    logger.print_error(str(e))
            if sent_message:
                self.message_counter += 1
            else:
                self.message_counter -= 1
                if self.message_counter == 0:
                    self.message_slowmode_lock = 0

    def check_for_updates(self):
        check_url = "https://raw.githubusercontent.com/mission712/TextSiri/master/VERSION"
        ver = requests.get(check_url)
        if ver.status_code != 200:
            logger.print_warn("Couldn't check version.")
            return
        local_version = botstrings.VERSION.split(".")
        remote_version = ver.text.split(".")
        for i in range(1, len(local_version)):
            if int(remote_version[i]) > int(local_version[i]):
                logger.print_info("{color_green}New bot version found! Pass --upgrade to upgrade TextSiri at startup.")

    def update_bot(): # we won't call this function from inside the bot
        # Assuming you are inside the TextSiri git repository (you should be.)
        try:
            subprocess.check_output(["git", "fetch"])
            subprocess.check_output(["git", "pull"])
        except FileNotFoundError:
            logger.print_error("You must have git installed!")
            exit(1)
        logger.print_info("Updated TextSiri, restarting.")
        python = sys.executable
        sys.argv.remove("--upgrade")
        os.execl(python, python, * sys.argv)


if __name__ == "__main__":
    if "--upgrade" in sys.argv:
        TextSiri.update_bot()
    else:
        Instance = TextSiri()
        try:
            Instance.start()
        except KeyboardInterrupt:
            Instance.die("Ctrl+C from terminal.")
            sys.exit(0)
        except Exception as e:
            logger.print_error(type(e).__name__+str(e))
