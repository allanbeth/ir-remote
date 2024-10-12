#!/usr/bin/python3

import sys

try:
    from remotelog import remoteLog
    from webserver import flaskWrapper
    from remote import remote
    from mqtt import remoteMqtt
except Exception as ex:
    print("Error" + str(ex))
    sys.exit()

              
class launchremote:           

    def __init__(self):

        #load remoteLog
        self.loadremoteLog()
        
        #load remote
        self.loadRemote()

        #load mqtt
        self.loadMqtt()
            
        #launch webserver
        self.loadWebserver()

        
    def loadremoteLog(self):
        self.remoteLog = remoteLog()

    def loadMqtt(self):
        self.mqtt = remoteMqtt()
        name = self.remote.config['name']
        self.mqtt.run(name)
        self.mqtt.client.on_message = self.mqttMessage 

    def loadRemote(self):
        self.remote = remote()
        self.remote.activeRemote.keyPress = self.webserverkeypress
        self.remote.activeRemote.updateConfig = self.webserverUpdate
        self.remote.activeRemote.switchDevice = self.webserverSwitch
            
    def loadWebserver(self):  
        activeRemote = self.remote.activeRemote   
        self.mywebserver = flaskWrapper(activeRemote)
        self.mywebserver.run()

    def mqttMessage(self, client, userdata, msg):
        key = msg.payload.decode()
        self.remoteLog.info("-------MQTT Button-------")
        self.remoteLog.info("Button Pressed: "+key+"")
        self.remote.send(key)

    def webserverkeypress(self, key):
        self.remoteLog.info("-------Webserver Button-------")
        self.remoteLog.info("Button Pressed: %s" % key)
        self.remote.send(key)

    def webserverUpdate(self, data):
        self.remoteLog.info("-------Saving config-------")
        self.remoteLog.info("Remote: "+self.remote.activeRemote.name+"")
        self.remote.update(data)
        self.remoteLog.info("Saved Successfully")

    def webserverSwitch(self, name):
        self.remoteLog.info("-------Switching Device-------")
        self.remoteLog.info("New Device: "+name+"")
        self.remote.load(name)
        self.remoteLog.info("Switched Successfully")


if __name__ == '__main__':
        
    #Start IR Remote
    remote = launchremote()

        

            
            


        

        
    
    
