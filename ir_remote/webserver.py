#!/usr/bin/python3

import sys, os


try:
    from flask import Flask, render_template, request
    from flask_restful import Api, Resource
    from pathlib import Path
    from remotelog import remoteLog
except Exception as ex:
    print("Error" + str(ex))
    sys.exit()


class flaskWrapper:
    def __init__(self, remote):
        self.remoteLog = remoteLog()
        self.remoteLog.info("-------Loading Webserver-------")
        self.root = Path(__file__).parents[1]
        #template_dir = os.path.join(template_dir, 'templates')
        self.templatePath = self.root / "templates"
        self.app = Flask(__name__, template_folder=self.templatePath)
        self.app.route("/", methods=["GET", "POST"])(self.main)
        self.app.route("/settings.html", methods=["GET", "POST"])(self.settings)
        self.remoteLog.info("Webserver Loaded uccessfully")
        self.remote = remote  

           
    def main(self):         
        key = ""
        if request.method == "POST":
            key = request.form.get('button') 
            self.remote.keyPress(key)
            key = ""                 
            return render_template('main.html', **self.remote.activeConfig) 
          
        if request.method == "GET":      
            return render_template('main.html', **self.remote.activeConfig)
        
    def settings(self):       
        if request.method == "POST":
            r = request.form.get('devices')
            p = request.form.get('pulseLength')
            if r == self.remote.active:           
                self.remote.activeConfig['pulseLength'] = p   
                for btn in self.remote.activeConfig['btns'] :
                    data = request.form.get('%s' % (btn))
                    pulse = request.form.get('%s_pulse' % (btn))                    
                    if pulse == 'on':
                        self.remote.activeConfig['btns'][btn]['pulse'] = "long"
                    else:
                        self.remote.activeConfig['btns'][btn]['pulse'] = "short" 
                    self.remote.activeConfig['btns'][btn]['key'] = data         
                self.remote.updateConfig(self.remote.activeConfig)                 
            else:
                self.remote.active = r
                self.remote.switchDevice(self.remote.active)                       
            return render_template('main.html', **self.remote.activeConfig)
        
        if request.method == "GET":       
            return render_template('settings.html', **self.remote.activeConfig)


    def run(self):
        self.app.run(host='0.0.0.0', port=8081, debug=True)

