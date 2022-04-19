# Vision Accelerator - Hands-On-Lab 

### [1. Set up your Azure VM](sections/vm_setup.md)
### [2. Set up your IoT Hub](sections/iothub_setup.md)
### [3. Set up your Azure Container Registry](sections/acr_setup.md)
### [4. Set up your CosmosDB](sections/cosmos_setup.md)
### [5. Set up your Module Twin Configuration app](sections/configuration_tool_setup.md)


## 1) Set up your Azure VM instance
   
   For this lab, we're going to create a non-GPU VM in Azure (you can also use a dGpu-based machine if you have want) To create a VM, you'll need an Azure subscription.  
   
   If you don't already have a subscription, you can easily create a [free account](https://azure.microsoft.com/free/?WT.mc_id=A261C142F) before you begin.
   
   Once you've logged into the Azure Portal, you can click I the upper left corner of the screen to bring up the menu, and then click add resource. From there you can either choose Virtual Machine, or the Ubuntu 18.04 Server VM option. (I’m using a VM with the SKU of Standard B4ms, which is the default for Ubuntu Server 18.04)
   
   ![](/hol_images/azure_portal.JPG)
    
   In the ‘Create a virtual machine’ blade, you will select your subscription, select or create your Resource Group, create a
   friendly name for your VM, choose the Region and availability options. Since this is temporary deployment, chose ‘No
   infrastructure redundancy required’. 
   
   Since we will be accessing this VM in the HoL remotely, we do want to enable SSH access over Port 22. Under Administrator Account -> Authentication type, choose Password and enter a username and password. We’ll use these quite often
   throughout the HoL, so please make a note of these or create a temporary
   copy of each in your text editor of choice.
   
   Under ‘Public Inbound Ports’ allow selected ports should be already selected with SSH(22) as the selected port.
   
   Since the aim is to use the simplest VM available, we can skip the additional setup blades you would normally go through, and just select the ‘Review & Create’ button. Once validated by the system, select ‘Create’ at the bottom of the
   screen.
   
   This will now create several resources: the virtual machine, a network security group and public IP addresses. When provisioning is complete, select the ‘Go to
   resource’ button at the bottom.
   
   Copy the Public IP Address in the Overview blade, and save this to your text editor of choice. We’ll use this for accessing the VM remotely via a terminal emulator,
   i.e. TeraTerm or [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab).

## 2) Set up IoT Hub

In the portal, click in the upper left corner and select 'Create a resource,' and in the search window, enter 'IoT Hub'.  In the drop down window, select IoT Hub, and select the 'Create' button on the next screen.

In the 'Create a resource > IoT Hub' screen, select your subscription, if not already populated, and select the same Resource Group you used for the VM.  Enter a friendly name for your IoT Hub, and take note of this - we'll need it later on.  Copy the IoT Hub name you chose, and paste this into your text editor of choice.  Lastly, choose the Region you used for your VM. 

For the purposes of the Lab, we're going to use the defaults for the remaining tabs, so just select 'Review + create' at the bottom of the screen.  Once validated, select 'Create' to deploy your instance of IoT Hub.

Once this is created, select the 'Go to resource' link, which will navigate you to the IoT Hub.  In the left-hand navigation column for IoT Hub, select the 'Shared access policies' link.  Once this populates, select the 'iothubowner' link and copy the 'Primary connection string' from the pop-out blade.  Go ahead and paste this in the same text editor, as we'll need this in a later step.

While we're in the IoT Hub resource, let's go ahead and set up our IoT Edge device.  In the left-hand navigation column, select IoT Edge, and then select the 'Add IoT Edge Device' link.  This will open a 'Create a device' blade where you can enter your Device ID.  Leave the Symmetric Key highlighted and the Connect this device to an IoT Hub enabled.  We won't be utilizing any child devices, so you can ignore this setting, and select the 'Save' button at the bottom of the screen.

This will automatically navigate back to the IoT Edge device list, which should now have your new Edge device listed.  Select your device, and a new blade of device information will open, allowing you to copy the 'Primary Connection String' for your Edge device.  Go ahead and paste this into your text editor as well - we'll use it for provisioning in a later step.

## 2) Set up an Azure Container Repository

In the portal, click in the upper left corner and select 'Create a resource,' and in the search window, enter 'Container Registry'.  In the drop down window, select Container Registry, and select the 'Create' button on the next screen.

In the 'Create a resource > Container Registry' screen, select your subscription, if not already populated, and select the same Resource Group you used for the VM.  Enter a friendly name for your ACR, and choose the Region you used for your VM.   For SKU, you can choose Standard, which is the default.

For the purposes of the Lab, we're going to use the defaults for the remaining tabs, so just select 'Review + create' at the bottom of the screen.  Once validated, select 'Create' to deploy your instance of Azure Container Registry.

Once this is created, select the 'Go to resource' link, which will navigate you to the ACR resource.  In the left-hand navigation column, select the 'Access keys' link, which will open new blade with the Registry name and Login server poluplated.  Toggle the 'Admin user' setting to enabled, which will now populate the Username and password/password2 fields.  We're going to copy the Login server, Username and password values over to our text editor for use later on, as we need to authenticate to the service before we can store containerized workloads.

## 3) Set up CosmosDB 

One of the unique challenges of connecting cameras on the Edge is the variability required, as each camera is bespoke in its own way.  Typically, there is a unique IP address, unique location, unique name and other inputs you may want to assign, such as model name and model version.  

You can manage this variability through environment variables in the deployment manifest, but the length of the manifest could potentially become an issue, depending on how many cameras are configured.  The deployment manifest is actually part of the edgeAgent module twin (desired state), and is therefore subject to a 32kb limit for desired/reported states.

To overcome this limitation, we've created an example python application which leverages flask, jinja2, flask-wtf forms and CosmosDB to create a 'desired-state' artifact for the individual module twin for each camera, which then has its own 32kb allocation for 'desired-state.'  

To set up CosmosDB, in the upper left-hand corner of the Azure Portal, select 'Create a resource,' just as you did to set up the VM.  On the 'Create a resource' blade, enter 'Azure Cosmos DB' in the search window, and select the 'Create' button.  In the API option window, selece Core(SQL) as your API choice, and select the 'Create' button.  

In the next "Create Azure Cosmos DB Account - Core (SQL)' window, select your subscription if not already populated.  On the Resource Group line, click the dropdown and select the RG you used for your VM above.  On the Account Name line, enter whatever friendly name you want to choose, and for Location, choose the same region as your VM.

For capacity, we're going to choose Serverless, as this database will have very limited utilization, so consumption-based will be the most cost-effective.  

Since we aren't concerned with the other blades for this Lab, we're going to simply choose 'Review + create' at the bottom of the screen. Once validated, choose 'Create' to spin up your instance of CosmosDB.

Once the resource is created, choose 'Go to resource' as we're going to need a few details from Cosmos for our application.  On the Overview tab, which should be the default tab you navigated to, we'll need the URI for CosmosDB.  If you hover over the URI, a copy symbol will appear to the right.  Copy this and paste it into your text editor of choice, i.e. Notepad.  In the left-hand navigation column, choose Keys.  To access Cosmos and insert the module twin json artifact, we're going to need the Primary Key.  Copy this and put it into your text editor temporarily.

## 3) Set up your Twin Configuration Tool 

Perhaps you noticed, there are two very similar folders in the repository - one inside of the 'modules' folder, labeled 'Mfg_Vision_Twin_Configuration_Tool,' and in the root directory, simply labeled 'Module_Twin_Configuration_Tool.'  The only difference between the two is where you choose to run the containerized application tool.  If you would like to run the configuration tool on your Edge device for testing, you can deploy it as part of your manifest.  If you want to run it locally on your desktop, you can choose other directory - build instructions are located at the top of the dockerfile, as well as run instructions.

If you want an 'easy button' and don't want to build the application container, we've stored a copy in an Azure Container Repository with anonymous pull capabilities.  Simply run:  'docker run -d -p 22000:22000 --rm -it visionaccelerator.azurecr.io/iot_edge_configuration_tool:0.0.1-amd64' on your command line or in PowerShell, or add 'sudo' at the beginning if using WSL.

In your web browser, open a window and navigate to 'http://localhost:22000'  This will open to the following screen: 

![](/hol_images/module_config_1.JPG)




## 4) Download the Code
   
   Now for the easiest portion of the HoL -- we're going to download a zip file of this repository.  Just click on the <>Code button and choose the Download Zip option.    On Windows, this will simply download into your Downloads folder - navigate to this folder, and move the zip to a folder of your choosing for your development environment. Go ahead and unzip the contents there.
   
   ![](/hol_images/repo_download.JPG)
   
   For the lab, we'll be using VS Code  - if you don't have a this installed on your PC, it's free to download and use for any  OS, and and be found [here]([Download Visual Studio Code - Mac, Linux, Windows](https://code.visualstudio.com/download)).
   
   In VS Code, go the File -> Open Folder and choose the MANUFACTURING-VISION-ACCELERATOR-AMD64 folder.   This will open the project in your IDE, and we can now walk through the code to give you better idea of how the solution functions.

## 5) Solution Walkthrough - what exactly does each module do?

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


