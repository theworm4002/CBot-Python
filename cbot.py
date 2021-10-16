#!/usr/bin/python

NICK = "CBot"
ALT = "CBot-"
IDENT = "CBot"
REALNAME = "CBot"
SERVER = "irc.technet.xi.ht"
PORT = 6667
CHANNEL = "#test"

import socket
import sys
import string
import time

sockChan = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sockChan.connect((SERVER, PORT))
sockChan.send('NICK CBot\r\n'.encode('UTF-8'))
sockChan.send('USER CBot * * :CBot\r\n'.encode('UTF-8'))

while 1: 
    text = sockChan.recv(2040)
    print(text)
    foo = text.split()
    if 'PING' in foo[0]:
        sockChan.send("PONG " + foo[1] + "\r\n")
    elif '001' in foo[1]:
        sockChan.send("JOIN " + CHANNEL + "\r\n")
    elif '433' in foo[1]:
        sockChan.send("NICK " + ALT + "\r\n")
