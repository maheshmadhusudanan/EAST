import time  
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler  
import os
import sys
import ntpath
import shutil
import uuid
import cv2
import numpy as np
import imutils
from types import SimpleNamespace
from keras.models import load_model, model_from_json
from tensorflow import Graph, Session
import math
import argparse
import sys
from os import path

sys.path.append(os.path.abspath(os.path.join('../utils')))
sys.path.append(os.path.abspath(os.path.join('../lanms')))
sys.path.append(os.path.abspath(os.path.join('../models')))
sys.path.append(os.path.abspath(os.path.join('..')))
from data_processor import restore_rectangle
from losses import *
from model import *
import lanms
import locality_aware_nms as nms_locality
from PipelineFileName import PipelineFileName
from eval import resize_image, detect, sort_poly

#
# This class will check if the image is a free block texts or if its a form
# Its will move the image to Open cv 
#
class Phase1_0ImageLineContourExtractorHandler(PatternMatchingEventHandler):

    patterns = ["*.jpg"]

    def __init__(self):
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        model_dir_path = os.path.join(os.path.dirname(__file__),"../models")
        default_model_file_path = os.path.join(model_dir_path,"EAST_IC15+13_model.h5")
        json_file = open(os.path.join(model_dir_path,'model.json'), 'r')
        # try:
        #     os.makedirs(FLAGS.output_dir)
        # except OSError as e:
        #     if e.errno != 17:
        #         raise

        # load trained model        
        loaded_model_json = json_file.read()
        json_file.close()
        self.graph1 = Graph()
        self.tf_session = None
        with self.graph1.as_default():
            self.tf_session = Session()
            with self.tf_session.as_default():
                self.model = model_from_json(loaded_model_json, custom_objects={'tf': tf, 'RESIZE_FACTOR': RESIZE_FACTOR})
                self.model.load_weights(default_model_file_path)
                print("**** loading "+default_model_file_path+"......successful *******")
        
        # call super
        super(Phase1_0ImageLineContourExtractorHandler, self).__init__()
            
    def on_created(self, event):
        self.process(event)
        
    #
    # This function will detect all the characters on the page
    # and erase it, so that the form borders can be easily detected.
    # This will create a file with name <target_file>-M.jpg, where M denotes the mask in 
    # a loose sense.
    
    def process(self, event):
        
        pipeline_file = PipelineFileName(task_file_name=os.path.basename(event.src_path))

        if pipeline_file.file_cat == "M":
            return

        # output of phase 0 is the input to phase1-0
        input_path = os.path.join(os.path.dirname(os.path.realpath("__file__")) , "phase0-output")     
        out_folder_name = pipeline_file.unique_id+"_"+pipeline_file.page_num
        temp_output_path = os.path.join(os.path.dirname(os.path.realpath("__file__")) , "phase-1-0-output","temp", pipeline_file.task_output_folder_name)        
        output_path = os.path.join(os.path.dirname(os.path.realpath("__file__")) , "phase-1-0-output")  
        #after phase 1 processing archive the images to archive folder
        archive_to =  os.path.join(os.path.basename(event.src_path),"processesd")
        
        img_file = event.src_path       
        img = cv2.imread(img_file)[:, :, ::-1]
        start_time = time.time()
        img_resized, (ratio_h, ratio_w) = resize_image(img)

        img_resized = (img_resized / 127.5) - 1

        timer = {'net': 0, 'restore': 0, 'nms': 0}
        start = time.time() 

        # feed image into model
        print("--->>>>> about to predict score map... for image "+str(img_resized.shape))
        boxes = None
        with self.graph1.as_default():
            with self.tf_session.as_default():
                score_map, geo_map = self.model.predict(img_resized[np.newaxis, :, :, :])
                timer['net'] = time.time() - start
                print("--->>>>> about to detect boxes")
                boxes, timer = detect(score_map=score_map, geo_map=geo_map, timer=timer)
                print('{} : net {:.0f}ms, restore {:.0f}ms, nms {:.0f}ms'.format(
                img_file, timer['net']*1000, timer['restore']*1000, timer['nms']*1000))

        if boxes is not None:
            boxes = boxes[:, :8].reshape((-1, 4, 2))
            boxes[:, :, 0] /= ratio_w
            boxes[:, :, 1] /= ratio_h

        duration = time.time() - start_time
        print('[timing] {}'.format(duration))

        print("about to remove all files from if already exists"+temp_output_path)
        try:
            shutil.rmtree(temp_output_path)
            shutil.rmtree(output_path)
        except Exception as e:
            print(e)
        os.mkdir(temp_output_path)

        # erase all detected boxes       
        if boxes is not None:            
            #
            # remove all the boxes
            #
            idx = 0
            save_pipeline_file = PipelineFileName(task_file_name=os.path.basename(event.src_path))
            doc_pos_map_file = os.path.join(temp_output_path, "doc_pos_map.csv")
            with open(doc_pos_map_file, 'w') as f:
                f.write('{},{},{},{},{}\r\n'.format("file", "x1", "y1", "x2", "y2"))                        
                for box in boxes:
                    # to avoid submitting errors
                    box = sort_poly(box.astype(np.int32))
                    if np.linalg.norm(box[0] - box[1]) < 5 or np.linalg.norm(box[3]-box[0]) < 5:
                        continue

                    margin = 1
                    y1 = box[0,1] + margin
                    y2 = box[2,1] - margin
                    x1 = box[0,0] + margin
                    x2 = box[2,0] - margin
                    
                    crop_img = img[y1:y2, x1:x2]                    
                    if crop_img.size != 0:
                        idx += 1
                        save_pipeline_file.segment = "0"
                        save_pipeline_file.segment = str(idx)
                        new_file = os.path.join(temp_output_path, save_pipeline_file.task_output_file_name)
                        print("phase-1-0: extracting snippet file ... "+new_file)
                        cv2.imwrite(new_file, crop_img)
                        f.write('{},{},{},{},{}\r\n'.format(save_pipeline_file.task_output_file_name, x1, y1, x2, y2))
                        

                    cv2.fillPoly(img[:, :, ::-1], [box.astype(np.int32).reshape((-1, 1, 2))], color=(255, 255, 255))                    

            # moving the temp data to output
            shutil.move(temp_output_path, output_path)
         
        # save to file        
        pipeline_file.file_cat = 'M'                
        img_path = os.path.join(os.path.dirname(img_file), pipeline_file.task_output_file_name)        
        print("about to save the line contour file....."+img_path)
        cv2.imwrite(img_path, img[:, :, ::-1])
        # move the processed file

if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(Phase1_0ImageLineContourExtractorHandler(), path=args[0] if args else './phase0-output')
    observer.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()