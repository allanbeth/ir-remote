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
        deviceList = self.remote.deviceList
        self.mqtt.run(deviceList)
        self.mqtt.remoteHass()
        self.mqtt.client.on_message = self.mqttMessage 

    def loadRemote(self):
        self.remote = remote()
        self.remote.activeRemote.keyPress = self.webserverkeypress
        self.remote.activeRemote.updateConfig = self.webserverUpdate
        self.remote.activeRemote.switchDevice = self.webserverSwitch
            
    def loadWebserver(self):     
        self.mywebserver = flaskWrapper(self.remote.activeRemote)
        self.mywebserver.run()

    def mqttMessage(self, client, userdata, msg):
        data = msg.payload.decode()
        device = data.split(':', 1)[0]
        key = data.split(':', 1)[-1] 
        self.remoteLog.info("-------MQTT Button-------")
        self.remoteLog.info("Button Pressed: "+key+"")
        self.remote.send(device, key)

    def webserverkeypress(self, key):
        self.remoteLog.info("-------Webserver Button-------")
        self.remoteLog.info("Button Pressed: %s" % key)
        self.remote.send(self.remote.activeRemote.active, key)

    def webserverUpdate(self, device, data):
        self.remoteLog.info("-------Saving config-------")
        self.remoteLog.info("Remote: "+self.remote.activeRemote.active+"")
        self.remote.update(device, data)
        self.remoteLog.info("Saved Successfully")

    def webserverSwitch(self, name):
        self.remoteLog.info("-------Switching Device-------")
        self.remoteLog.info("New Device: "+name+"")
        self.remote.load(name)
        self.remoteLog.info("Switched Successfully")

def run():
    remote = launchremote()

if __name__ == "__main__":
        
    #Start IR Remote
    run()
        

            
            


        

        
    
    
