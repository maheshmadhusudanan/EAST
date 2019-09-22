#!/usr/bin/env python
__author__="Mahesh Madhusudanan"

from flask import Flask, render_template, Response, request, send_file
from flask_cors import CORS
import numpy as np
from flask import json
import os
from os import listdir
from os.path import isfile, join
from utils.PipelineFileName import PipelineFileName
import sys
import pandas as pd
import csv
sys.path.append(os.path.abspath(os.path.join('./utils')))

app = Flask(__name__)
CORS(app)

processed_files_path = os.path.join(".","pipeline","phase0-output","processed")
uploaded_files_path = os.path.join(".","pipeline","phase0-input","processed")
results_files_path = os.path.join(".","pipeline","phase-2-0-output")

@app.route("/textext/files", methods=['GET'])
def get_all_processed_files():
    try:
        onlyfiles = [f for f in listdir(processed_files_path) if isfile(join(processed_files_path, f))]

        tree_items = []
        item = {'id':"", 'title':"", 'isLeaf':False, "children":None}
        child_item = item.copy()        
        current_file = ""
        pgs = []
        for f in onlyfiles:            
            if "_M." in f:
                continue            
            pf = PipelineFileName(task_file_name=f)
            if current_file != pf.unique_id:
                new_item = item.copy()                
                current_file = pf.unique_id
                print("processing.."+current_file)
                new_item['id'] = pf.unique_id
                new_item['title'] = pf.unique_id 
                new_item['children'] = []               
                tree_items.append(new_item)

            new_child = child_item.copy()
            new_child['id'] = str(pf.page_num+"-"+pf.unique_pg_id)
            new_child['title'] = "Page-"+str(pf.page_num)
            new_child['isLeaf'] = True
            new_child['children'] = None
            new_item['children'].append(new_child)   

        upload_files = [f for f in listdir(uploaded_files_path) if isfile(join(uploaded_files_path, f))]
        for uf in upload_files: 
            puf = PipelineFileName(original_file_name=uf)
            for pitem in tree_items:           
                # print("checking "+str(pitem['id'])+" ...with ..."+str(puf.unique_id))     
                if pitem['id'] == puf.unique_id:
                    pitem['title'] = uf
                        
        response = app.response_class(response=json.dumps(tree_items),
                                        status=200,
                                        mimetype='application/json')  
    except Exception as e:
        response = app.response_class(response=json.dumps(e),
                                status=500,
                                mimetype='application/json')

    return response

@app.route("/textext/file/<file_id>/page/<page_id>", methods=['GET'])
def get_file_by_id(file_id, page_id):
    try:
        unique_pg_id = page_id.split("-")[1]
        results_csv = os.path.join(results_files_path, file_id+"-"+unique_pg_id+"_pg-"+page_id.split("-")[0]+"-Final.csv")
        results_df = pd.read_csv(results_csv, error_bad_lines=False, quoting=csv.QUOTE_NONE, encoding='utf-8')

        results_df.drop(results_df.columns[[0]], axis=1, inplace=True)
        results_df.replace(np.nan, "", inplace=True)
        response = app.response_class(response=json.dumps(results_df.to_dict('records')),
                                status=200,
                                mimetype='application/json')    
    except Exception as e:
        response = app.response_class(response=json.dumps(e),
                                status=500,
                                mimetype='application/json')

    return response

@app.route("/textext/view/<file_id>/page/<page_id>", methods=['GET'])
def get_file_by_preview(file_id, page_id):
    try:
        unique_pg_id = page_id.split("-")[1]
        file_name_view = os.path.join(processed_files_path, file_id+"-"+unique_pg_id+"_pg-"+page_id.split("-")[0]+"_sg-0"+".jpg")
        
        return send_file(file_name_view, mimetype='image/jpeg')

    except Exception as e:
        return app.response_class(response=json.dumps(e),
                                status=500,
                                mimetype='application/json')

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007,debug=False)
