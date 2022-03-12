import os
import pickle
from typing import Any, Union
from threading import Thread
from time import sleep
from twin_call import TwinUpdater
from azure.iot.device import IoTHubModuleClient, Message

class HubConnector():

    def __init__(self):
        self.client = IoTHubModuleClient.create_from_edge_environment()
        self.client.connect()

    def send_to_output(self, message: Union[Message, str], outputQueueName: str):
        self.client.send_message_to_output(message, outputQueueName)

def send_to_upload(msg_str: str) -> None:
    message = Message(bytearray(msg_str, 'utf-8'))
    hub_connector.send_to_output(message, "outputImageSend")

def send_to_upstream(msg_str: str) -> None:
    message = Message(bytearray(msg_str, 'utf-8'))
    hub_connector.send_to_output(message, "outputInference")

class CaptureInferenceStore():

    def __init__(self, camGvspAllied, camGvspBasler, camRTSP, camFile, camID, camTrigger, camURI, camLocation, camPosition, camFPS, inferenceFPS, modelACV,
                modelYOLOv5, modelName, modelVersion, targetDim, probThres, iouThres, retrainInterval, storeRawFrames, storeAllInferences, SqlDb, SqlPwd):

        modelPath = f'/model_volume/{modelName}/{modelVersion}/model.onnx'
        labelPath = f'/model_volume/{modelName}/{modelVersion}/labels.txt'
        modelFile = f'{modelName}-v.{modelVersion}'
        labelFile = 'labels.txt'
        sleep(5)
        if modelACV:
            from inference.onnxruntime_predict import initialize_acv
            initialize_acv(modelPath, labelPath)
        else:
            from inference.onnxruntime_yolov5 import initialize_yolov5
            initialize_yolov5(modelPath, labelPath, targetDim, probThres, iouThres)
        sleep(1)

        if camGvspAllied:     
            from capture.allied.camera_gvsp_allied import Allied_GVSP_Camera
            Allied_GVSP_Camera(camID, camTrigger, camURI, camLocation, camPosition, camFPS, inferenceFPS, modelACV, modelFile, labelFile, 
                targetDim, probThres, iouThres, retrainInterval, SqlDb, SqlPwd, storeRawFrames, storeAllInferences, send_to_upload, send_to_upstream)

        if camGvspBasler:     
            from capture.basler.camera_gvsp_basler import Basler_GVSP_Camera
            Basler_GVSP_Camera(camID, camTrigger, camURI, camLocation, camPosition, camFPS, inferenceFPS, modelACV, modelFile, labelFile, 
                targetDim, probThres, iouThres, retrainInterval, SqlDb, SqlPwd, storeRawFrames, storeAllInferences, send_to_upload, send_to_upstream)
            
        elif camRTSP:
            from capture.RTSP.camera_rtsp import RTSP_Camera
            RTSP_Camera(camID, camTrigger, camURI, camLocation, camPosition, camFPS, inferenceFPS, modelACV, modelFile, labelFile, 
                targetDim, probThres, iouThres, retrainInterval, SqlDb, SqlPwd, storeRawFrames, storeAllInferences, send_to_upload, send_to_upstream)

        elif camFile:
            from capture.file.camera_file import Cam_File_Sink
            Cam_File_Sink(camID, camTrigger, camURI, camLocation, camPosition, camFPS, inferenceFPS, modelACV, modelFile, labelFile, 
                targetDim, probThres, iouThres, retrainInterval, SqlDb, SqlPwd, storeRawFrames, storeAllInferences, send_to_upload, send_to_upstream)

        else:
            print("No camera found")
 
def __convertStringToBool(env: str) -> bool:
    if env in ['true', 'True', 'TRUE', '1', 'y', 'YES', 'Y', 'Yes']:
        return True
    elif env in ['false', 'False', 'FALSE', '0', 'n', 'NO', 'N', 'No']:
        return False
    else:
        raise ValueError('Could not convert string to bool.')

def run_CIS():

    global hub_connector
    try:
        hub_connector = HubConnector()
    except Exception as err:
        print(f"Unexpected error {err} from IoTHub")

    config_read = open("/config/variables.pkl", "rb")
    variables = pickle.load(config_read)
    print(f"Variables: \n{variables}")

    if variables["CAMERA_FPS"]:
        CAMERA_FPS = float(variables["CAMERA_FPS"])
    else: 
        CAMERA_FPS = float(1)

    if variables["INFERENCE_FPS"]:
        INFERENCE_FPS = float(variables["INFERENCE_FPS"])
    else: 
        INFERENCE_FPS = float(1)

    os.environ["IOU_THRES"] = variables["IOU_THRES"]
    os.environ['TARGET_DIM'] = variables["TARGET_DIM"]
    os.environ["PROB_THRES"] = variables["PROB_THRES"]

    CaptureInferenceStore(
        camGvspAllied = (variables["CAMERA_GVSP_ALLIED"]), 
        camGvspBasler = (variables["CAMERA_GVSP_BASLER"]),
        camRTSP = (variables["CAMERA_RTSP"]), 
        camFile = (variables["CAMERA_FILE"]), 
        camID = variables["CAMERA_ID"],
        camTrigger = (variables["CAMERA_TRIGGER"]), 
        camURI = variables["CAMERA_URI"], 
        camLocation = variables["CAMERA_LOCATION"], 
        camPosition = variables["CAMERA_POSITION"], 
        camFPS = CAMERA_FPS, 
        inferenceFPS = INFERENCE_FPS, 
        modelACV = variables["MODEL_ACV"],
        modelYOLOv5 = variables["MODEL_YOLOV5"],
        modelName = variables["MODEL_NAME"], 
        modelVersion = variables["MODEL_VERSION"], 
        targetDim = int(variables["TARGET_DIM"]), 
        probThres = float(variables["PROB_THRES"]), 
        iouThres = float(variables["IOU_THRES"]), 
        retrainInterval = int(variables["RETRAIN_INTERVAL"]), 
        storeRawFrames = (variables["STORE_RAW_FRAMES"]), 
        storeAllInferences = (variables["STORE_ALL_INFERENCES"]), 
        SqlDb = variables["MSSQL_DB"], 
        SqlPwd = variables["MSSQL_PWD"],
        )
        
def twin_update():
    TwinUpdater()

thread1 = Thread(name='twin_update',target=twin_update)
thread2 = Thread(name='run_CIS', target=run_CIS)

if __name__ == "__main__":
    thread1.start()
    thread1.join()
    # sleep(5)
    thread2.start()

    
