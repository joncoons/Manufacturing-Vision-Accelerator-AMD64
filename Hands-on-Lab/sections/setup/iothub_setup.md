## 2) Set up IoT Hub

In the portal, click in the upper left corner and select 'Create a resource,' and in the search window, enter 'IoT Hub'.  In the drop down window, select IoT Hub, and select the 'Create' button on the next screen.

In the 'Create a resource > IoT Hub' screen, select your subscription, if not already populated, and select the same Resource Group you used for the VM.  Enter a friendly name for your IoT Hub, and take note of this - we'll need it later on.  Copy the IoT Hub name you chose, and paste this into your text editor of choice.  Lastly, choose the Region you used for your VM. 

For the purposes of the Lab, we're going to use the defaults for the remaining tabs, so just select 'Review + create' at the bottom of the screen.  Once validated, select 'Create' to deploy your instance of IoT Hub.

Once this is created, select the 'Go to resource' link, which will navigate you to the IoT Hub.  In the left-hand navigation column for IoT Hub, select the 'Shared access policies' link.  Once this populates, select the 'iothubowner' link and copy the 'Primary connection string' from the pop-out blade.  Go ahead and paste this in the same text editor, as we'll need this in a later step.

While we're in the IoT Hub resource, let's go ahead and set up our IoT Edge device.  In the left-hand navigation column, select IoT Edge, and then select the 'Add IoT Edge Device' link.  This will open a 'Create a device' blade where you can enter your Device ID.  Leave the Symmetric Key highlighted and the Connect this device to an IoT Hub enabled.  We won't be utilizing any child devices, so you can ignore this setting, and select the 'Save' button at the bottom of the screen.

This will automatically navigate back to the IoT Edge device list, which should now have your new Edge device listed.  Select your device, and a new blade of device information will open, allowing you to copy the 'Primary Connection String' for your Edge device.  Go ahead and paste this into your text editor as well - we'll use it for provisioning in a later step.

[Back to HoL main](../../Hands-on-Lab.md)

