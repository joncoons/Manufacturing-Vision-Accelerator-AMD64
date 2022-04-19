## 3) Set up an Azure Container Repository

In the portal, click in the upper left corner and select 'Create a resource,' and in the search window, enter 'Container Registry'.  In the drop down window, select Container Registry, and select the 'Create' button on the next screen.

In the 'Create a resource > Container Registry' screen, select your subscription, if not already populated, and select the same Resource Group you used for the VM.  Enter a friendly name for your ACR, and choose the Region you used for your VM.   For SKU, you can choose Standard, which is the default.

For the purposes of the Lab, we're going to use the defaults for the remaining tabs, so just select 'Review + create' at the bottom of the screen.  Once validated, select 'Create' to deploy your instance of Azure Container Registry.

Once this is created, select the 'Go to resource' link, which will navigate you to the ACR resource.  In the left-hand navigation column, select the 'Access keys' link, which will open new blade with the Registry name and Login server poluplated.  Toggle the 'Admin user' setting to enabled, which will now populate the Username and password/password2 fields.  We're going to copy the Login server, Username and password values over to our text editor for use later on, as we need to authenticate to the service before we can store containerized workloads.


[Back to HoL main](../../Hands-on-Lab.md)
