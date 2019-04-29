#
# freemother 1.0 03/2018
#
from websocket_server import WebsocketServer
import logging
import json
import datetime
import time
import subprocess

PORT=80
HOST='10.29.4.156'
mac='MO0004A3FFB99D'
xmac='MO0004A3F90000' ###change here
cookieName=['one','two','three','four']
cookieNode=['6FEC200D','AA81082C','206B121A','65EB0E1C'] ##change here

fase=0
sleep_state=0
cl_mother=''
cl0=''

msg_1='{"body": {"token": "hn3mnbvzkdd1pqlbzp70la81okvzlpbn"}, "resource": "login", "method": "get"}'
msg_2='{"body": {"status": 200}, "resource": "login", "method": "post"}'
msg_3='Asking for registration state'
msg_3a='{"body": 1, "type": "gateway", "resource": "registration", "method": "post", "auth": "'+mac+'"}'
msg_4='{"body": {"stateFrequency": 180, "smileLed": "255,0,0", "serverUrl": "in.sen.se", "rightLed": "60,100,240", "rfPower": 100, "leftLed": "60,100,240", "serverPort": 80, "maxConn": 24, "soundLevel": 75}, "type": "gateway", "resource": "state", "method": "post", "auth": "'+mac+'"}'
msg_5='{"body": {"version": 103, "collection": []}, "type": "gateway", "resource": "library/resident", "method": "post", "auth": "'+mac+'"}'
msg_6='{"body": {"version": 102, "collection": []}, "type": "gateway", "resource": "library/sound", "method": "post", "auth": "'+mac+'"}'
msgup='\n' #0x0a 

msgsleep='{"body": 1, "type": "gateway", "resource": "mute", "method": "post", "auth": "'+mac+'"}'
msgwakeup='{"body": 0, "type": "gateway", "resource": "mute", "method": "post", "auth": "'+mac+'"}'
'''# {"body": 1, "type": "gateway", "resource": "mute", "method": "post", "auth": "MO0004A3F9B33B"}
    {"resource": "status", "method": "get", "auth": "MO0004A3F9B33B"}
{"body": {"stateFrequency": 180, "smileLed": "255,0,0", "serverUrl": "in.sen.se", "rightLed": "60,100,240", "rfPower": 100, "leftLed": "60,100,240", "serverPort": 80, "maxConn": 24, "soundLevel": 75}, "type": "gateway", "resource": "state", "method": "post", "auth": "MO0004A3F9B33B"}



{"body": {"smileLed": "0,255,0", "rightLed": "60,100,240",  "leftLed": "60,100,240"}, "type": "gateway", "resource": "state", "method": "post", "auth": "MO0004A3F9B33B"}

{"body": {"rfPower": 100}, "type": "gateway", "resource": "state", "method": "post", "auth": "MO0004A3F9B33B"}
{"body": {"Nb Cookie": 1}, "type": "gateway", "resource": "events", "method": "post", "auth": "MO0004A3F9B33B"}

'''
def debugLog( txt ): 
    n = "( " + time.strftime("%c") + " ) "
    logFile = 'srvlog.log'
    subprocess.call( 'echo "'+n+txt+'" >> '+logFile, shell=True )  
    return

def addToLog( txt ):
    print(txt)
    f = open("mother-log.txt", "a+")
    f.write(txt)
    f.write("\n")

# Called for every client connecting (after handshake)
def new_client(client, server):
    global cl_mother
    global cl0
    h=client['address'][0]
    addToLog("New client connected and was given id %d %s" % (client['id'], h))
    
    if client['id']==1:
      cl_mother=client
    if client['id']==2:
      cl0=client
    ##server.send_message_to_all("Hey all, a new client has joined us")


# Called for every client disconnecting
def client_left(client, server):
    global cl0
    addToLog("Client(%d) disconnected" % client['id'])
    if client['id']==2:
      cl0=''


# Called when a client sends a message
def message_received(client, server, message):
    addToLog(message);
    global sleep_state
    global cl_mother
    global cl0
    try:
        debugLog(chr(48+client['id'])+" "+message)
    except:
        addToLog("Error handling on message: " + str(client['id']) + " " + message)

    #debugLog(message)
    if len(message) > 200:
      message = message[:200]+'..'
    addToLog("Client(%d) said: %s" % (client['id'], message))
    if client['id']==2:
      addToLog("invio a Client(%d) " % (cl_mother['id']))
      addToLog("test " + message)
      server.send_message(cl_mother, message)
  
    #controlli
    if client['id']==1:
     j = json.loads(message)
     if j['resource']=='auth':
      addToLog("Client(%d) " % (client['id']))
      addToLog("auth request")
      fase=1
      server.send_message(client, msg_1)
      addToLog("SRV:" + msg_1)

     if j['resource']=='login':
      addToLog("Client(%d) " % (client['id']))
      addToLog("auth request 2")
      fase=2
      server.send_message(client, msg_2)
      addToLog("SRV:" + msg_2)
      
     if j['resource']=='registration':
      addToLog("Client(%d) " % (client['id']))
      addToLog("auth request 3")
      fase=3
      server.send_message(client, msg_3)
      addToLog("SRV:" + msg_3)
      server.send_message(client, msg_3a)
      addToLog("SRV:" + msg_3a)
      
     if j['resource']=='planning':
      addToLog("Client(%d) " % (client['id']))
      addToLog("auth request 4")
      fase=4
      server.send_message(client, msg_4)
      addToLog("SRV:" + msg_4)
      
     if j['resource']=='library/sound':
      addToLog("Client(%d) " % (client['id']))
      addToLog("auth request 6")
      fase=5
      server.send_message(client, msg_6)
      addToLog("SRV:" + msg_6)     

     if j['resource']=='library/resident':
      addToLog("Client(%d) " % (client['id']))
      addToLog("auth request 5")
      fase=6
      server.send_message(client, msg_5)
      addToLog("SRV:" + msg_5)

     if j['resource']=='events':
      addToLog("Client(%d) " % (client['id']))
      addToLog("events ")
      node=''
      try:
        node=j['body'][0]['node']
      except KeyError:
        addToLog("no node")
      ## cerca il nodo tra i biscotti
      co=''
      idx=0
      for x in cookieNode:
        if x==node:
          co=cookieName[idx]
          break
        idx+=1
      if co!='':
        addToLog("cookie " + co)
        ft=j['body'][0]['feed_type']
        si=j['body'][0]['signal']
        va=j['body'][0]['value']
        #a=datetime.datetime.now()
        #t=a.strftime('%d-%m-%Y %H:%M:%S.%f')
        t = "( " + time.strftime("%c") + " ) "
        #tmp="_"+t+"_feed_=" + ft + "_signal_=" +si+ "_value_="+va
        tmp=t+";"+ft+";"+si+";"+va;
        addToLog("tmp = " + tmp)
        #send to browser
        if cl0!='':
          server.send_message(cl0, "COOKIE"+chr(49+idx)+tmp)
        else:
          addToLog("not dbg redirection")
                
      if j['body'][0]['feed_type']=='6':
        addToLog("feed 6 ")
        if j['body'][0]['value']>='5000' and sleep_state<2:
           addToLog("sleep fase 1")
           sleep_state+=1
           if sleep_state==2:
              addToLog("sleep fase 2")
              server.send_message(client, msgsleep)
        else:
           if sleep_state>1:
              addToLog("wake up ")
              sleep_state=0
              server.send_message(client, msgwakeup)
      if j['body'][0]['feed_type']=='1' and j['body'][0]['value']=='1':
        addToLog("ping!? ")
        server.send_message(client, msgup)
          
      
#PORT=80
#HOST='192.168.0.1'
server = WebsocketServer(PORT,HOST,logging.INFO)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
