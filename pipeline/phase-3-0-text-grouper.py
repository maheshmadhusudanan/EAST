import string
import time  
import argparse
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler
import pandas as pd
import sys
import os
import csv
import traceback
sys.path.append(os.path.abspath(os.path.join('../utils')))
from PipelineFileName import PipelineFileName
from types import SimpleNamespace
import traceback


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
    

    def is_rectangle_inside(self,r1, r2):
     
        if (((r2.x2)  <= (r1.x2)) and (r2.x1 >= r1.x1) and (r2.y1 >= r1.y1) and ((r2.y2) <= (r1.y2))):                                            
            return True
        else:
            return False
       
    
    def process(self, event):

        try:       

            print("------------------------------ phase -3 STARTED for file "+event.src_path+"------------------------")                        
            input_pipe_file = PipelineFileName(task_file_name=os.path.basename(event.src_path))
            output_pipe_file = PipelineFileName(task_file_name=os.path.basename(event.src_path))
            output_pipe_file.file_cat = ""
            output_pipe_file.file_ext = ".csv"

            preds_map_df = pd.read_csv(event.src_path, error_bad_lines=False, quoting=csv.QUOTE_NONE, encoding='utf-8')
            print ("** predictions shape = "+str(preds_map_df.shape))
            
            main_sections_file = os.path.join(".","phase-1-1-output", 
                                        output_pipe_file.task_output_folder_name, output_pipe_file.task_output_file_name)
            print("about to read the main sections file "+main_sections_file)
            main_sections_df = pd.read_csv(main_sections_file, error_bad_lines=False, quoting=csv.QUOTE_NONE, encoding='utf-8')            

            output_pipe_file.file_cat = "FI"
            final_output_file = os.path.join(".","phase-3-0-output",output_pipe_file.task_output_file_name)            
            
            #
            # Group logically 
            #
            preds_map_df.sort_values(by='y1', ascending=True, inplace=True)
            main_sections_df.sort_values(by='y1', ascending=True, inplace=True)
            main_sections_df["preds"] = ""

            for midx, main_seg in main_sections_df.iterrows():
                main_seg_box = SimpleNamespace(**main_seg)
                if not main_seg_box.isleaf:
                    continue

                for index, row in preds_map_df.iterrows():                
                    snippet_seg_box = SimpleNamespace(**row)
                    if self.is_rectangle_inside(main_seg_box, snippet_seg_box):
                        main_sections_df.at[midx, "preds"] = main_sections_df.at[midx, "preds"] + " " + snippet_seg_box.pred
                    if int(main_seg_box.y2) < int(snippet_seg_box.y1):
                        break

            print("wrting phase 3 output...")
            main_sections_df.sort_values(by='y1', ascending=True, inplace=True)      
            main_sections_df.to_csv(final_output_file)
            
            print("------------------------------ complete PHASE -3-------------------------")
        
        except Exception as me:
            print("------------------------------------------------- EXCEPTION ---------------------------------------------------------")
            print(str(me))
            print("could not process file "+str(event.src_path))
            # Display the *original* exception
            traceback.print_exc()
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