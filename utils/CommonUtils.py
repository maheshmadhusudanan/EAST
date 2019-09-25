import time
import os
import sys
import ntpath
import shutil
import uuid
from types import SimpleNamespace

class CommonUtils(object):

    def get_coords(r):
        return SimpleNamespace(**{"x1":r.x, "x2":r.x+r.w, "y1":r.y, "y2":r.y+r.h  })

    #
    # To check if fit is inside target
    #
    def is_rectangle_inside(target, fit):

        inside = False

        if ((fit.x1 == target.x1) and (fit.x2 == target.x2) and (fit.y1 == target.y1) and (fit.y2 == target.y2)):
            inside = False
        elif ((fit.x1 >= target.x1) and (fit.x2 < target.x2) and (fit.y1 >= target.y1) and (fit.y2 <= target.y2)):                        
            inside = True 
        elif ((fit.x1 > target.x1) and (fit.x2 <= target.x2) and (fit.y1 >= target.y1) and (fit.y2 <= target.y2)):                        
            inside = True        
               
        if inside:
            print("----------------------"+str(inside)+"--------------------------------------")
            print(str(fit.x1) +">="+ str(target.x1)+" = "+str(fit.x1 >= target.x1))
            print(str(fit.y1) +">="+ str(target.y1)+" = "+str(fit.y1 >= target.y1))
            print(str(fit.x2) +"<="+ str(target.x2)+" = "+str(fit.x2 <= target.x2))                        
            print(str(fit.y2) +"<="+ str(target.y2)+" = "+str(fit.y2 <= target.y2))
        
        return inside
    
