BNICK  = 'CBot'

BIDENT = 'CBot'

BNAME  = 'CBot'

ADMIN  = 'Your-nick'

BHOST  = 'irc.address.org

BPORT  = '+6697'

#####

import socket

import tls

import string

  sockChan = socket.socket()

  if PORT[0][0] == "+": 

    sockChan = ssl.wrap_socket(s)

  

  sockChan.connect((BHOST, BPORT))

  sockChan.send('NICK',BNICK)

  sockChan.send('USER',BIDENT,BNAME))

  while 1:

     text = sockChan.recv(1024)

     text = string.split(text)

     

     if text.find('PING') == [0]:

      sockChan.send('PONG',text[1])

      
