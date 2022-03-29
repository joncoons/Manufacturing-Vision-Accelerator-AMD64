

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
import threading
from azure.iot.device.aio import IoTHubModuleClient

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def main():
    blob_connstr = os.environ['BLOB_LOCAL_CONNSTR']
    blob_container = os.environ['BLOB_LOCAL_AZURE_FILE_CONTAINER']

    while True:

        files = os.listdir(os.environ['LOCAL_FILE_PATH'])
        for root, dirs, files in os.walk(os.environ['LOCAL_FILE_PATH']):
            if not files:
                continue
            for file in files:
                # print(file)
                local_path = os.path.join(os.environ['LOCAL_FILE_PATH'], root, file)
                azure_path = os.path.join(root.replace(os.environ['LOCAL_FILE_PATH'], ''), file)

                blob_service_client = BlobServiceClient.from_connection_string(blob_connstr, api_version='2019-07-07')
                try:
                    container_client = blob_service_client.create_container(blob_container)
                except Exception as e:
                    pass

                container_client = blob_service_client.get_container_client(blob_container)
                blob_client = container_client.get_blob_client(azure_path)

                blob_client = blob_service_client.get_blob_client(container=blob_container, blob=azure_path)

                file_data = None
                with open(local_path, 'rb') as file:
                    blob_client.upload_blob(file, overwrite=True)
                # print(f'Uploaded from local file {local_path} to Azure Blob storage path {azure_path}')
                #     file_data = file.read()
                        
                # container_client.upload_blob(file, file_data)
        # print('Finished uploading files!\n')
        time.sleep(60)


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
    main()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())