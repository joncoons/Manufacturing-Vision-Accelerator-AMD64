import os
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient 
from azure.core.exceptions import ResourceExistsError

class Blob_Upload():

    def __init__(self, fs_name, img_name, img_path, cam_location, cam_position, conn_str):
        self.fs_name = fs_name
        self.img_name = img_name
        self.img_path = img_path
        self.cam_location = cam_location
        self.cam_position = cam_position
        self.conn_str = conn_str

        self.create_connection()
    
    def store_image(self):
        self.create_container()
        try:
            blob_client = container_client.get_blob_client(f"{self.cam_location}/{self.cam_position}/{self.img_name}")
            with open(f'{self.img_path}','rb') as data:
                blob_client.upload_blob(data, blob_type="BlockBlob")
                print(f"Successfully uploaded {self.img_name}")
        except Exception as e:
            print(e)
           
    def create_container(self):
        global container_client
        try:
            container_client = storage_client.create_container(self.fs_name)
        
        except ResourceExistsError as e:
            print(e)
            container_client = storage_client.get_container_client(self.fs_name)
        
    def create_connection(self):
        try:
            global storage_client
            storage_client = BlobServiceClient.from_connection_string(self.conn_str)
            try:
                print ("Uploading file")
                self.store_image()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)