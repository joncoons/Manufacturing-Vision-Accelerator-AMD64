import os
import json
import sys
import time
import uuid
from io import BytesIO
from PIL import Image
from time import sleep
from typing import Any, Callable, Optional
import cv2
import numpy as np
from datetime import datetime
from pypylon import pylon
from pypylon import genicam
from capture.frame_preprocess import frame_resize
from capture.frame_save import FrameSave
from store.sql_insert import InsertInference

class Basler_GVSP_Camera:
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

        self.frameCount = 0
        self.frameRateCount = 0

        global capturing
        self.capturing = False

        self.streamCap()

    def streamCap(self):
        while True:

            cam_info = pylon.DeviceInfo()
            cam_info.SetSerialNumber(self.camURI)
            camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(cam_info))
            # camera.open()

            # Grabing Continusely (video) with minimal delay
            camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
            converter = pylon.ImageFormatConverter()

            # converting to opencv bgr format
            converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

            while camera.IsGrabbing():
                grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                if grabResult.GrabSucceeded():
                    # Access the image data
                    print("SizeX: ", grabResult.Width)
                    print("SizeY: ", grabResult.Height)

                    image = converter.Convert(grabResult)
                    frame = image.GetArray()
                    # frame = cv2.cvtColor(frame, cv2.COLOR_BAYER_RG2RGB)
                    frame_optimized = frame_resize(frame, self.targetDim)

                    if self.camTrigger:
                        pass
                    else:
                        if self.inferenceFPS > 0:
                            if self.frameRateCount == int(self.camFPS/self.inferenceFPS): 
                                self.frameRateCount = 0 
                                pass   
                    
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

                        sql_insert = InsertInference(Basler_GVSP_Camera.sql_state, self.SqlDb, self.SqlPwd, detection_count, inference_obj)

                        Basler_GVSP_Camera.sql_state = sql_insert                      

                        self.send_to_upstream(json.dumps(inference_obj))

                        annotated_frame = frame_optimized

                        for i in range(detection_count):
                            tag_name = result['predictions'][i]['labelName']
                            probability = round(result['predictions'][i]['probability'],2)
                            bounding_box = result['predictions'][i]['bbox']
                            
                            # Workplace saftey detection example code
                            # image_text = f"{probability}%"
                            # color1 = (0, 0, 255)
                            # color2 = (0, 255, 0)
                            # thickness1 = 2
                            # thickness2 = 1
                            # if bounding_box:
                            #     if self.modelACV:
                            #         height, width, channel = annotated_frame.shape
                            #         xmin = int(bounding_box["left"] * width)
                            #         xmax = int((bounding_box["left"] * width) + (bounding_box["width"] * width))
                            #         ymin = int(bounding_box["top"] * height)
                            #         ymax = int((bounding_box["top"] * height) + (bounding_box["height"] * height))
                            #         start_point = (xmin, ymin)
                            #         end_point = (xmax, ymax)
                            #         if tag_name == "no_hardhat" or tag_name == "no_safety_vest":
                            #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color1, thickness1)
                            #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .5, color = (0,0,255))
                            #         else:
                            #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color2, thickness2)
                            #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .5, color = (0,255,0))
                            #     else:
                            #         start_point = (int(bounding_box["left"]), int(bounding_box["top"]))
                            #         end_point = (int(bounding_box["width"]), int(bounding_box["height"]))
                            #         if tag_name == "no_hardhat" or tag_name == "no_safety_vest":
                            #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color1, thickness1)
                            #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .5, color = (0,0,255))
                            #         else:
                            #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color2, thickness2)
                            #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .5, color = (0,255,0))
                                        
                            # Defect Detection example code
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

                        sql_insert = InsertInference(Basler_GVSP_Camera.sql_state, self.SqlDb, self.SqlPwd, detection_count, inference_obj)

                        Basler_GVSP_Camera.sql_state = sql_insert            

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