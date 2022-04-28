## Mfg_Vision_Model_Repo Module

The model repo is used as as another variability abstraction from the CIS module, so that a model change or version update doesn't require a push of the CIS module, just an update of the module twin.

Model naming happens at the directory level within the model folder, and each unique model will have its own directory.  This is similar to the Model Repo structure Nvidia uses for their [Triton Inference Server](https://github.com/triton-inference-server/server/blob/main/docs/model_repository.md), except the label files sit adjacent to the model definition file (ONNX file), as label files can (and do) change.  

This was puposely done for forward flexibility, in case you would want to leverage Nvidia's server at some future point.  Triton can manage multiple model instances and multiple-gpu resources across both image and traditional tabular models.

If you look at the deployment manifest, you'll notice there are both docker binds and volume mounts in the create options for many of the containers.  In the case of the module repo, this gives the container the ability to not only store the models locally in the identified host directory, but also to share this information across the deployed containers.  In this way the CIS modules automatically see the model and label files as though they were part of the container.


[Back to HoL main](../../Hands-on-Lab.md)
