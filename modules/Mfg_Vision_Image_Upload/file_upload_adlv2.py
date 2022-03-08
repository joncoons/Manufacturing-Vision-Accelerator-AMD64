import os
import time
from azure.storage.filedatalake._models import ContentSettings
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceExistsError

class ADL_G2_Upload():

    def __init__(self, fs_name, img_name, img_path, cam_location, cam_position, conn_str):
        self.fs_name = fs_name
        self.img_name = img_name
        self.img_path = img_path
        self.cam_location = cam_location
        self.cam_position = cam_position
        self.conn_str = conn_str
        self.t_upload_begin = time.time()
        self.t_upload_end = 0
        self.t_upload = 0
        self.create_connection()
    
    def store_image(self):
        self.create_file_system()
        self.create_directory()
        print(f"Image path: {self.img_path}")
        try:
            file_client = directory_client.create_file(self.img_name)
            open_file = open(f'{self.img_path}','rb')
            read_file = open_file.read()
            file_client.append_data(data=read_file, offset=0, length=len(read_file))
            file_client.flush_data(len(read_file))
            self.t_upload_end = time.time()
            self.t_upload = (self.t_upload_end - self.t_upload_begin)*1000
            print("Image upload time: {} milliseconds".format(self.t_upload))

        except Exception as e:
            print(e)
        
    def create_file_system(self):
        global file_system_client
        try:

            file_system_client = storage_client.create_file_system(file_system=self.fs_name)
        
        except ResourceExistsError as e:
            # print(e)
            file_system_client = storage_client.get_file_system_client(self.fs_name)
        
    def create_directory(self):
        global directory_client
        try:
            directory_client = file_system_client.create_directory(f"{self.cam_location}/{self.cam_position}")
        
        except ResourceExistsError as e:
            # print(e)
            directory_client = file_system_client.get_directory_client(f"{self.cam_location}/{self.cam_position}")

    def create_connection(self):
        try:
            global storage_client
            storage_client = DataLakeServiceClient.from_connection_string(self.conn_str)
            try:
                print ("Uploading file")
                self.store_image()
            except Exception as e:
                print(e)
            # finally:
            #     # Graceful exit
            #     storage_client.shutdown()
        except Exception as e:
            print(e)