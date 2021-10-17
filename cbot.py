#!/usr/bin/python

from config import *

import socket
import sys
import string
import time

sockChan = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sockChan.connect((BSERVER, BPORT))
sockChan.send('NICK ' + BNICK + '\r\n'.encode('UTF-8'))
sockChan.send('USER ' + BREALNAME +  ' * * :' + BIDENT + '\r\n'.encode('UTF-8'))

while 1: 
    line = sockChan.recv(2040)
    print(line)
    lline = line.split()
    if 'PING' in lline[0]:
        sockChan.send("PONG " + lline[1] + "\r\n")
    if '001' in lline[1]:
        sockChan.send("JOIN " + BCHANNEL + "\r\n")
       # sockChan.send("PRIVMSG NICKSERV :IDENTIFY " + BPASSWORD + "\r\n")
    if '433' in lline[1]:
        sockChan.send("NICK " + BALT + "\r\n")
    if 'PRIVMSG' in lline[1]:
      if '!quit' in lline[3]:
         sockChan.send("QUIT \r\n")
      if '!join' in lline[3]:
        sockChan.send("JOIN " + lline[4] + "\r\n")
      if '!part' in lline[3]:
        sockChan.send("PART " + lline[4] + "\r\n")
