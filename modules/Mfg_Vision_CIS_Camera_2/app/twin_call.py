   
import os
import time
import pickle
from azure.iot.device import IoTHubModuleClient

class TwinUpdater():

    def __init__(self) -> None:
        
        self.client = IoTHubModuleClient.create_from_edge_environment()
        self.client.connect()
        print("Client connected")
        twin_read = self.client.get_twin()
        print(twin_read)
        self.twin_to_config(twin_read)

    def twin_to_config(self, twin_raw):
        twin_dict = self.twin_parse(twin_raw)
        config_write = open("/config/variables.pkl", "wb")
        pickle.dump(twin_dict, config_write)
        config_write.close()
        print(f"Config file written")
        self.client.shutdown()

    def twin_parse(self, twin_data):
        twin_variables = {
            "CAMERA_GVSP_ALLIED": twin_data["desired"]["CAMERA_GVSP_ALLIED"],
            "CAMERA_GVSP_BASLER": twin_data["desired"]["CAMERA_GVSP_BASLER"],
            "CAMERA_RTSP": twin_data["desired"]["CAMERA_RTSP"],
            "CAMERA_FILE": twin_data["desired"]["CAMERA_FILE"],
            "CAMERA_ID": twin_data["desired"]["CAMERA_ID"],
            "CAMERA_TRIGGER": twin_data["desired"]["CAMERA_TRIGGER"],
            "CAMERA_URI": twin_data["desired"]["CAMERA_URI"],
            "CAMERA_LOCATION": twin_data["desired"]["CAMERA_LOCATION"],
            "CAMERA_POSITION": twin_data["desired"]["CAMERA_POSITION"],
            "CAMERA_FPS": twin_data["desired"]["CAMERA_FPS"],
            "INFERENCE_FPS": twin_data["desired"]["INFERENCE_FPS"],
            "MODEL_ACV": twin_data["desired"]["MODEL_ACV"],
            "MODEL_FILE": twin_data["desired"]["MODEL_FILE"],
            "LABEL_FILE": twin_data["desired"]["LABEL_FILE"],
            "TARGET_DIM": twin_data["desired"]["TARGET_DIM"] ,
            "PROB_THRES": twin_data["desired"]["PROB_THRES"],
            "IOU_THRES": twin_data["desired"]["IOU_THRES"],
            "RETRAIN_INTERVAL": twin_data["desired"]["RETRAIN_INTERVAL"],
            "STORE_RAW_FRAMES": twin_data["desired"]["STORE_RAW_FRAMES"],
            "STORE_ALL_INFERENCES": twin_data["desired"]["STORE_ALL_INFERENCES"] ,
            "MSSQL_DB": twin_data["desired"]["MSSQL_DB"],
            "MSSQL_PWD": twin_data["desired"]["MSSQL_PWD"]
        }
        
        return twin_variables
