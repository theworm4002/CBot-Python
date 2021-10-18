#!/usr/bin/python




import sys
import time
import socket
import string

from config import *

debugmode = True

sockChan = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockChan.connect_ex((BotServer, BotPort))

sendIRC(f'USER {BotIdent} * * :{BotRealName}') #Command: USER Parameters: <user> <mode> <unused> <realname>
sendIRC('NICK ' + BotNick)
connected = True

while connected: 
    line = sockChan.recv(2040).decode('utf-8')

    print(line)
    
    if line != "":
        lline = line.split()
        if 'PING' in lline[0]:
            sendIRC("PONG " + lline[1] )
        if '001' in lline[1]:
            sockChan.send(bytes("JOIN " + BotChannel )
           # sockChan.send("PRIVMSG NICKSERV :IDENTIFY " + BPASSWORD + "\r\n")
        if '433' in lline[1]:
            sockChan.send(bytes("NICK " + BotAlt )
        if 'PRIVMSG' in lline[1]:
          if '!quit' in lline[3]:
             sockChan.send(bytes("QUIT")
          if '!join' in lline[3]:
            sockChan.send(bytes("JOIN " + lline[4] )
          if '!part' in lline[3]:
            sockChan.send(bytes("PART " + lline[4] )
 #if lline.find('PING') != -1:
