#!/usr/bin/env python3
import psutil
import subprocess

def run_pipeline_task(py_task):
    
    if py_task == None:
        raise ValueError("*** pidfile_path is required !!")
    
    CMD = ['python', py_task]

    for process in psutil.process_iter():
        # print("checking proc id = "+str(process.cmdline()) +"has...."+str(py_task))
        if py_task in process.cmdline():
            print('Process found. Terminating ....'+py_task)
            try:                
                process.terminate()
                process.kill()
            except Exception as ex:                
                print(ex)
            break        
    
    print("Sarting py process ...."+py_task)
    proc = subprocess.Popen(CMD, shell=False)
    # proc.communicate()
    
    
    pass

if __name__ == "__main__":
    
    print(" starting bynd ocr pipeline.......")
    run_pipeline_task("phase-0-pdf-to-img-conversion.py")
    run_pipeline_task("phase-1-0-img-line-contour-extractor.py")
    run_pipeline_task("phase-1-1-img-segmentor.py")
    run_pipeline_task("phase-2-0-img-to-text-extractor.py")
    run_pipeline_task("phase-3-0-text-grouper.py")




  