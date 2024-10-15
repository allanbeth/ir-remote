#!/usr/bin/python3

import sys, logging

try:
    from pathlib import Path
except Exception as ex:
    print("Error" + str(ex))
    sys.exit()

root = Path(__file__).parents[0]
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
