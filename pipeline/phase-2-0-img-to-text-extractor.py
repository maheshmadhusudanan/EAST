import string
import time  
import argparse
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler
import pandas as pd
import sys
import os
import csv
sys.path.append(os.path.abspath(os.path.join('../../deep-text-recognition-benchmark')))
from text_reader import TextReader

class Phase_2_0_Image2TextExtractor(PatternMatchingEventHandler):

    patterns = ["*"]
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
                
        results = self.txtReader.predictAllImagesInFolder(os.path.abspath(event.src_path))
        res_file = os.path.join(event.src_path,"text-reader-output.csv")
        doc_pos_map_file = os.path.join(event.src_path,"doc_pos_map.csv")
        combined_file = os.path.join(event.src_path,"combined_results.csv")

        with open(res_file, 'w') as f:
            f.write('{},{}\r\n'.format("file", "pred"))
            for r in results:
                f.write("%s\n" % r)

        print("processed "+str(len(results))+" files...")
        
        #
        # combine files
        #
        docs_map_df = pd.read_csv(doc_pos_map_file, error_bad_lines=False).set_index('file')
        results_df = pd.read_csv(res_file, error_bad_lines=False).set_index('file')
        comb_df = results_df[results_df.index.isin(docs_map_df.index)]
            
        final_df = pd.concat([docs_map_df, comb_df], axis=1)
        final_df.to_csv(combined_file)
        

        print("completed combining doc map and results...")

        print("------------------------------ complete ------------------------")
                

if __name__ == '__main__':
    args = sys.argv[1:]

    observer = Observer()
    observer.schedule(Phase_2_0_Image2TextExtractor(), path=args[0] if args else './phase-1-0-output')
    observer.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()