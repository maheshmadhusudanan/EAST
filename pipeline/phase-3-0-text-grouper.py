import string
import time  
import argparse
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler
import pandas as pd
import sys
import os
import csv

class Phase_3_0_TextGrouper(PatternMatchingEventHandler):

    patterns = ["*.csv"]
    ignore_directories = False
    txtReader = None

    def __init__(self):
        
        # predict
        # model.eval()
        self.txtReader = TextReader({})

         # call super
        super(Phase_2_0_Image2TextExtractor, self).__init__()
    
        
    def on_created(self, event):
        print("triggered event  is dir="+str(event.is_directory)+" , file path = "+str(event.src_path))
        # if (event.is_directory == False):
        #     return
        self.process(event)

    
    #
    # This function will detect all the characters on the page
    # and erase it, so that the form borders can be easily detected.
    # This will create a file with name <target_file>-M.jpg, where M denotes the mask in 
    # a loose sense.
    
    def process(self, event):

        try:       

            print("completed combining doc map and results...")

            print("------------------------------ complete ------------------------")
        except Exception as me:
            print ("------------------------------------------------- EXCEPTION ---------------------------------------------------------")
            print (str(me))
            print("could not process file "+str(event.src_path))
            print ("------------------------------------------------- EXCEPTION ---------------------------------------------------------")

                

if __name__ == '__main__':
    args = sys.argv[1:]

    observer = Observer()
    observer.schedule(Phase_3_0_TextGrouper(), path=args[0] if args else './phase-3-0-input')
    observer.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()