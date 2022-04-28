## Mfg_Vision_CIS_Camera_1 Module

The model repo is used as as another variability abstraction from the CIS module, so that a model change or version update doesn't require a push of the CIS module, just an update of the module twin.

Model naming happens at the directory level within the model folder, and each unique model will have its own directory.  This is similar to the Model Repo structure Nvidia uses for their [Triton Inference Server](https://github.com/triton-inference-server/server/blob/main/docs/model_repository.md), except the label files sit adjacent to the model definition file (ONNX file), as label files can (and do) change.  

This was puposely done for forward flexibility, in case you want to leverage Nvidia's server, which can manage multiple-gpu resources very efficiently in the futrure.

[Back to HoL main](../../Hands-on-Lab.md)