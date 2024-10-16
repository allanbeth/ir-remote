#!/usr/bin/python3

import os, time, sys, json

try:
    from pathlib import Path
    from remotelog import remoteLog
except Exception as ex:
    print("Error" + str(ex))
    sys.exit()


class activeRemote:

    def __init__(self, config):        
        self.remoteLog = remoteLog()
        self.activeConfig = config
        self.active = self.activeConfig['name']
        self.remoteLog.info("-------Loading active remote-------")
        self.remoteLog.info("Loaded: "+self.active+"")


        
    def keyPress(self, key):
        return key  

    def updateConfig(self, device, data):
        self.remoteLog.info("-------Updating Config-------")
        return device, data
    
    def switchDevice(self, name):
        self.remoteLog.info("-------Switching active remote-------")
        return name
    
class remote:

    def __init__(self):

        #load remote log
        self.remoteLog = remoteLog()
        
        #load master config
        self.root = Path(__file__).parents[1]
        self.masterPath = self.root / "irMasterConfig.json"    
        file = open(self.masterPath, "r")
        self.masterConfig = json.load(file)
        file.close()
        self.activeConfig = {}

        #configure buttons from master config 
        self.activeConfig['btns'] = self.masterConfig['btns']

        #check config directory exists
        configDir = "config" 
        configPath = self.root / configDir
        Path(configPath).mkdir(parents=True, exist_ok=True) 

        self.activeFile = "config/activeDevice.json"
        self.activePath = self.root / self.activeFile
        self.remoteLog.info( self.activePath)
        active = {}
        
        if self.activePath.is_file():
            file = open(self.activePath, "r")
            active = json.load(file)
            file.close()
            self.active = active['name']
        else:
            active['name'] = "None"
            with open(self.activePath, "w") as f:
                json.dump(active, f)
                f.close()
            self.active = active['name']

        #get device list
        self.deviceList = self.list()
        self.remoteLog.info("Loaded remotes: %s" % self.deviceList)
        if len(self.deviceList) == 0:
            self.remoteLog.info("No Config files installed")
            exit()
        else:
            self.activeConfig['devices'] = self.deviceList
        if self.active == "None":
            self.active = self.deviceList[0]
            self.remoteLog.info("Set Remote: %s" % self.active)
        
        self.load(self.active)


    def list(self):
        path = self.root / "devices.txt"
        deviceList = []
        list = os.system('irsend LIST "" "" > %s' % path)
        with open(path, "r") as d:
            for line in d:
                x = line.split(' ', 1)[-1]                
                x = x.replace("\n", "")
                x = x.strip()
                if len(x) >= 2:
                    deviceList.append(x) 

        os.system("rm %s" % path)
        return(deviceList)
        

    def load(self, active):
        #load devices
        for device in self.deviceList:
            file = "config/%s.json" % device
            path = self.root / file
            if path.is_file():
                pass
            else:
                self.add(device)

        self.active = active
        
        self.activeConfigFile = "config/%s.json" % self.active
        self.activeConfigPath = self.root / self.activeConfigFile       
        if self.activeConfigPath.is_file():
            self.setActive()
        else:
            self.add(device)
            self.setActive()
        

    def setActive(self): 
        file = open(self.activeConfigPath)
        config = json.load(file)
        self.activeConfig['name'] = self.active 
        self.activeConfig['make'] = self.active.split('_', 1)[0]
        self.activeConfig['model'] = self.active.split('_', 1)[-1]  
        keys = self.getKeys(self.active)
        self.activeConfig['option'] = keys
        #assign buttons
        for btn in self.activeConfig['btns'] :
            data = config['btns'][btn]['key']
            pulse = config['btns'][btn]['pulse']                   
            if pulse == 'on':
                self.activeConfig['btns'][btn]['pulse'] = "long"
            else:
                self.activeConfig['btns'][btn]['pulse'] = "short" 
            self.activeConfig['btns'][btn]['key'] = data 
        self.activeConfig['pulseLength'] = config['pulseLength'] 
        self.activeRemote = activeRemote(self.activeConfig)
        #self.remoteLog.info("Buttons Assigned Successfully") 
        self.getKeys(self.active)     

        #save active device name
        #self.updateMaster()   
        self.updateActive()  
                     
    def add(self, device):
         

        #initial button config
        btns = self.activeConfig['btns']
        keys = self.getKeys(device)
        #keys = self.activeConfig['option']
        for btn in btns:
            for key in keys:
                vu = "VOLUMEUP"
                vd = "VOLUMEDOWN"
                chu = "CHANNELUP"
                chd = "CHANNELDOWN"
                prefix = "KEY_%s" % (btn)
                prefix = prefix.upper()
                if prefix in key:
                    btns[btn]['key'] = key
                    
                elif btn in key and btns[btn]['key'] == '':
                    btns[btn]['key'] = key 
                elif vu in key:
                    btns['Vol +']['key'] = key
                elif vd in key:
                    btns['Vol -']['key'] = key
                elif chu in key:
                    btns['Ch +']['key'] = key
                elif chd in key:
                    btns['Ch -']['key'] = key
        config = {}
        config['btns'] = btns
        config['option'] = keys
        config['pulseLength'] = "2"
        self.update(device, config)

    def send(self, device, key):
        #self.remoteLog.info(""+device+" "+key+"")
        
        #get code from keypress
        configFile = "config/%s.json" % device
        path = self.root / configFile
        file = open(path, "r")
        config = json.load(file)

        k = config['btns'][key]['key']
        p = config['btns'][key]['pulse'] 
        if p == "long":
            l = int(self.config['pulseLength']) 
        else:
            l = 0   
        #os.system('irsend SEND_START %s %s'%(self.active, self.activeConfig['btns'][key]['key']))
        os.system('irsend SEND_START %s %s'%(device, k))
        time.sleep(l)
        #os.system('irsend SEND_STOP %s %s'%(self.active, self.activeConfig['btns'][key]['key']))
        os.system('irsend SEND_STOP %s %s'%(device, k))
        #self.remoteLog.info("IR Signal Sent for: "+self.active+" "+self.activeConfig['btns'][key]['key']+"")
        self.remoteLog.info("IR Signal Sent for: "+device+" "+k+"")

    def update(self, device, data):
        config = {}
        config['btns'] = data['btns']
        config['pulseLength'] = data['pulseLength']
        file = "config/%s.json" % device
        path = self.root / file
        with open(path, "w") as f:
            json.dump(config, f)
        self.remoteLog.info("Buttons Updated")
        
    def updateActive(self):
        #set active remote
        file = open(self.activePath, "r")
        active = json.load(file)
        active['name'] = self.active
        with open(self.activePath, "w") as f:
            json.dump(active, f)
        self.remoteLog.info("-------Active Device Updated-------")

    def getKeys(self, device):
        #load keys codes
        keyPath = self.root / "key_list.txt"
        get_list = 'irsend LIST %s "" > %s' % (device, keyPath)
        list = os.system(get_list)
        #store key codes
        keys = []
        with open(keyPath, "r") as rc:
            for line in rc:
                x = line.split(' ', 1)[-1]
                x = x.replace("\n", "")
                x = x.strip()
                keys.append(x)
            os.system("rm %s" % keyPath)

        return keys
        #self.activeConfig['option'] = keys  

