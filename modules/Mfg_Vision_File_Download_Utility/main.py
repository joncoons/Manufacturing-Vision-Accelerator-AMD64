# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
from six.moves import input
import threading

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def main():
    while True:

        blob_connstr = os.environ['BLOB_CLOUD_CONNSTR']
        blob_container = os.environ['BLOB_AZURE_FILE_DOWNLOAD_CONTAINER']

        blob_service_client = BlobServiceClient.from_connection_string(blob_connstr, api_version='2019-07-07')
        try:
            container_client = blob_service_client.create_container(blob_container)
        except Exception as e:
            pass

        container_client = blob_service_client.get_container_client(blob_container)

        for blob in container_client.list_blobs():
            if not os.path.isfile(os.path.join(os.environ['LOCAL_FILE_PATH'], blob['name'])):
                data = container_client.download_blob(blob['name']).readall()
                with open(os.path.join(os.environ['LOCAL_FILE_PATH'], blob['name']), 'wb') as file:
                    file.write(data)

        time.sleep(60)


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
    main()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())
