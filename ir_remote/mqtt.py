#!/usr/bin/python3

import sys, os, time, json
import paho.mqtt.client as mqtt

try:
    from remotelog import remoteLog
except Exception as ex:
    print("Error" + str(ex))
    sys.exit()


class remoteMqtt:

    def __init__(self): 
        self.remoteLog = remoteLog()  
        self.remoteLog.info("-------Launching MQTT-------")  
        self.broker = 'localhost'
        self.port = 1883
        self.client_id = 'irRemote-mqtt-bridge'  

    def run(self, deviceList):       
        mqtt.Client.connected_flag = False
        mqtt.Client.bad_connection_flag=False
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.loop_start()
        self.remoteLog.info("Connecting to Broker: %s" % self.broker)
        self.client.connect(self.broker, self.port, 60)
        while not self.client.connected_flag:
            self.remoteLog.info("-------Connecting-------.")
            time.sleep(1)
        if self.client.bad_connection_flag:
            self.client.loop_stop()
            sys.exit()

        for device in deviceList:
            self.haDiscovery(device)

        #self.remoteHass()

    def haDiscovery(self, remote):

        self.remoteLog.info("-------Start MQTT Discovery-------")
        self.remoteLog.info("Remote: "+remote+"")
        make = remote.split('_', 1)[0]
        model = remote.split('_', 1)[-1]  


        #Power button
        discoveryMsg = {"name": "Power",
            "command_topic":"IR-Remote/"+remote+"/pwr/set",
            "payload_press":""+remote+":Power",
            "unique_id":""+remote+"",
            "icon": "mdi:power",
            "device": {
                "name": remote,
                "model": ""+model+"",
                "manufacturer": ""+make+"",
                "identifiers": remote,
                }
            } 
        
        self.publish("homeassistant/button/"+remote+"/config", json.dumps(discoveryMsg))
        self.subscribe("IR-Remote/"+remote+"/pwr/set")

        #CH + button
        discoveryMsg = {"name": "Ch +",
            "command_topic":"IR-Remote/"+remote+"/chup/set",
            "payload_press":""+remote+":Ch +",
            "unique_id":"ChUp"+remote+"",
            "icon": "mdi:plus",
            "device": {
                
                "identifiers": remote
                }
            } 

        self.publish("homeassistant/button/"+remote+"_chup/config", json.dumps(discoveryMsg))
        self.subscribe("IR-Remote/"+remote+"/chup/set")

        #Ch - button
        discoveryMsg = {"name": "Ch -",
            "command_topic":"IR-Remote/"+remote+"/chdwn/set",
            "payload_press":""+remote+":Ch -",
            "unique_id":"chdwn_"+remote+"",
            "icon": "mdi:minus",
            "device": {
                
                "identifiers": remote
                }
            } 

        self.publish("homeassistant/button/"+remote+"_chdwn/config", json.dumps(discoveryMsg))
        self.subscribe("IR-Remote/"+remote+"/chdwn/set")

        #Vol + button
        discoveryMsg = {"name": "Vol +",
            "command_topic":"IR-Remote/"+remote+"/volup/set",
            "payload_press":""+remote+":Vol +",
            "unique_id":"volup_"+remote+"",
            "icon": "mdi:volume-plus",
            "device": {
                
                "identifiers": remote
                }
            } 
        
        self.publish("homeassistant/button/"+remote+"_volup/config", json.dumps(discoveryMsg))
        self.subscribe("IR-Remote/"+remote+"/volup/set")

        #Vol - button
        discoveryMsg = {"name": "Vol -",
            "command_topic":"IR-Remote/"+remote+"/voldwn/set",
            "payload_press":""+remote+":Vol -",
            "unique_id":"voldwn_"+remote+"",
            "icon": "mdi:volume-minus",
            "device": {
                
                "identifiers": remote
                }
            } 
     
        self.publish("homeassistant/button/"+remote+"_voldwn/config", json.dumps(discoveryMsg))
        self.subscribe("IR-Remote/"+remote+"/voldwn/set")

        #mute button
        discoveryMsg = {"name": "Mute",
            "command_topic":"IR-Remote/"+remote+"/mute/set",
            "payload_press":""+remote+":Mute",
            "unique_id":"mute_"+remote+"",
            "icon": "mdi:volume-mute",
            "device": {
                
                "identifiers": remote
                }
            } 
        
        self.publish("homeassistant/button/"+remote+"_mute/config", json.dumps(discoveryMsg))
        self.subscribe("IR-Remote/"+remote+"/mute/set")

        #Info button
        discoveryMsg = {"name": "Info",
            "command_topic":"IR-Remote/"+remote+"/info/set",
            "payload_press":""+remote+":Info",
            "unique_id":"info_"+remote+"",
            "icon": "mdi:information-variant",
            "device": {
                "name": remote,
                "identifiers": remote
                }
            } 
        
        self.publish("homeassistant/button/"+remote+"_info/config", json.dumps(discoveryMsg))
        self.subscribe("IR-Remote/"+remote+"/info/set")


    def remoteHass(self):
        self.remoteLog.info("-------Start MQTT Discovery-------")
        self.remoteLog.info("Remote: Test IR Remote")
        remoteDiscovery = {
            "name": "Living Room Remote",
            "unique_id": "livingroom_remote",
            "command_topic": "homeassistant/remote/livingroom_remote/set",
            "availability_topic": "homeassistant/remote/livingroom_remote/availability",
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": {
                "identifiers": ["livingroom_remote"],
                "manufacturer": "Example Manufacturer",
                "model": "Model ABC",
                "name": "Living Room Remote"
            },
            "commands": {
                "power": {
                "command_topic": "homeassistant/remote/livingroom_remote/power",
                "payload_on": "ON",
                "payload_off": "OFF"
                },
                "mute": {
                "command_topic": "homeassistant/remote/livingroom_remote/mute",
                "payload_on": "MUTE_ON",
                "payload_off": "MUTE_OFF"
                }
            }
        }

        self.publish("homeassistant/media_player/test_tv/config", json.dumps(remoteDiscovery))
        self.subscribe("IR-Remote/test_tv/set")


        
    def publish(self, topic, msg):           
            config = json.loads(msg) 
            #self.remoteLog.info("-------MQTT Publish-------")
            #self.remoteLog.info("Topic: "+config['name']+"")
            self.client.publish(topic, msg, qos=2, retain=False)
            #self.remoteLog.info("Published Successfully" )
            
    def subscribe(self, topic):
        #self.remoteLog.info("-------MQTT Subscribe-------")
        #self.remoteLog.info("Topic: "+topic+"")
        self.client.subscribe(topic, 1)
        #self.remoteLog.info("Subscribed Successfully")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.client.connected_flag=True
            self.remoteLog.info("Connected to MQTT Broker Successfully")
        else:
            self.client.bad_connection_flag=True
            print("Failed to connect, return code %d\n", rc)
            self.remoteLog.info("-------Failed to connect-------")

    def on_disconnect(self, client, userdata, rc):
        self.remoteLog.info(rc)

    