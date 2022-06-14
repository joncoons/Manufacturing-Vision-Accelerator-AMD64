## Mfg_Vision_Image_Upload Module

This module is handles the upload of images to your storage in Azure, and offers the flexibility of using either Azure Blob Storage or Azure Data Lake Generation 2.  If you're utilizing Azure Machine Learning to train your models, it makes it incredibly simple to connect your data as a datastore.  You choose your path in the deployment manifest by setting a boolean value, and connection string.

Given the superior user experience with a hierarchichical namespace, Azure Data Lake Gen 2 is the route most popular, although you will need to establish a service principle in Azure AD to access service from AML.

For the simplicity of the HoL, however, we're going to use a simple blob storage with uname/pwd authentication.

The main.py file in this module is a light modification of the bootstrap code generated when you create a new module.  It receives image path data via an IoT Edge route sent from the CIS module(s) and will upload this to pre-determined directories, which can, as with the entire solution, be modified to fit whatever nomenclature you want to utilize.  

Based on the boolean value set in the deployment manifest, the code will either call the 'file_upload_adlv2.py' or the 'file_upload_blob.py' to execute.

You can easily check your storage resource either in the portal or with the [Azure Storage Explorer](https://docs.microsoft.com/en-us/azure/vs-azure-tools-storage-manage-with-storage-explorer?tabs=linux)<br><br>





[Back to HoL main](../../Hands-on-Lab.md)