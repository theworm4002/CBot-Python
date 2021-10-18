#!/usr/bin/python3
#
#

import os
import sys
import ssl
import time
import socket
import logging
import datetime
from config import *
from requests import get  
starttime = datetime.datetime.utcnow() # To calculate uptime.
ip = get('https://api.ipify.org').text

dirName = os.path.dirname(os.path.abspath(__file__))
logname = f'{dirName}/Py_CBot.log'
#handlers = [logging.FileHandler(logname), logging.StreamHandler()]
handlers = [logging.FileHandler(logname)]
logging.basicConfig(
				handlers=handlers,
				level=logging.DEBUG,
				format='%(asctime)s %(levelname)s - %(message)s',
				datefmt='%Y-%m-%d %H:%M:%S'
			)

log = logging.getLogger() 

lastping = time.time() # Time at last PING.
threshold = 200 # Ping timeout before reconnecting.
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Set ircsock

if usessl: # If SSL is True, connect using SSL.
    ircsock = ssl.wrap_socket(ircsock)
ircsock.settimeout(240) # Set socket timeout.
connected = False 


# New Decode  most IRC is utf-8 but the older ones vary... this probably  could be done better but it will do#
def decode(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('latin1')
        except UnicodeDecodeError:
            try:
                text = bytes.decode('iso-8859-1')
            except UnicodeDecodeError:
                text = bytes.decode('cp1252')			
    return text


def ircsend(msg):
    ircsock.send(bytes(f'{str(msg)} \r\n', 'UTF-8')) # Send data to IRC server.
    if debugmode:
        print(f'Sending to Server: {msg}')


def connect():
    global connected

    while not connected:
        try: # Try and connect to the IRC server.
            if debugmode: 
                print(f'Connecting to {str(server)}:{str(port)}')
            ircsock.connect_ex((server, port)) # Connect to the server.
            if usesasl:
                ircsend('CAP REQ :sasl') # Request SASL Authentication.
                if debugmode:
                    print('Requesting SASL login.')
            if useServPass: # If useServPass is True, send serverPass to server to connect.
                ircsend('PASS '+ serverPass) 
                if debugmode:
                    print('Requesting PASS login.')
            ircsend(f'USER {botIdent} * * :{botRealname}') #Command: USER Parameters: <user> <mode> <unused> <realname>
            ircsend('NICK ' + botNick)
            connected = True
            main()

        except Exception as iconnex: 
            if debugmode:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]             
                print(f'Exception: {str(iconnex)}')
                print(f'Failed to connect to {str(server)}:{str(port)}. Retrying in 10 seconds...')
            logging.exception('\n\n\n =========================    --ERROR--    =======================================================================================================================================================================================================================================================================================================================\n ')
            connected = False
            time.sleep(10)
            reconnect()

def reconnect():
    global connected # Set 'connected' variable
    global ircsock # Set 'ircsock' variable

    while not connected:
        ircsock.close() # Close previous socket.
        ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Set ircsock variable.
        if usessl: # If SSL is True, connect using SSL.
            ircsock = ssl.wrap_socket(ircsock) 

        try:
            if debugmode: 
                print(f'Reconnecting to {str(server)} : {str(port)}')
            ircsock.connect_ex((server, port)) # Connect to the server.
            if usesasl:
                ircsend('CAP REQ :sasl') # Request SASL Authentication.
                if debugmode:
                    print('Requesting SASL login.')            
            if useServPass: # If useServPass is True, send serverPass to server to connect.
                ircsend('PASS '+ serverPass) 
            ircsend(f'USER {botIdent} * * :{botRealname}')
            ircsend('NICK ' + botNick)
            connected = True
            main()

        except Exception as iconnex: 
            if debugmode:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]  
                print('Exception: ' + str(iconnex))
                print('Failed to connect to ' + str(server) + ':' + str(port) + '. Retrying in 10 seconds...')
            logging.exception('\n\n\n =========================    --ERROR--    =======================================================================================================================================================================================================================================================================================================================\n ')
            connected = False
            time.sleep(10)
            reconnect()


def joinchan(chan): # Join channel(s).
    ircsend('JOIN '+ chan)
    
def partchan(chan): # Part channel(s).
    ircsend('PART '+ chan)            

def pjchan(chan): # Part then Join channel(s) 
    ircsend('PART '+ chan)
    ircsend('JOIN '+ chan)     

def newnick(newnick): # Change botNick.
    ircsend('NICK '+ newnick)  

def sendmsg(msg, target=botChannel): # Sends messages to the target.
    ircsend('PRIVMSG '+ target +' :'+ msg)    

def sendntc(ntc, target=botChannel): # Sends a NOTICE to the target.
    ircsend('NOTICE '+ target +' :'+ ntc)       

def sendversion(nick, ver): # Respond to VERSION request.
    ver = 'VERSION ' + software + ' ' + version 
    sendntc(ver, nick)          

def uptime(): # Used to get current uptime for .uptime command
    delta = datetime.timedelta(seconds=round((datetime.datetime.utcnow() - starttime).total_seconds()))
    return delta  

def setmode(flag, target=botChannel): # Sets given mode to nick or channel.
    ircsend('MODE '+ target +' '+ flag)
   


########
# MAIN #
######################################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################################

def main():
    global connected
    global botNick
    global ip
    global lastping
                         
    while connected:
        try: ircmsg = ircsock.recv(4096) # IrcV3 
        except: ircmsg = ircsock.recv(2048)

        ircmsg = decode(ircmsg)
        ircmsg = ircmsg.strip('\n\r')

        if debugmode: # If debugmode is True, bot & server msgs will print to screen.
            print(ircmsg) 
        
        # CAP (IRCv3).
        if ircmsg.find(' CAP * LS :') != -1:
            print('finish this you ass hat')
            
        # SASL Authentication.
        if ircmsg.find('ACK :sasl') != -1:
            if usesasl:
                if debugmode:
                    print('Authenticating with SASL PLAIN.') # Request PLAIN Auth.
                ircsend('AUTHENTICATE PLAIN')

        if ircmsg.find('AUTHENTICATE +') != -1:
            if usesasl:
                if debugmode:
                    print('Sending %s Password: %s to SASL.' % (nickserv, botNsPass))
                authpass = botNick + '\x00' + botNick + '\x00' + botNsPass
                ap_encoded = str(base64.b64encode(authpass.encode('UTF-8')), 'UTF-8')
                ircsend('AUTHENTICATE ' + ap_encoded) # Authenticate with SASL.

        if ircmsg.find('SASL authentication successful') != -1:
            if usesasl:
                if debugmode:
                    print('Sending CAP END command.')
                ircsend('CAP END') # End the SASL Authentication.
        
        # Wait 30 seconds and try to reconnect if 'too many connections from this IP'
        if ircmsg.find('Too many connections from your IP') != -1:
            if debugmode: 
                print('Too many connections from this IP! Reconnecting in 30 seconds...')
            connected = False
            time.sleep(30)
            reconnect()
        
        # Change nickname if current nickname is already in use.
        if ircmsg.find('Nickname is already in use') != -1:
            botNick = 'abot' + str(random.randint(10000,99999))
            newnick(botNick)

        # Join 'channel' and msg 'admin' after getting an invite  https://sopel.chat/appendix/formatting/
        if ircmsg.find('INVITE') != -1:             
            if ircmsg.find(adminName) != -1 and ircmsg.find('INVITE') != -1:
                #if message.split(' ', 1)[1].startswith('#'):
                    target = ircmsg.split('INVITE',1)[1].split(':',1)[1]
                    message = 'Ok, I will join the channel: ' + target
                    joinchan(target)
                    sendntc(message, adminName)
                
        # Respond to CTCP VERSION
        if ircmsg.find('VERSION') != -1:
            print(ircmsg)
            name = ircmsg.split('!',1)[0][1:]
            if name.lower() != adminName.lower():
                log.info(ircmsg)            
                vers = version            
                sendversion(name, vers)

#------------
# If TOPIC /
#-------------------------------------                                     
        #if ircmsg.find('TOPIC #channel :') != -1:
        #    name = ircmsg.split('!',1)[0][1:]
        #    message = ircmsg.split('TOPIC',1)[1].split(':',1)[1]
                
#------------
# If JOIN /
#-------------------------------------
        #if ircmsg.find('JOIN :') != -1:            
        #    name = ircmsg.split('!',1)[0][1:]
        #    chnl = ircmsg.split('JOIN',1)[1].split(':',1)[1] 

#------------
# If Notice /
#-------------------------------------

        if ircmsg.find(' NOTICE ') != -1:
            try:
                name = ircmsg.split('!',1)[0][1:]
                message = ircmsg.split('NOTICE',1)[1].split(':',1)[1]
            except: print('Cant split msg')
            
            if message.find('*** You are connected') != -1:
                sendmsg('IDENTIFY %s' % botNsPass, nickserv)
                joinchan(botChannel)
                sendntc(format(ip) + ' Online!', adminName)

            if message.find('This nickname is registered and protected.') != -1:
                sendmsg('IDENTIFY %s' % botNsPass, nickserv)
                
            if (
                   message.find('*** ') != -1 and message.find('did a /whois on you') != -1 and
                   ircmsg.lower().find(':{}!'.format(adminName.lower())) == -1         
                ):  #Only works if IRCOper with flag set 
                sendntc(ircmsg, adminName2)   
                
#------------
# If PRIV  /
#-------------------------------------         
        if ircmsg.find(' PRIVMSG ') != -1:
            try:
                name = ircmsg.split('!',1)[0][1:]
                message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
            except: print('Cant split msg')

            # IRC Nicks are normally less than 17 characters long.
            if len(name) < 17:

                # Respond to the CTCP 
                if ircmsg.find('') != -1:
                    message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
                    target = ircmsg.split('PRIVMSG',1)[1].split(' :',1)[0].split(' ', 1)[1]

                    if ircmsg.lower().find('source') != -1:
                        msg = 'Your mom gave me this shit.'
                        sendntc(msg, name)

                    if ircmsg.lower().find('finger') != -1:
                        msg = 'Riding that 2 knuckle pony are you?'
                        sendntc(msg, name)

                # Respond to '.msg [target] [message]' command from admin.
                if name.lower() == adminName.lower() and message[:5].find('.msg') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                    else:
                        target = name
                        message = 'Could not parse. The message should be in format of ".msg [target] [message]" to work properly.'
                    sendmsg(message, target)

                # Respond to '.act [target] [message]' command from admin.
                if name.lower() == adminName.lower() and message[:5].find('.act') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                        msg = f'\x01ACTION {message}\x01'
                        sendmsg(msg, target)
                    else:
                        target = name
                        message = 'Could not parse. The message should be in format of ".act [target] [message]" to work properly.'
                        sendmsg(message, target)

                # Respond to '.ntc [target] [message]' command from admin.
                if name.lower() == adminName.lower() and message[:5].find('.ntc') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        message = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                    else:
                        target = name
                        message = 'Could not parse. The message should be in the format of ".msg [target] [message]" to work properly.'
                    sendntc(message, target)
                
                # Respond to '.kick [channel] [nick] [reason]' command from admin.
                if name.lower() == adminName.lower() and message[:5].find('.kick') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        reason = target.split(' ', 2)[2]
                        nick = target.split(' ')[1]
                        chnl = target.split(' ')[0]
                        message = nick + ' was kicked from ' + chnl + ' Reason:' + reason
                        kick(reason, nick, chnl)
                    else:
                        message = 'Could not parse. The message should be in the format of ".kick [#channel] [nick] [reason]" to work properly.'
                    sendntc(message, name)
                
                # Respond to the '.mode [target] [mode]' command from admin.
                if name.lower() == adminName.lower() and message[:5].find('.mode') != -1:
                    target = message.split(' ', 1)[1]
                    if target.find(' ') != -1:
                        mode = target.split(' ', 1)[1]
                        target = target.split(' ')[0]
                        message = 'Setting mode ' + mode + ' on ' + target + '!'
                        setmode(mode, target)
                    else:
                        message = 'Could not parse. The message should be in the format of ".mode [target] [mode]" to work properly.'
                    sendntc(message, adminName)
                
                # Respond to '.uptime' command from admin.
                if name.lower() == adminName.lower() and message.find('.uptime') != -1:
                    sendntc('My current uptime: ' + format(uptime()), name)

        else:
            if ircmsg.find('PING') != -1: # Reply to PINGs.
                nospoof = ircmsg.split(' ', 1)[1] # Unrealircd 'nospoof' compatibility.
                ircsend('PONG ' + nospoof)
                lastping = time.time() # Set time of last PING.
                if (time.time() - lastping) >= threshold: # If last PING was longer than set threshold, try and reconnect.
                    if debugmode: 
                        print('PING time exceeded threshold')
                    connected = False
                    reconnect()
                
            if not ircmsg: # If no response from server, try and reconnect.
                if debugmode: 
                    print('Disconnected from server')
                connected = False
                reconnect()

try: # Here is where we actually start the Bot.
    if not connected:
        connect() # Connect to server.
    
except KeyboardInterrupt: # Kill Bot from CLI using CTRL+C
    ircsend('QUIT Going off to die')
    if debugmode: 
        print('... Going off to die')
    sys.exit()




