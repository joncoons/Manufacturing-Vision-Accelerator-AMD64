## 5) Set up your Twin Configuration Tool 

Perhaps you noticed, there are two very similar folders in the repository - one inside of the 'modules' folder, labeled 'Mfg_Vision_Twin_Configuration_Tool,' and in the root directory, simply labeled 'Module_Twin_Configuration_Tool.'  The only difference between the two is where you choose to run the containerized application tool.  If you would like to run the configuration tool on your Edge device for testing, you can deploy it as part of your manifest.  If you want to run it locally on your desktop, you can choose other directory - build instructions are located at the top of the dockerfile, as well as run instructions.

If you want an 'easy button' and don't want to build the application container, we've stored a copy in an Azure Container Repository with anonymous pull capabilities.  Simply run:  'docker run -d -p 22000:22000 --rm -it visionaccelerator.azurecr.io/iot_edge_configuration_tool:0.0.1-amd64' on your command line or in PowerShell, or add 'sudo' at the beginning if using WSL.

In your web browser, open a window and navigate to 'http://localhost:22000'  This will open to the following screen: 

![](../hol_images/module_config_1.JPG)


[Back to HoL main](../Hands-on-Lab.md)
