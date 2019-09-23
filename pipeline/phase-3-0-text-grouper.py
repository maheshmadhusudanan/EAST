import string
import time  
import argparse
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler
import pandas as pd
import sys
import os
import csv
sys.path.append(os.path.abspath(os.path.join('../utils')))
from PipelineFileName import PipelineFileName

class Phase_3_0_TextGrouper(PatternMatchingEventHandler):

    patterns = ["*.csv"]
    ignore_directories = False
    txtReader = None

    def __init__(self):
        
         # call super
        super(Phase_3_0_TextGrouper, self).__init__()
    
        
    def on_created(self, event):
        print("triggered event  is dir="+str(event.is_directory)+" , file path = "+str(event.src_path))
        # if (event.is_directory == False):
        #     return
        self.process(event)
 
    
    def process(self, event):

        try:       

            print("------------------------------ phase -3 STARTED for file "+event.src_path+"------------------------")                        
            input_pipe_file = PipelineFileName(task_file_name=os.path.basename(event.src_path))
            output_pipe_file = PipelineFileName(task_file_name=os.path.basename(event.src_path))
            output_pipe_file.file_cat = ""
            output_pipe_file.file_ext = ".csv"

            preds_map_df = pd.read_csv(event.src_path, error_bad_lines=False, quoting=csv.QUOTE_NONE, encoding='utf-8')
            print ("** predictions shape = "+str(preds_map_df.shape))
            

            segmented_file_name = os.path.join(".","phase-1-1-output", 
                                        output_pipe_file.task_output_folder_name, output_pipe_file.task_output_file_name)
            print("about to read the segmented file "+segmented_file_name)
            segmented_data_df = pd.read_csv(segmented_file_name, error_bad_lines=False, quoting=csv.QUOTE_NONE, encoding='utf-8')

            output_pipe_file.file_cat = "FI"
            grouped_output_file = os.path.join(".","phase-3-0-output",output_pipe_file.task_output_file_name)            
            
            print ("segmented data shape ="+str(segmented_data_df.shape))
            
            print("------------------------------ complete PHASE -3-------------------------")
        except Exception as me:
            print ("------------------------------------------------- EXCEPTION ---------------------------------------------------------")
            print (str(me))
            print("could not process file "+str(event.src_path))
            print ("------------------------------------------------- END EXCEPTION PHASE -3-0---------------------------------------------------------")

                

if __name__ == '__main__':
    args = sys.argv[1:]

    print("Started Phase-3 observer....")
    observer = Observer()
    observer.schedule(Phase_3_0_TextGrouper(), path=args[0] if args else './phase-2-0-output')
    observer.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()