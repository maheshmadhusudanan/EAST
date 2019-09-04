import time  
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler  
from pdf2image import convert_from_path
import os
import sys
import ntpath
import shutil
import uuid
sys.path.append(os.path.abspath(os.path.join('../utils')))
from PipelineFileName import PipelineFileName


class Pdf2ImageConvertorHandler(PatternMatchingEventHandler):

    patterns = ["*.pdf"]
    
    output_path = os.path.dirname(os.path.realpath("__file__")) + "/phase0-output"
    
    def on_created(self, event):
        self.process(event)
    
    def process(self, event):
        
        # for file_name in os.listdir(os.path.dirname(event.src_path)):
        pages = convert_from_path(event.src_path)
        
        print ("processed "+event.src_path+ " pages = "+str(len(pages)))

        for page in pages:

            pipeline_file  = PipelineFileName(os.path.basename(event.src_path), page_num=pages.index(page))
            outfile = os.path.join(self.output_path , pipeline_file.task_output_file_name)
            print ("saving..."+outfile)
            with open(outfile, 'w') as f:                 
                page.save(f, "JPEG")
        
        move_to =  os.path.join(os.path.dirname(event.src_path), "processed",os.path.basename(event.src_path))
        shutil.move(event.src_path, move_to)
        print ("moved file "+event.src_path+ " to.. "+move_to)


if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(Pdf2ImageConvertorHandler(), path=args[0] if args else './phase0-input')
    observer.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()