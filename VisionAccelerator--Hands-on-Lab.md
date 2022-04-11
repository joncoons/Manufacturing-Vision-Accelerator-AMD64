# Vision Accelerator - Hands-On-Lab 

##1) Set up your Azure VM instance##
   
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

##2) Download Code##
   
   Now for the easiest portion of the HoL -- we're going to download a zip file of this repository.  Just click on the <>Code button and choose the Download Zip option.    On Windows, this will simply download into your Downloads folder - navigate to this folder, and move the zip to a folder of your choosing for your development environment. Go ahead and unzip the contents there.
   
   ![](/hol_images/repo_download.JPG)
   
   For the lab, we'll be using VS Code  - if you don't have a this installed on your PC, it's free to download and use for any  OS, and and be found [here]([Download Visual Studio Code - Mac, Linux, Windows](https://code.visualstudio.com/download)).
   
   In VS Code, go the File -> Open Folder and choose the MANUFACTURING-VISION-ACCELERATOR-AMD64 folder.   This will open the project in your IDE, and we can now walk through the code to give you better idea of how the solution functions.

##3) What exactly does each module do?##

###Mfg_Vision_CIS_Camera_1### <br>
This is the main module we'll be working with to connect to caputure, inference and store (CIS) analysis of individual frames.  This module also handles routing the inference and images to Azure in conjunction with the other modules.

If you open this module folder you'll see three directories, capture, inference, and store.  If you click on capture, you'll see a few different options to choose from.  For machine vision systems in industrial environments, it's more common to see GVSP (GigE Vision Streaming Protocol), also known as GigE (gigabit) cameras, such as Allied Vision, Basler and others.  For convenience, we've included two examples, but you can easily integrate addtional camera SDKs as needed. (We'll cover the Dockerfile coniguration a bit later ih this section.)

We also included a simple OpenCV-based connector for RTSP (Real-Time Streaming Protocol), which is quite common for CCTV/Security cameras.

The last option is for a file-based system, where the camera captures the image and simply stores it to a diretory. This 

4) To DevOps or not to DevOps, that is the question?

5) Train a model

6) Upload sample pictures for testing

7) 


