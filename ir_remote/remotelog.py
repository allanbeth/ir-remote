#!/usr/bin/python3

import sys, logging

try:
    from pathlib import Path
except Exception as ex:
    print("Error" + str(ex))
    sys.exit()

root = Path(__file__).parents[1]
logPath = root / "irRemote.log"
log_format = "%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(filename=logPath, level=logging.DEBUG, format=log_format, datefmt=date_format)

class remoteLog:

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    def debug(self, msg):
        self.logger.debug(msg)
        

    def info(self, msg):
        self.logger.info(msg)
        
    def warning(self, msg):
        self.logger.warning(msg)
        
        
    def error(self, msg):
        self.logger.error(msg)


    def critical(self, msg):
        self.logger.critical(msg)

    def resetLog(self):
        with open(logPath, "w") as data:
            pass

        self.info("Log File Reset Successfully")

    def getLog(self, x):
        fileContent = []
        with open(logPath, "r") as data:
            for line in data:
                fileContent.append(line)  

        if x == 1:
            fileContent = fileContent[-100:]
        logData = {} 
        fileContent.reverse()
        logData['data'] = fileContent
        return logData

