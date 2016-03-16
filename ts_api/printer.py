# -*- coding: utf-8 -*-

import time

def print_info(message):
    print("[{}] [INFO] {}".format(time.strftime("%y-%m-%d %H:%M:%S"), message))

def print_warn(message):
    print("[{}] [WARN] {}".format(time.strftime("%y-%m-%d %H:%M:%S"), message))

def print_error(message):
    print("[{}] [ERROR] {}".format(time.strftime("%y-%m-%d %H:%M:%S"), message))

def print_fatal(message):
    print("[{}] [FATAL] {}".format(time.strftime("%y-%m-%d %H:%M:%S"), message))

def print_custom(message, prefix):
    print("[{}] [{}] {}".format(time.strftime("%y-%m-%d %H:%M:%S"), prefix, message))

