# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import os
import sys
import signal
import threading
import json
from azure.iot.device.aio import IoTHubModuleClient
from file_upload_adlv2 import ADL_G2_Upload
from file_upload_blob import Blob_Upload


# Event indicating client stop
stop_event = threading.Event()

def create_client():
    client = IoTHubModuleClient.create_from_edge_environment()
    async def receive_message_handler(message):
        if message.input_name in ("inputImageSend"):
            message = message.data
            msg_str = message.decode('utf-8')
            print(msg_str)
            msg_json = json.loads(msg_str)
            fs_name = msg_json.get('fs_name')
            img_name = msg_json.get('img_name')
            location = msg_json.get('location')
            position = msg_json.get('position')
            path = msg_json.get('path')
            if ADL_G2:
                ADL_G2_Upload(fs_name, img_name, path, location, position, STORE_CONN_STR)
            else:
                Blob_Upload(fs_name, img_name, path, location, position, STORE_CONN_STR)

    try:
        # Set handler on the client
        client.on_message_received = receive_message_handler
    except:
        # Cleanup if failure occurs
        client.shutdown()
        raise
    return client

async def run_sample(client):
    # Customize this coroutine to do whatever tasks the module initiates
    # e.g. sending messages
    while True:
        await asyncio.sleep(1000)

def main():
    if not sys.version >= "3.5.3":
        raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
    print ( "IoT Hub Client for Python" )
    

    # NOTE: Client is implicitly connected due to the handler being set on it
    client = create_client()

    # Define a handler to cleanup when module is is terminated by Edge
    def module_termination_handler(signal, frame):
        print ("IoTHubClient sample stopped by Edge")
        stop_event.set()

    # Set the Edge termination handler
    signal.signal(signal.SIGTERM, module_termination_handler)

    # Run the sample
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_sample(client))
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    finally:
        print("Shutting down IoT Hub Client...")
        loop.run_until_complete(client.shutdown())
        loop.close()

def __convertStringToBool(env: str) -> bool:
    if env in ['true', 'True', 'TRUE', '1', 'y', 'YES', 'Y', 'Yes']:
        return True
    elif env in ['false', 'False', 'FALSE', '0', 'n', 'NO', 'N', 'No']:
        return False
    else:
        raise ValueError('Could not convert string to bool.')

if __name__ == "__main__":
    try:
        ADL_G2 = __convertStringToBool(os.environ["ADL_G2"])
        STORE_CONN_STR = os.environ["STORE_CONN_STR"]
    except ValueError as error:
        print(error)
        sys.exit(1)
    main()
    
