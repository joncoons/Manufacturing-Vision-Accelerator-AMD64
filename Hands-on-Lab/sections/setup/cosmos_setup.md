
## 4) Set up CosmosDB 

One of the unique challenges of connecting cameras on the Edge is the variability required, as each camera is bespoke in its own way.  Typically, there is a unique IP address, unique location, unique name and other inputs you may want to assign, such as model name and model version.  

You can manage this variability through environment variables in the deployment manifest, but the length of the manifest could potentially become an issue, depending on how many cameras are configured.  The deployment manifest is actually part of the edgeAgent module twin (desired state), and is therefore subject to a 32kb limit for desired/reported states.

To overcome this limitation, we've created an example python application which leverages flask, jinja2, flask-wtf forms and CosmosDB to create a 'desired-state' artifact for the individual module twin for each camera, which then has its own 32kb allocation for 'desired-state.'  

To set up CosmosDB, in the upper left-hand corner of the Azure Portal, select 'Create a resource,' just as you did to set up the VM.  On the 'Create a resource' blade, enter 'Azure Cosmos DB' in the search window, and select the 'Create' button.  In the API option window, selece Core(SQL) as your API choice, and select the 'Create' button.  

In the next "Create Azure Cosmos DB Account - Core (SQL)' window, select your subscription if not already populated.  On the Resource Group line, click the dropdown and select the RG you used for your VM above.  On the Account Name line, enter whatever friendly name you want to choose, and for Location, choose the same region as your VM.

For capacity, we're going to choose Serverless, as this database will have very limited utilization, so consumption-based will be the most cost-effective.  

Since we aren't concerned with the other blades for this Lab, we're going to simply choose 'Review + create' at the bottom of the screen. Once validated, choose 'Create' to spin up your instance of CosmosDB.

Once the resource is created, choose 'Go to resource' as we're going to need a few details from Cosmos for our application.  On the Overview tab, which should be the default tab you navigated to, we'll need the URI for CosmosDB.  If you hover over the URI, a copy symbol will appear to the right.  Copy this and paste it into your text editor of choice, i.e. Notepad.  In the left-hand navigation column, choose Keys.  To access Cosmos and insert the module twin json artifact, we're going to need the Primary Key.  Copy this and put it into your text editor temporarily.

[Back to HoL main](../../Hands-on-Lab.md)