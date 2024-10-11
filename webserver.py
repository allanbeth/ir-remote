#!/usr/bin/python3

import sys


try:
    from flask import Flask, render_template, request
    from flask_restful import Api, Resource
    from pathlib import Path
except Exception as ex:
    print("Error" + str(ex))
    sys.exit()


class flaskWrapper:
    def __init__(self, remote):
        self.app = Flask(__name__)
        self.root = Path(__file__).parents[0]
        self.app.route("/", methods=["GET", "POST"])(self.main)
        self.app.route("/settings.html", methods=["GET", "POST"])(self.settings)
        self.remote = remote  

           
    def main(self):         
        key = ""
        if request.method == "POST":
            key = request.form.get('button') 
            self.remote.keyPress(key)
            key = ""                 
            return render_template('main.html', **self.remote.config) 
          
        if request.method == "GET":      
            return render_template('main.html', **self.remote.config)
        
    def settings(self):       
        if request.method == "POST":
            r = request.form.get('devices')
            p = request.form.get('pulseLength')
            if r == self.remote.name:           
                self.remote.config['pulseLength'] = p   
                for btn in self.remote.config['btns'] :
                    data = request.form.get('%s' % (btn))
                    pulse = request.form.get('%s_pulse' % (btn))                    
                    if pulse == 'on':
                        self.remote.config['btns'][btn]['pulse'] = "long"
                    else:
                        self.remote.config['btns'][btn]['pulse'] = "short" 
                    self.remote.config['btns'][btn]['key'] = data         
                self.remote.updateConfig(self.remote.config)                 
            else:
                self.remote.name = r
                self.remote.switchDevice(self.remote.name)                       
            return render_template('main.html', **self.remote.config)
        
        if request.method == "GET":       
            return render_template('settings.html', **self.remote.config)


    def run(self):
        self.app.run(host='0.0.0.0', port=8081, debug=True)

