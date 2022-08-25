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
from shapely.geometry import Polygon

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

        self.work_boundary = [(0, 640), (0, 0), (220, 0), (220, 640)]

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
                        self.frameRateCount = 0
                        h, w = frame.shape[:2]
                        if self.modelACV:
                            frame_optimized = frame_resize(frame, self.targetDim, model = "acv")
                            from inference.onnxruntime_predict import predict_acv
                            pil_frame = Image.fromarray(frame_optimized)
                            result = predict_acv(pil_frame)
                            predictions = result['predictions']
                            frame_resized = frame_optimized.copy()
                            annotated_frame = frame_optimized.copy()
                        else:
                            frame_optimized, ratio, pad_list = frame_resize(frame, self.targetDim, model = "yolov5")
                            from inference.onnxruntime_yolov5 import predict_yolov5
                            result = predict_yolov5(frame_optimized, pad_list)
                            predictions = result['predictions'][0]
                            new_w = int(ratio[0]*w)
                            new_h = int(ratio[1]*h)
                            frame_resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
                            annotated_frame = frame_resized.copy()

                        now = datetime.now()
                        created = now.isoformat()
                        unique_id = str(uuid.uuid4())
                        filetime = now.strftime("%Y%d%m%H%M%S%f")
                        annotatedName = f"{self.camLocation}-{self.camPosition}-{filetime}-annotated.jpg"
                        annotatedPath = os.path.join('/images_volume', annotatedName)
                        frameFileName = f"{self.camLocation}-{self.camPosition}-{filetime}-rawframe.jpg"
                        frameFilePath = os.path.join('/images_volume', frameFileName)
                        retrainFileName = f"{self.camLocation}-{self.camPosition}-{filetime}-retrain.jpg"
                        retrainFilePath = os.path.join('/images_volume', retrainFileName)
                        
                        if result is not None:
                            print(json.dumps(result))

                        if predictions is not None:
                            detection_count = len(predictions)
                            t_infer = result["inference_time"]
                            print(f"Detection Count: {detection_count}")

                        if detection_count > 0:
                            # t_route_iothub_begin = time.time()
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
                                'detected_objects': predictions
                                }

                            sql_insert = InsertInference(RTSP_Camera.sql_state, self.SqlDb, self.SqlPwd, detection_count, inference_obj)
                            RTSP_Camera.sql_state = sql_insert                      
                            self.send_to_upstream(json.dumps(inference_obj))   

                            # For establishing boundary area - comment out if not used
                            boundary_active = self.__convertStringToBool(os.environ['BOUNDARY_DETECTION'])
                            work_polygon = Polygon(self.work_boundary)
                            object_poly_list = []                          

                            for i in range(detection_count):
                                bounding_box = predictions[i]['bbox']
                                tag_name = predictions[i]['labelName']
                                probability = round(predictions[i]['probability'],2)
                                
                                # /////////////////////////////////////
                                # Simple object detection bounding box
                                # 
                                image_text = f"{probability}%"
                                color = (0, 255, 0)
                                thickness = 1
                                if bounding_box:
                                    if self.modelACV:
                                        height, width, channel = annotated_frame.shape
                                        xmin = int(bounding_box["left"] * width)
                                        xmax = int((bounding_box["left"] * width) + (bounding_box["width"] * width))
                                        ymin = int(bounding_box["top"] * height)
                                        ymax = int((bounding_box["top"] * height) + (bounding_box["height"] * height))
                                    else:
                                        xmin = int(bounding_box["left"])
                                        xmax = int(bounding_box["width"])
                                        ymin = int(bounding_box["top"])
                                        ymax = int(bounding_box["height"])
                                    start_point = (int(bounding_box["left"]), int(bounding_box["top"]))
                                    end_point = (int(bounding_box["width"]), int(bounding_box["height"]))
                                    annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color, thickness)
                                    # annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (255,0, 0))

                                # /////////////////////////////////////
                                # Simple workplace saftey PPE detection example code
                                # 
                                # image_text = f"{probability}%"
                                # color1 = (0, 0, 255)
                                # color2 = (0, 255, 0)
                                # thickness1 = 1
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
                                #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,0,255))
                                #         else:
                                #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color2, thickness2)
                                #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,255,0))
                                #     else:
                                #         start_point = (int(bounding_box["left"]), int(bounding_box["top"]))
                                #         end_point = (int(bounding_box["width"]), int(bounding_box["height"]))
                                #         if tag_name == "no_hardhat" or tag_name == "no_safety_vest":
                                #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color1, thickness1)
                                #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,0,255))
                                #         else:
                                #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color2, thickness2)
                                #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,255,0))
                                    
                                # /////////////////////////////////////
                                # Object Detection for PPE with Boundary Area Identification
                                #
                                # image_text = f"{probability}%"
                                # color1 = (0, 0, 255)
                                # color2 = (0, 255, 0)
                                # thickness1 = 1
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
                                #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,0,255))
                                #         else:
                                #             annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color2, thickness2)
                                #             annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,255,0))
                                #     else:
                                #         if boundary_active:
                                #             poly_red = (0, 0, 255)
                                #             poly_yellow = (0, 255, 255)
                                #             poly_black = (0, 0, 0)
                                #             poly_white = (255, 255, 255)
                                #             point1 = (int(bounding_box["left"]), int(bounding_box["top"]))
                                #             point2 = (int(bounding_box["width"]), int(bounding_box["top"]))
                                #             point3 = (int(bounding_box["width"]), int(bounding_box["height"]))
                                #             point4 = (int(bounding_box["left"]), int(bounding_box["height"]))
                                #             object_boundary = [(point1),(point2), (point3), (point4)]
                                #             print("object_boundary: ", object_boundary)
                                #             object_polygon = Polygon(object_boundary)
                                #             if object_polygon.intersects(work_polygon):
                                #                 object_poly_list.append(object_boundary)
                                #             start_point = (int(bounding_box["left"]), int(bounding_box["top"]))
                                #             end_point = (int(bounding_box["width"]), int(bounding_box["height"]))
                                #             if tag_name == "no_hardhat" or tag_name == "no_safety_vest":
                                #                 annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color1, thickness1)
                                #                 # annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,0,255))
                                #             else:
                                #                 annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color2, thickness2)
                                #                 # annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,255,0))

                                #         else:
                                #             start_point = (int(bounding_box["left"]), int(bounding_box["top"]))
                                #             end_point = (int(bounding_box["width"]), int(bounding_box["height"]))
                                #             if tag_name == "no_hardhat" or tag_name == "no_safety_vest":
                                #                 annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color1, thickness1)
                                #                 annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,0,255))
                                #             else:
                                #                 annotated_frame = cv2.rectangle(annotated_frame, start_point, end_point, color2, thickness2)
                                #                 annotated_frame = cv2.putText(annotated_frame, image_text, start_point, fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = .4, color = (0,255,0))
                                # 
                            # Code for creating polygon overlay - comment out if not using boundary detection
                            # if len(object_poly_list) > 0:
                            #     cv2.polylines(annotated_frame, np.array([self.work_boundary]), False, poly_yellow, 3)
                            #     overlay = annotated_frame.copy()
                            #     poly_arr = np.array(object_poly_list)
                            #     print(f'Poly/NP Array: {poly_arr}')
                            #     # cv2.fillPoly(overlay, np.array([self.work_boundary]), poly_white)
                            #     cv2.fillPoly(overlay, poly_arr, poly_red)
                            #     alpha = 0.4
                            #     annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0)
                        
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
                                'detected_objects': predictions
                                }
    
                            sql_insert = InsertInference(RTSP_Camera.sql_state, self.SqlDb, self.SqlPwd, detection_count, inference_obj)
                            RTSP_Camera.sql_state = sql_insert            
                            self.send_to_upstream(json.dumps(inference_obj))

                        print(f"Frame count = {self.frameCount}")
                        FrameSave(frameFilePath, frame_resized)

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
                print("Reconnecting RTSP stream {}".format(self.camURI))
                break
            except Exception as e:
                print(e)
                retry_backoff = pow(retry_backoff,2)
                time.sleep(retry_backoff)

    def __convertStringToBool(self, env: str) -> bool:
        if env in ['true', 'True', 'TRUE', '1', 'y', 'YES', 'Y', 'Yes']:
            return True
        elif env in ['false', 'False', 'FALSE', '0', 'n', 'NO', 'N', 'No']:
            return False
        else:
            raise ValueError('Could not convert string to bool.')