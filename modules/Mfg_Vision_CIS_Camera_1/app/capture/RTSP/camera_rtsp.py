import os
import sys
import logging
import subprocess
import numpy as np
import cv2
import time
import json
import uuid
from typing import Any, Callable
from datetime import datetime
from capture.frame_preprocess import frame_resize
from capture.frame_save import FrameSave
from store.sql_insert import InsertInference
from PIL import Image

class RTSP_Camera():
    sql_state = 0
    
    def __init__(self, camID, camTrigger, camURI, camLocation, camPosition, camFPS, inferenceFPS, modelACV,
                modelFile, labelFile, targetDim, probThres, iouThres, retrainInterval, SqlDb, SqlPwd, storeRawFrames, storeAllInferences, send_to_upload: Callable[[str], None], send_to_upstream: Callable[[str], None]):

        self.camID = camID
        self.camTrigger = camTrigger
        self.camURI = camURI
        self.camLocation = camLocation
        self.camPosition = camPosition
        self.camFPS = camFPS
        self.inferenceFPS = inferenceFPS
        self.modelACV = modelACV
        self.modelFile = modelFile
        self.labelFile = labelFile
        self.targetDim = targetDim
        self.probThres = probThres
        self.iouThres = iouThres
        self.retrainInterval = retrainInterval
        self.SqlDb = SqlDb
        self.SqlPwd = SqlPwd
        self.storeRawFrames = storeRawFrames
        self.storeAllInferences = storeAllInferences
        self.send_to_upload = send_to_upload
        self.send_to_upstream = send_to_upstream

        self.model_name = modelFile
        self.retry_delay = 2
        self.retry_max = 20
        self.frameCount = 0
        self.frameRateCount = 0
        self.inferenceFrameCount = 0
        self.inferenceCount = 0
        self.inferenceRatio = 0.00
        self.cap = None

        self.cap_RTSP()
 
    def cap_RTSP(self):
        
        self.cap = cv2.VideoCapture(self.camURI)
        if not self.cap.isOpened():
            print('Cannot open RTSP stream - attempting reconnect')
            self.capReconnect()
        while(self.cap.isOpened()):
            _, frame = self.cap.read()
            if _ == True:
                self.frameCount += 1
                self.frameRateCount += 1
                if self.inferenceFPS > 0:
                    if self.frameRateCount == int(self.camFPS/self.inferenceFPS):
                        h, w = frame.shape[:2]
                        print("\n\n Original frame height = {} \n Frame width = {} \n\n ".format(h,w))             
                        frame_optimized = frame_resize(frame, self.targetDim)
                        if self.modelACV:
                            from inference.onnxruntime_predict import predict_acv
                            pil_frame = Image.fromarray(frame_optimized)
                            result = predict_acv(pil_frame)
                        else:
                            from inference.onnxruntime_yolov5 import predict_yolo
                            result = predict_yolo(frame_optimized)
                        # print(json.dumps(result))

                        now = datetime.now()
                        created = now.isoformat()
                        unique_id = str(uuid.uuid4())
                        filetime = now.strftime("%Y%d%m%H%M%S%f")
                        annotatedName = f"{self.camLocation}-{self.camPosition}-{filetime}-annotated.jpg"
                        annotatedPath = os.path.join('/images_volume', annotatedName)
                        frameFileName = f"{self.camLocation}-{self.camPosition}-{filetime}.jpg"
                        frameFilePath = os.path.join('/images_volume', frameFileName)
                        retrainFileName = f"{self.camLocation}-{self.camPosition}-{filetime}.jpg"
                        retrainFilePath = os.path.join('/images_volume', retrainFileName)
                        detection_count = len(result['predictions'])
                        t_infer = result["inference_time"]
                        print(f"Detection Count: {detection_count}")

                        if detection_count > 0:
                            inference_obj = {
                                'model_name': self.model_name,
                                'object_detected': 1,
                                'camera_id': self.camID,
                                'camera_name': f"{self.camLocation}-{self.camPosition}",
                                'raw_image_name': frameFileName,
                                'raw_image_local_path': frameFilePath,
                                'annotated_image_name': annotatedName,
                                'annotated_image_path': annotatedPath,
                                'inferencing_time': t_infer,
                                'created': created,
                                'unique_id': unique_id,
                                'detected_objects': result['predictions']
                                }

                            sql_insert = InsertInference(RTSP_Camera.sql_state, self.SqlDb, self.SqlPwd, detection_count, inference_obj)

                            RTSP_Camera.sql_state = sql_insert                      

                            self.send_to_upstream(json.dumps(inference_obj))

                            annotated_frame = frame_optimized

                            for i in range(detection_count):
                                tag_name = result['predictions'][i]['labelName']
                                probability = round(result['predictions'][i]['probability'],2)
                                bounding_box = result['predictions'][i]['bbox']
                                image_text = f"{tag_name}@{probability}%"
                                color = (0, 255, 0)
                                thickness = 1

                                if bounding_box:
                                    if self.modelACV:
                                        height, width, channel = annotated_frame.shape
                                        xmin = int(bounding_box["left"] * width)
                                        xmax = int((bounding_box["left"] * width) + (bounding_box["width"] * width))
                                        ymin = int(bounding_box["top"] * height)
                                        ymax = int((bounding_box["top"] * height) + (bounding_box["height"] * height))
                                        start_point = (xmin, ymin)
                                        end_point = (xmax, ymax)
                                        annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color, thickness)
                                        annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .6, color = (255,0, 0))
                                    else:
                                        start_point = (int(bounding_box["left"]), int(bounding_box["top"]))
                                        end_point = (int(bounding_box["width"]), int(bounding_box["height"]))
                                        annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color, thickness)
                                        annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .6, color = (255,0, 0))
                                
                            FrameSave(annotatedPath, annotated_frame)
                            annotated_msg = {
                            'fs_name': "images-annotated",
                            'img_name': annotatedName,
                            'location': self.camLocation,
                            'position': self.camPosition,
                            'path': annotatedPath
                            }
                            self.send_to_upload(json.dumps(annotated_msg))
                    
                        elif self.storeAllInferences:
                            print("No object detected.")
                            inference_obj = {
                                'model_name': self.model_name,
                                'object_detected': 0,
                                'camera_id': self.camID,
                                'camera_name': f"{self.camLocation}-{self.camPosition}",
                                'raw_image_name': frameFileName,
                                'raw_image_local_path': frameFilePath,
                                'annotated_image_name': frameFileName,
                                'annotated_image_path': frameFilePath,
                                'inferencing_time': t_infer,
                                'created': created,
                                'unique_id': unique_id,
                                'detected_objects': result['predictions']
                                }
   
                            sql_insert = InsertInference(RTSP_Camera.sql_state, self.SqlDb, self.SqlPwd, detection_count, inference_obj)

                            RTSP_Camera.sql_state = sql_insert            

                            self.send_to_upstream(json.dumps(inference_obj))             
                        
                        print(f"Frame count = {self.frameCount}")
                        
                        self.frameRateCount = 0
                        FrameSave(frameFilePath, frame_optimized)

                        if self.storeRawFrames:
                            frame_msg = {
                            'fs_name': "images-frame",
                            'img_name': frameFileName,
                            'location': self.camLocation,
                            'position': self.camPosition,
                            'path': frameFilePath
                            }
                            self.send_to_upload(json.dumps(frame_msg))

                        if self.frameCount % self.retrainInterval == 0:
                            FrameSave(retrainFilePath, frame)
                            retrain_msg = {
                            'fs_name': "images-retraining",
                            'img_name': retrainFileName,
                            'location': self.camLocation,
                            'position': self.camPosition,
                            'path': retrainFilePath
                            }
                            self.send_to_upload(json.dumps(retrain_msg))
                    
                if self.frameCount == 1000000:
                    self.frameCount = 0
            else:
                print("Can't receive frame (stream end?). Attempting reconnection")  
                self.capReconnect()       
                break
    
    def capReconnect(self):
        time.sleep(self.retry_delay)
        retry_backoff = self.retry_delay
        while self.retry_max:
            self.retry_max -= 1
            try:
                self.cap = cv2.VideoCapture(self.camURI)
                if not self.cap.isOpened():
                    print('Cannot open RTSP stream on reconnect attempt {}'.format(self.retry_max))
                print("Reconnected RTSP stream {}".format(self.camURI))
                break
            except Exception as e:
                print(e)
                retry_backoff = pow(retry_backoff,2)
                time.sleep(retry_backoff)