import os
from re import L
import sys
import pickle
import json
import pyodbc
from cachetools import TTLCache
from threading import Thread
from time import sleep
from datetime import datetime
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

def sql_connect():
    with pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};PORT='+sql_port+';SERVER='+sql_server+';DATABASE='+sql_db+';UID='+sql_uid+';PWD='+ sql_pwd) as sql_conn:
        sql_conn.autocommit = True
        print("SQL connected")
        cursor = sql_conn.cursor()
        return cursor
        
def q_camera():
    q_0 = _sql.execute(f'WITH CTE AS (SELECT DISTINCT camera_id FROM InferenceData) SELECT TOP ({CAMS_TO_DISPLAY}) camera_id FROM CTE ORDER BY camera_id ASC')
    q_0_results = q_0.fetchall()
    return q_0_results

def q_inference(camera_id):
    q_1 = _sql.execute("""SELECT TOP(1) a.model_name, a.object_detected, a.camera_id, a.camera_name, 
    a.annotated_image_name, ROUND(a.inferencing_time,2), a.created, a.unique_id FROM InferenceData 
    AS a WHERE a.camera_id = ? ORDER BY a.created DESC""", camera_id)
    q_1_results = q_1.fetchall()
    return q_1_results

def q_detections(unique_id):
    q_2 = _sql.execute("""SELECT b.tag_name, ROUND(b.probability,2), b.unique_id FROM DetectionData AS b WHERE b.unique_id = ? """, unique_id)
    q_2_results = q_2.fetchall() 
    return q_2_results

def q_pass_fail():
    q_3 = _sql.execute("SELECT COUNT(a.object_detected) FROM InferenceData AS a WHERE a.object_detected = ? ", 0)
    q_3_results = q_3.fetchone()
    p_count = len(q_3_results)
    for p in range(p_count):
        p_val = q_3_results[p]
    q_4 = _sql.execute("SELECT COUNT(a.object_detected) FROM InferenceData AS a WHERE a.object_detected = ? ", 1)
    q_4_results = q_4.fetchone()
    f_count = len(q_4_results)
    for p in range(f_count):
        f_val = q_4_results[p]
    return (p_val, f_val)

def list_to_dict(keys, values):
    zip_k_v = zip(keys, values)
    new_dict = dict(zip_k_v)
    return new_dict

@app.route('/', methods=['GET', 'POST'])
def index():
    global _sql
    _sql = sql_connect()
    inf_keys = ['model_name', 'object_detected', 'camera_id', 'camera_name', 'annotated_image_name', 'inferencing_time', 'created', 'unique_id']
    det_keys = ['tag_name', 'probability', 'unique_id']
    inf_list = []
    det_list = []
    now = datetime.now()
    utc_now = datetime.utcnow()
    print(utc_now)
    print(now)
    cams = q_camera() 
    for cam in cams:        
        inf_vals = q_inference(cam)
        inf_count = len(inf_vals)
        print(inf_count)
        for inf_val in inf_vals:
            inf_dict = list_to_dict(inf_keys, inf_val)
            inf_list.append(inf_dict)
            inf_unique_id = inf_dict['unique_id']
            det_vals = q_detections(inf_unique_id)
            for det_val in det_vals:
                det_dict = list_to_dict(det_keys, det_val)
                det_list.append(det_dict)
    inf_count = (len(inf_list))
    det_count = (len(det_list))

    p,f = q_pass_fail()

    return render_template('index.html', inf_count=inf_count, det_count = det_count, inf_list = inf_list, det_list=det_list, p=p, f=f)

if __name__ == '__main__':

    try:
        CAMS_TO_DISPLAY = int(os.environ["CAMS_TO_DISPLAY"])
        sql_db = os.environ['MSSQL_DB']
        sql_pwd = os.environ['MSSQL_SA_PASSWORD']
        
    except ValueError as error:
        print(error)
        sys.exit(1)
        
    sql_server = 'localhost'
    sql_port = '1433'
    sql_uid = 'SA'
    print('DRIVER={ODBC Driver 17 for SQL Server};PORT='+sql_port+';SERVER='+sql_server+';DATABASE='+sql_db+';UID='+sql_uid+';PWD='+ sql_pwd)

    app.run(host='0.0.0.0', port=23000)


