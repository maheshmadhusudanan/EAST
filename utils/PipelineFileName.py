import uuid
from os import path

class PipelineFileName(object):
    
    def __init__(self, original_file_name=None, task_file_name=None, page_num="0", segment="", output_file_ext=".jpg"):
        
        self.output_file_ext = str(output_file_ext)
        
        print("*********** Building pipeline file object "+str(task_file_name) + ","+str(original_file_name))
        if (task_file_name != None):
            file_wo_ext = path.splitext(task_file_name)[0]
            print("deserializing file name = "+file_wo_ext)
            fname_split = file_wo_ext.split("_")
            assert(len(fname_split) >= 3)
            self.original_file_name = None
            uids_parts = fname_split[0].split("-") 
            self.unique_pg_id = str(uids_parts[len(uids_parts)-1])
            self.unique_id = fname_split[0].replace("-"+self.unique_pg_id,"")            
            self.page_num = str(fname_split[1].replace("pg-",""))
            self.segment = str(fname_split[2].replace("sg-",""))            
            self.file_cat = fname_split[3] if len(fname_split) > 3 else ""
        if (original_file_name != None):
            print("!!!!!!!!! building it from original file name!!! "+original_file_name)
            self.original_file_name = original_file_name
            self.unique_id = str(uuid.uuid5(uuid.NAMESPACE_OID,original_file_name))
            self.unique_pg_id = str(uuid.uuid4())[:8]            
            self.page_num = str(page_num)
            self.segment = str(segment)
            self.file_ext = str(path.splitext(original_file_name)[1])
            self.file_cat = ""        


    def to_string(self):
        return "({0}, {1}, {2})".format(self.unique_id, self.unique_pg_id, self.file_ext)

    @property
    def file_cat(self):   
        return self.__file_cat

    @file_cat.setter
    def file_cat(self, v):  
        print("setting file category = "+v)      
        self.__file_cat = v

    @property
    def segment(self):   
        return self.__segment

    @segment.setter
    def segment(self, v):  
        print("setting segment = "+v)
        v = v.strip()      
        self.__segment = "0" if (v == "0" or v == "") else self.segment+"-"+v
    
    @property
    def page_num(self):   
        return self.__page_num

    @page_num.setter
    def page_num(self, v):
        self.__page_num = v
    
    @property
    def file_ext(self):   
        return self.__file_ext

    @file_ext.setter
    def file_ext(self, v):
        self.__file_ext = v

    @property
    def original_file_name(self):   
        return self.__original_file_name

    @original_file_name.setter
    def original_file_name(self, v):
        self.__original_file_name = v

    @property
    def unique_id(self):        
        return self.__unique_id

    @unique_id.setter
    def unique_id(self, v):       
        self.__unique_id = v

    @property
    def unique_pg_id(self):        
        return self.__unique_pg_id

    @unique_pg_id.setter
    def unique_pg_id(self, v):       
        self.__unique_pg_id = v

    @property
    def output_file_ext(self):        
        return self.__output_file_ext

    @output_file_ext.setter
    def output_file_ext(self, v):       
        self.__output_file_ext = v

    @property
    def task_output_file_name(self):        
        return self.unique_id+"-"+self.unique_pg_id+"_pg-"+str(self.page_num) + "_sg-"+str(self.segment) + \
                (("_"+self.file_cat) if self.file_cat != "" else "" )+str(self.output_file_ext)

    @property
    def task_output_folder_name(self):        
        return self.unique_id+"-"+self.unique_pg_id+"_pg-"+str(self.page_num)

    
   
