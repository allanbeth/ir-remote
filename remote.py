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
        self.config = config
        self.name = self.config['name']
        self.remoteLog.info("-------Loading active remote-------")
        self.remoteLog.info("Loaded: "+self.name+"")

    def saveActive(self):
        #set active remote
        file = open(self.activePath, "r")
        config = json.load(file)
        config['active'] = self.name
        with open(self.activePath, "w") as f:
            json.dump(config, f)
        self.remoteLog.info("Master Config Updated")
        
    def keyPress(self, key):
        return key  

    def updateConfig(self, data):
        self.remoteLog.info("-------Updating Config-------")
        return data
    
    def switchDevice(self, name):
        self.remoteLog.info("-------Switching active remote-------")
        return name
    
class remote:

    def __init__(self):

        #load remote log
        self.remoteLog = remoteLog()
        
        #load master config
        self.root = Path(__file__).parents[0]
        self.masterPath = self.root / "irMasterConfig.json"    
        file = open(self.masterPath, "r")
        self.masterConfig = json.load(file)
        file.close()
        self.config = {}

        #configure buttons from master config 
        self.config['btns'] = self.masterConfig['btns']

        #check config directory exists
        configDir = "config" 
        configPath = self.root / configDir
        Path(configPath).mkdir(parents=True, exist_ok=True) 

        self.activeFile = "config/active.json"
        self.activePath = self.root / self.activeFile
        self.remoteLog.info( self.activePath)
        active = {}
        
        if self.activePath.is_file():
            file = open(self.activePath, "r")
            active = json.load(file)
            self.name = active['name']
            file.close()
        else:
            active['name'] = "None"
            with open(self.activePath, "w") as f:
                json.dump(active, f)
            self.name = active['name']

  

        #get device list
        self.deviceList = self.list()
        self.remoteLog.info("Loaded remotes: %s" % self.deviceList)
        if len(self.deviceList) == 0:
            self.remoteLog.info("No Config files installed")
            exit()
        else:
            self.config['devices'] = self.deviceList
        if self.name == "None":
            self.name = self.deviceList[0]
            self.remoteLog.info("Set Remote: %s" % self.name)
        
        self.load(self.name)


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
        

    def load(self, name):
     
        self.configFile = "config/%s.json" % name
        self.configPath = self.root / self.configFile       
        if self.configPath.is_file():
            self.set()
        else:
            self.add()
            self.set()
        

    def set(self): 
        file = open(self.configPath)
        config = json.load(file)
        self.config['name'] = self.name 
        self.config['make'] = self.name.split('_', 1)[0]
        self.config['model'] = self.name.split('_', 1)[-1]  
        #self.remoteLog.info("Loaded Remote: %s " % self.name)

        #assign buttons
        for btn in self.config['btns'] :
            data = config['btns'][btn]['key']
            pulse = config['btns'][btn]['pulse']                   
            if pulse == 'on':
                self.config['btns'][btn]['pulse'] = "long"
            else:
                self.config['btns'][btn]['pulse'] = "short" 
            self.config['btns'][btn]['key'] = data 
        self.config['pulseLength'] = config['pulseLength'] 
        self.activeRemote = activeRemote(self.config)
        #self.remoteLog.info("Buttons Assigned Successfully") 
        self.getKeys()     

        #save active device name
        #self.updateMaster()   
        self.updateActive()  
                     
    def add(self):
        self.getKeys() 

        #initial button config
        btns = self.config['btns']
        keys = self.config['option']
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
        self.config['btns'] = btns
        self.config['option'] = keys
        self.config['pulseLength'] = "2"
        self.update(self.config)

    def send(self, key):
        k = self.config['btns'][key]['key']
        p = self.config['btns'][key]['pulse'] 
        if p == "long":
            l = int(self.config['pulseLength']) 
        else:
            l = 0.5    
        os.system('irsend SEND_START %s %s'%(self.name, self.config['btns'][key]['key']))
        time.sleep(l)
        os.system('irsend SEND_STOP %s %s'%(self.name, self.config['btns'][key]['key']))
        self.remoteLog.info("IR Signal Sent for: "+self.name+" "+self.config['btns'][key]['key']+"")

    def update(self, data):
        config = {}
        config['btns'] = data['btns']
        config['pulseLength'] = data['pulseLength']
        with open(self.configPath, "w") as f:
            json.dump(config, f)
        self.remoteLog.info("Buttons Updated")
        
    def updateActive(self):
        #set active remote
        file = open(self.activePath, "r")
        active = json.load(file)
        active['name'] = self.name
        with open(self.activePath, "w") as f:
            json.dump(active, f)
        self.remoteLog.info("-------Active Device Updated-------")

    def getKeys(self):
        #load keys codes
        keyPath = self.root / "key_list.txt"
        get_list = 'irsend LIST %s "" > %s' % (self.name, keyPath)
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

        self.config['option'] = keys  

