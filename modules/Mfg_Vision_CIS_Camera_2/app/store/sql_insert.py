from datetime import datetime
import time
import pyodbc
import json

pyodbc.pooling = False

class InsertInference():

    def __init__(self, sql_state, sql_db, sql_pwd, detection_count, inference):
        now = datetime.now()
        self.sql_db = sql_db
        self.sql_pwd = sql_pwd
        self.model_name = str(inference['model_name'])
        self.object_detected = str(inference['object_detected'])
        self.camera_id = str(inference['camera_id'])
        self.camera_name = str(inference['camera_name'])
        self.raw_image_name = str(inference['raw_image_name'])
        self.raw_image_path = str(inference['raw_image_local_path'])
        self.annotated_image_name = str(inference['annotated_image_name'])
        self.annotated_image_path = str(inference['annotated_image_path'])
        self.inferencing_time = str(inference['inferencing_time'])
        self.created = now
        self.unique_id = str(inference['unique_id'])
        self.detections = inference['detected_objects']
        self.detection_count = detection_count

        self.tag_name = "none"
        self.tag_id = "-1"
        self.probability = "-1.0"
        self.bbox = "none"

        self.t_begin = time.time()
        self.t_end = time.time()
        self.t_insert = 0

        self.sql_state = sql_state
        print(f"SQL package:  {json.dumps(inference)}")
        self.create_record()
    
    def create_record(self):  
        if self.sql_state == 0:
            self.create_db()

        with pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};PORT=1433;SERVER=localhost;UID=SA;PWD=Sm&8jZX*WSkJL2j%27XT;DATABASE=DefectDB') as sql_conn:
            print('Connected to DB')
            sql_conn.autocommit = True
            cursor = sql_conn.cursor()

            if self.sql_state == 0:

                create_inference_tbl = """IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'InferenceData' AND type = 'U') CREATE TABLE InferenceData (id INT NOT NULL IDENTITY PRIMARY KEY, 
                            model_name VARCHAR(60), object_detected BIT, camera_id VARCHAR(40), camera_name VARCHAR(40), raw_image_name VARCHAR(100), raw_image_local_path VARCHAR(100), 
                            annotated_image_name VARCHAR(100), annotated_image_path VARCHAR(100), inferencing_time FLOAT, created DATETIME, unique_id VARCHAR(40));"""

                create_detections_tbl = """IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DetectionData' AND type = 'U') CREATE TABLE DetectionData (id INT NOT NULL IDENTITY PRIMARY KEY, 
                            tag_name VARCHAR(100), tag_id INT, probability FLOAT, bbox VARCHAR(120), unique_id VARCHAR(40));"""
                
                cursor.execute(create_inference_tbl)

                cursor.execute(create_detections_tbl)

                print("Created tables")

            cursor.execute("""INSERT into DefectDB.dbo.InferenceData
                        (model_name, object_detected, camera_id, camera_name, raw_image_name, raw_image_local_path,
                        annotated_image_name, annotated_image_path, inferencing_time, created, unique_id) 
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
                                    self.model_name,
                                    self.object_detected,
                                    self.camera_id,
                                    self.camera_name,
                                    self.raw_image_name,
                                    self.raw_image_path,
                                    self.annotated_image_name,
                                    self.annotated_image_path,
                                    self.inferencing_time,
                                    self.created,
                                    self.unique_id)
                                )
            i = int(0)
            print(type(self.detections))
            if self.detection_count > 0:
                for i in range(int(self.detection_count)):
                    self.tag_id = self.detections[i]['labelId']
                    self.tag_name = self.detections[i]['labelName']
                    self.probability = round(self.detections[i]['probability'],2)
                    self.bbox = self.detections[i]['bbox']
                    cursor.execute("INSERT into DefectDB.dbo.DetectionData (tag_name, tag_id, probability, bbox, unique_id) VALUES (?,?,?,?,?)", 
                            (
                            str(self.tag_name),
                            str(self.tag_id),
                            str(self.probability),
                            str(self.bbox),
                            self.unique_id)
                        )
            else:
                cursor.execute("INSERT into DefectDB.dbo.DetectionData (tag_name, tag_id, probability, bbox, unique_id) VALUES (?,?,?,?,?)", 
                            (
                            str(self.tag_name),
                            str(self.tag_id),
                            str(self.probability),
                            str(self.bbox),
                            self.unique_id)
                        )

            self.t_end = time.time()
            self.t_insert = (self.t_end - self.t_begin)*1000
            print("Insert Time in ms: {}".format(self.t_insert))

            return 1

    def create_db(self):
        with pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};PORT=1433;SERVER=localhost;UID=SA;PWD=Sm&8jZX*WSkJL2j%27XT') as sql_conn:
            sql_conn.autocommit = True
            cursor = sql_conn.cursor()
            cursor.execute("SELECT name FROM master.dbo.sysdatabases where name='DefectDB'")
            data = cursor.fetchone()
            if not data:
                cursor.execute("CREATE DATABASE DefectDB")
                print('Creating Database')
            else:
                print('Database currently exists')
