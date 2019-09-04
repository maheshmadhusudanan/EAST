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

sys.path.append(os.path.abspath(os.path.join('../utils')))
from PipelineFileName import PipelineFileName

#
# This class will check if the image is a free block texts or if its a form
# Its will move the image to Open cv 
#
class Phase1_1ImageSegmentorHandler(PatternMatchingEventHandler):

    patterns = ["*.jpg"]
        
    def on_created(self, event):
        self.process(event)
    
    def remove_duplicate_blocks(self,rects):
    
        clear_rects = []
        
        for r1 in rects:
            
            found = False
            for r2 in rects:                        
                if ((r2.x + r2.w)  <= (r1.x+r1.w)) and (r2.x >= r1.x) and (r2.y > r1.y) and ((r2.y+r2.h) < (r1.y+r1.h)):                                            
                    found = True
            
            if not found:
                clear_rects.append(r1)
        
        print(clear_rects)
        return clear_rects
    
    def sort_contours(self,cnts, method="left-to-right"):
        # initialize the reverse flag and sort index
        reverse = False
        i = 0
    
        # handle if we need to sort in reverse
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
    
        # the x-coordinate of the bounding box
        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1
    
        # construct the list of bounding boxes and sort them from top to
        # bottom
        boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
            key=lambda b:b[1][i], reverse=reverse))
    
        # return the list of sorted contours and bounding boxes
        return (cnts, boundingBoxes)

    def process(self, event):
                
        pipeline_file = PipelineFileName(task_file_name=os.path.basename(event.src_path))                        

        if pipeline_file.file_cat != "M":
            return

        tru_img_pipeline_file = PipelineFileName(task_file_name=os.path.basename(event.src_path)) 
        tru_img_pipeline_file.file_cat = ""
        tru_img_path = os.path.join(os.path.dirname(event.src_path), tru_img_pipeline_file.task_output_file_name)

        try:

            # output of phase 0 is the input to phase1-0
            input_path = os.path.join(os.path.dirname(os.path.realpath("__file__")) , "phase0-output")
            #output of phase 1-0
            out_folder_name = pipeline_file.unique_id+"_"+pipeline_file.page_num
            temp_output_path = os.path.join(os.path.dirname(os.path.realpath("__file__")) , "phase-1-1-output","temp", out_folder_name)        
            output_path = os.path.join(os.path.dirname(os.path.realpath("__file__")) , "phase-1-1-output")
            old_output_path = os.path.join(output_path, out_folder_name)
            #after phase 1 processing archive the images to archive folder
            archive_to =  os.path.join(os.path.basename(event.src_path),"processesd")

            img = cv2.imread(event.src_path ,0)
            (thresh, img_bin) = cv2.threshold(img, 128, 255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
            
            #invert image to binary
            img_bin = 255-img_bin 
            
            #define the kernal
            # Defining a kernel length
            kernel_length = np.array(img).shape[1]//80
            kernel_length = 2 
            # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
            verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
            kernel_length = 5
            # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
            hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
            print(hori_kernel)
            print(verticle_kernel)
            # A kernel of (3 X 3) ones.
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

            #
            # Morphological operation to detect vertical lines from an image
            img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=5)
            verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=5)
            #cv2.imwrite("verticle_lines.jpg",verticle_lines_img)
            # Morphological operation to detect horizontal lines from an image
            img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=5)
            horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=15)
            #cv2.imwrite("horizontal_lines.jpg",horizontal_lines_img)

            #
            #
            # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
            alpha = 0.5
            beta = 1.0 - alpha
            # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
            img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
            img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=1)
            (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            
            # Find contours for image, which will detect all the boxes
            contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # Sort all the contours by top to bottom.
            (contours, boundingBoxes) = self.sort_contours(contours, method="top-to-bottom")

            idx = 0
            img_tru = cv2.imread(tru_img_path,0)
            print("about to remove all files from if already exists"+temp_output_path)
            try:
                shutil.rmtree(temp_output_path)
                shutil.rmtree(old_output_path)
            except Exception as e:
                print(e)
            os.mkdir(temp_output_path)

            bounding_rects = []
            for c in contours:       
                x, y, w, h = cv2.boundingRect(c)    
                if (w > 5 and h > 5) and w >= 1*h:
                    r = {'x':x,'y':y,'w':w,'h':h}
                    n = SimpleNamespace(**r)
                    bounding_rects.append(n)

            # print(bounding_rects)
            dedupe_rects = self.remove_duplicate_blocks(bounding_rects)

            #print(str(c.size))
            #print(boundingBoxes)              
            process_pipeline_file = PipelineFileName(task_file_name=os.path.basename(tru_img_pipeline_file.task_output_file_name))
            res_file = os.path.join(temp_output_path, '{}.csv'.format(os.path.basename(tru_img_path).split('.')[0]))
            with open(res_file, 'w') as f:
                for r in dedupe_rects:
                    # Returns the location and width,height for every contour        
                    idx += 1
                    new_img = img_tru[r.y:r.y+r.h, r.x:r.x+r.w]            
                    process_pipeline_file.segment = "0"
                    process_pipeline_file.segment = str(idx)
                    process_pipeline_file.file_cat = ""
                    new_file = os.path.join(temp_output_path, process_pipeline_file.task_output_file_name)
                    f.write('{},{},{},{},{}\r\n'.format(process_pipeline_file.task_output_file_name, r.y, r.y+r.h, r.x, r.x+r.w))
                    print("writing out ..."+new_file)
                    cv2.imwrite(new_file, new_img)

            # move the processed file
            shutil.move(temp_output_path, output_path)
            move_to =  os.path.join(os.path.dirname(event.src_path), "processed",os.path.basename(event.src_path))
            shutil.move(event.src_path, move_to)        
            move_to =  os.path.join(os.path.dirname(tru_img_path), "processed",os.path.basename(tru_img_path))
            shutil.move(tru_img_path, move_to)
            print ("moved file "+event.src_path+ " to.. "+move_to)
            print ("------------------------------------------------- COMPLETE ---------------------------------------------------------")
        
        except Exception as me:
            print ("------------------------------------------------- EXCEPTION ---------------------------------------------------------")
            print (str(me))
            print("could not process file "+str(event.src_path))
            print ("------------------------------------------------- EXCEPTION ---------------------------------------------------------")



if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(Phase1_1ImageSegmentorHandler(), path=args[0] if args else './phase0-output')
    observer.start()

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()