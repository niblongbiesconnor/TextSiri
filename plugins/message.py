#!/usr/bin/python2.7
#-*- coding: UTF-8 -*-

def main():
    return {'anonymous message': anonmsg, 'message': msg}

def anonmsg(c,e):
    nick     = e.source.nick
    hostmask = e.source
    chan     = e.target
    msg      = ' '.join(e.arguments)
    splitted = e.arguments[0].split(' ')
    mynick   = c.get_nickname()
    del splitted[0]
    del splitted[0]
    receiver = splitted[0]
    del splitted[0]
    message = ' '.join(splitted)
    if receiver[:1]!='#':
        c.notice(nick, 'Your message will be delivered to '+receiver+' if they\'re online.')
        c.privmsg(receiver, 'You\'ve got an anonymous message as follows:')
        c.privmsg(receiver, message)
    else:
        c.notice(nick,'You can\'t message channels.')

def msg(c,e):
    nick     = e.source.nick
    hostmask = e.source
    chan     = e.target
    msg      = ' '.join(e.arguments)
    splitted = e.arguments[0].split(' ')
    mynick   = c.get_nickname()
    del splitted[0]
    receiver = splitted[0]
    del splitted[0]
    message = ' '.join(splitted)
    if receiver[:1]!='#':
        c.notice(nick, 'Your message will be delivered to '+receiver+' if they\'re online.')
        c.privmsg(receiver, 'You\'ve got an message from '+nick+' as follows:')
        c.privmsg(receiver, message)
    else:
        c.notice(nick,'You can\'t message channels.')