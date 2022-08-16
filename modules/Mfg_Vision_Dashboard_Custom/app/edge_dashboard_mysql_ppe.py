import os, sys
import mysql.connector as msql
# import mariadb as msql
# import mysqlx
from datetime import datetime
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

class Connect_MySQL():

    def __init__(self, host, port, user, password, database) -> None:

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        # self.connect_params = {
        #     "host": self.host,
        #     "port": self.port,
        #     "user": self.user,
        #     "password": self.password,
        #     "database": self.database
        #     }
        
        # print(self.connect_params)
        
    def q_camera(self):
        with msql.connect(host=f"{self.host}", user=f"{self.user}", password=f"{self.password}", database=f"{self.database}") as mysql_conn:
            print('Connected to DB')
            cursor = mysql_conn.cursor()

            cursor.execute(f'SELECT DISTINCT camera_id FROM inference_data ORDER BY camera_id ASC LIMIT {CAMS_TO_DISPLAY}')
            q_0_results = cursor.fetchall()
            cursor.close()

            print(q_0_results)
            return q_0_results

    def q_inference(self, camera_id):
        with msql.connect(host=f"{self.host}", user=f"{self.user}", password=f"{self.password}", database=f"{self.database}") as mysql_conn:
            cursor = mysql_conn.cursor()
            cursor.execute("""SELECT model_name, object_detected, camera_id, camera_name, 
            annotated_image_name, ROUND(inferencing_time,2), created, unique_id FROM inference_data 
            WHERE camera_id = %s ORDER BY id DESC LIMIT 1""", camera_id)
            q_1_results = cursor.fetchall()
            print(q_1_results)
            cursor.close()
        return q_1_results

    def q_detections(self, unique_id):
        uniqueId = (unique_id,)
        with msql.connect(host=f"{self.host}", user=f"{self.user}", password=f"{self.password}", database=f"{self.database}") as mysql_conn:
            cursor = mysql_conn.cursor()
            cursor.execute("SELECT tag_name, probability, unique_id FROM detection_data WHERE unique_id = %s", uniqueId)
            q_2_results = cursor.fetchall() 
            print(q_2_results)
            cursor.close()
        return q_2_results

    def q_pass_fail(self):
        with msql.connect(host=f"{self.host}", user=f"{self.user}", password=f"{self.password}", database=f"{self.database}") as mysql_conn:
            cursor = mysql_conn.cursor()
            cursor.execute("SELECT COUNT(tag_name) FROM detection_data WHERE tag_name = 'hardhat' OR tag_name = 'safety_vest' ")
            q_3_results = cursor.fetchone()
            print(q_3_results)
            cursor.close()
            p_count = len(q_3_results)
            for p in range(p_count):
                p_val = q_3_results[p]
            cursor2 = mysql_conn.cursor()
            cursor2.execute("SELECT COUNT(tag_name) FROM detection_data WHERE tag_name = 'no_hardhat' OR tag_name = 'no_safety_vest' ")
            q_4_results = cursor2.fetchone()
            print(q_4_results)
            cursor2.close()
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
    inf_keys = ['model_name', 'object_detected', 'camera_id', 'camera_name', 'annotated_image_name', 'inferencing_time', 'created', 'unique_id']
    det_keys = ['tag_name', 'probability', 'unique_id']
    inf_list = []
    det_list = []
    now = datetime.now()
    utc_now = datetime.utcnow()
    print(utc_now)
    print(now)
    cams = _mysql.q_camera() 
    for cam in cams:        
        inf_vals = _mysql.q_inference(cam)
        inf_count = len(inf_vals)
        print(inf_count)
        for inf_val in inf_vals:
            inf_dict = list_to_dict(inf_keys, inf_val)
            inf_unique_id = inf_dict['unique_id']
            det_vals = _mysql.q_detections(inf_unique_id)
            fail_count = 0
            for det_val in det_vals:
                if det_val[0] == "no_hardhat" or det_val[0] == "no_safety_vest":
                    fail_count += 1
                det_dict = list_to_dict(det_keys, det_val)
                det_list.append(det_dict)
            print(f"Fail Count: {fail_count}")
            inf_dict['fail_count'] = fail_count
            inf_list.append(inf_dict)
    inf_count = (len(inf_list))
    det_count = (len(det_list))

    p,f = _mysql.q_pass_fail()

    return render_template('index.html', inf_count=inf_count, det_count = det_count, inf_list = inf_list, det_list=det_list, p=p, f=f)

if __name__ == '__main__':
    try:
        CAMS_TO_DISPLAY = int(os.environ["CAMS_TO_DISPLAY"])
        MYSQL_DATABASE = os.environ["MYSQL_DATABASE"]
        MYSQL_USER = os.environ["MYSQL_USER"]
        MYSQL_PWD = os.environ["MYSQL_PWD"]
    except ValueError as error:
        print(error)
        sys.exit(1)

    _mysql = Connect_MySQL(            
        host = "127.0.0.1",
        port = "3306",
        user= f"{MYSQL_USER}",
        password = f"{MYSQL_PWD}",
        database = f"{MYSQL_DATABASE}"
    )

    app.run(host='0.0.0.0', port=23000)


