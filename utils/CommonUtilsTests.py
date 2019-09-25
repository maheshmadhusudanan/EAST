import time  
import os
import sys
import ntpath
import shutil
import uuid
from types import SimpleNamespace
import unittest
sys.path.append(os.path.abspath(os.path.join('.')))
from CommonUtils import CommonUtils


class CommonUtilsTests(unittest.TestCase):

     def test_is_rectangle_inside(self):
        		
        smallRect = {'x1':850,'y1':185,'x2':1648,'y2':349}
        bigRect = {'x1':47,'y1':114,'x2':1652,'y2':386}                
        br1 = SimpleNamespace(**bigRect)
        sm1 = SimpleNamespace(**smallRect)
        
        assert CommonUtils.is_rectangle_inside(br1,sm1) == True

if __name__ == '__main__':
    unittest.main()


   