# Vision Accelerator - Hands-On-Lab 

### Initial Setup Steps
[1. Set up your Azure VM](sections/setup/vm_setup.md) <br>
[2. Set up your IoT Hub](sections/setup/iothub_setup.md) <br>
[3. Set up your Azure Container Registry](sections/setup/acr_setup.md) <br>
[4. Set up your CosmosDB](sections/setup/cosmos_setup.md) <br>
[5. Set up your Module Twin Configuration app](sections/setup/configuration_tool_setup.md) <br>
[6. Download this code repo](sections/setup/code_download.md)<br>

<br>
[Set up IoT Edge on your VM - External Link](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-provision-single-device-linux-symmetric?view=iotedge-2020-11&tabs=azure-portal%2Cubuntu)<br><br>


### Solution Walkthrough - what exactly does each module do?

[1. Mfg_Vision_CIS_Camera_1 module](sections/solution/cis_module.md)<br>


### Mfg_Vision_CIS_Camera_1 <br>
This is the main module we'll be working with to connect to caputure, inference and store (CIS) analysis of individual frames.  This module also handles routing the inference and images to Azure in conjunction with the other modules.

If you open this module folder you'll see three directories, capture, inference, and store.  If you click on capture, you'll see a few different options to choose from.  For machine vision systems in industrial environments, it's more common to see GVSP (GigE Vision Streaming Protocol), also known as GigE (gigabit) cameras, such as Allied Vision, Basler and others.  For convenience, we've included two examples, but you can easily integrate addtional camera SDKs as needed. (We'll cover the Dockerfile coniguration a bit later ih this section.)

We also included a simple OpenCV-based connector for RTSP (Real-Time Streaming Protocol), which is quite common for CCTV/Security cameras.

The last option is for a file-based system, where the camera captures the image and simply stores it to a diretory. The python code works as a file watcher, processing the image when uploaded. This is the example we'll be using for this lab, as we won't have a physical camera connected.  This code is also useful in a test environment as part of a CI/CD pipeline.

To start examining the code, let's look at the twin_call.py file. The purpose of this code is to create a connection to edgeHub or IoT Hub in Azure via 'IoTHubModuleClient.create_from_edge_environment()' and harvest the desired state twin information from the module twin in the 'twin_parse' function inside of the 'TwinUpdater' class.  In the 'twin_to_config' function, we're saving the dictionary object output of the 'twin_to_config' functions into a pickle file, variables.pkl, within /config directory of the container.

![](/hol_images/twin_to_config.JPG)

Corresponding to saving the 'variable.pkl' file, in the deployment manifest, you'll also notice an entry in the "Mfg_Vision_CIS_Camera_1" module under "Binds" that references this directory also.  This effectively stores a copy of the variables.pkl in the 'edge_assets' directory that gets automatically created on your Edge device.

![](/hol_images/dm_cis_cam_1.JPG)

Moving to the main.py file, at the very bottom you'll notice that main.py invokes two defined threads - thread1 calls the 'TwinUpdater' class, which blocks until complete, and thread2, which starts the 'run_CIS' function.  

![](/hol_images/main_cis_1.JPG)

The 'run_CIS' function loads the variable.pkl file from the /config, and creates variables for each value which are then passed through to the CaptureInferenceStore class, which, depending on the values, then executes the appropriate code for the camera type in the 'capture' directory. 

![](/hol_images/main_cis_2.JPG)

The HubConnector class builds off of an example from Emmanuel Bertrand's Custom Vision Service repo on Github.
The original repo can be found at https://github.com/Azure-Samples/Custom-vision-service-iot-edge-raspberry-pi  This creates a callable function to handle routing both to other modules and $upstream to IoT Hub.

![](/hol_images/main_cis_3.JPG)

The 'inference' directory contains three files - two which handle the output tensor from Azure Custom Vision's ONNX export, and one that inteprets the output of a YOLOv5 object detection model, created in Azure Machine Learning AutoML for Images and exported to ONNX.

Within the module folder, there are two Dockerfiles present - one for GPU acceleration using Nvidia and one for CPU acceleration for AVX2/AVX512 capable processors.  Within each of these are comments regarding which files to include/excluded depending on your target camera hardware.  Please note that to run any of the vision examples, you will need a processor capable of at least AVX2 (Advanced Vector Instruction)

We'll go a bit more indepth on this module in the accompanying video.


### Mfg_Vision_CIS_Camera_1 <br>



4) To DevOps or not to DevOps, that is the question?

5) Train a model

6) Upload sample pictures for testing

7) 


