#!/usr/bin/env python3

##########################
#                        #
#   TEXTSIRI NEO v1.0    #
#                        #
# Licensed under the MIT #
# license. Enjoy.        #
#                        #
##########################

# utils/logger.py = Logs to the screen.

import datetime

ansi_colors = {
        "color_bold": "\x1b[1m",
        "color_black": "\x1b[30m",
        "color_red": "\x1b[31m",
        "color_green": "\x1b[32m",
        "color_yellow": "\x1b[33m",
        "color_blue": "\x1b[34m",
        "color_magenta": "\x1b[35m",
        "color_cyan": "\x1b[36m",
        "color_white": "\x1b[37m",
        "color_blackbg": "\x1b[40m",
        "color_redbg": "\x1b[41m",
        "color_greenbg": "\x1b[42m",
        "color_yellowbg": "\x1b[43m",
        "color_bluebg": "\x1b[44m",
        "color_magentabg": "\x1b[45m",
        "color_cyanbg": "\x1b[46m",
        "color_whitebg": "\x1b[47m",
        "color_clear": "\x1b[0m"
}

def print_custom(text, source):
    print("[{}] [{}] {}{color_clear}".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), source.format(**ansi_colors), text.format(**ansi_colors), **ansi_colors))

def print_info(text):
    print_custom(text, " {color_green}{color_bold}INFO{color_clear} ")

def print_warn(text):
    print_custom("{color_yellow}"+text, " {color_yellow}{color_bold}WARN{color_clear} ")

def print_error(text):
    print_custom("{color_red}"+text, "{color_red}{color_bold}FAILED{color_clear}")

def print_serv(text):
    print_custom("{color_cyan}"+text, " {color_magenta}{color_bold}SERV{color_clear} ")
