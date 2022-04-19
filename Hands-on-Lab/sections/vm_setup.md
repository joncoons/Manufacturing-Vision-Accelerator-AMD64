## 1) Set up your Azure VM instance
   
   For this lab, we're going to create a non-GPU VM in Azure (you can also use a dGpu-based machine if you have want) To create a VM, you'll need an Azure subscription.  
   
   If you don't already have a subscription, you can easily create a [free account](https://azure.microsoft.com/free/?WT.mc_id=A261C142F) before you begin.
   
   Once you've logged into the Azure Portal, you can click I the upper left corner of the screen to bring up the menu, and then click add resource. From there you can either choose Virtual Machine, or the Ubuntu 18.04 Server VM option. (I’m using a VM with the SKU of Standard B4ms, which is the default for Ubuntu Server 18.04)
   
   ![](../hol_images/azure_portal.JPG)
    
   In the ‘Create a virtual machine’ blade, you will select your subscription, select or create your Resource Group, create a
   friendly name for your VM, choose the Region and availability options. Since this is temporary deployment, chose ‘No
   infrastructure redundancy required’. 
   
   Since we will be accessing this VM in the HoL remotely, we do want to enable SSH access over Port 22. Under Administrator Account -> Authentication type, choose Password and enter a username and password. We’ll use these quite often
   throughout the HoL, so please make a note of these or create a temporary
   copy of each in your text editor of choice.
   
   Under ‘Public Inbound Ports’ allow selected ports should be already selected with SSH(22) as the selected port.
   
   Since the aim is to use the simplest VM available, we can skip the additional setup blades you would normally go through, and just select the ‘Review & Create’ button. Once validated by the system, select ‘Create’ at the bottom of the
   screen.
   
   This will now create several resources: the virtual machine, a network security group and public IP addresses. When provisioning is complete, select the ‘Go to resource’ button at the bottom.
   
   Copy the Public IP Address in the Overview blade, and save this to your text editor of choice. We’ll use this for accessing the VM remotely via a terminal emulator,
   i.e. TeraTerm or [Windows Terminal](https://www.microsoft.com/en-us/p/windows-terminal/9n0dx20hk701?activetab=pivot:overviewtab).

[Back to HoL main](../Hands-on-Lab.md)