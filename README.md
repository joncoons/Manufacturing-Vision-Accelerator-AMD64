# Manufacturing Vision Accelerator for AMD64 architectures
Welcome to the Manufacuring Vision Accelerator repo - we hope what you find here may be helpful to your pursuit of vision analytics on the Edge!  

This is a sample repository of working code - nothing more, nothing less.  There are no warranties or guarantees stated, or otherwise implied.

# A bit about the 'vision' 

This project was built out of necessity - the need to solve for that 'last mile' connectivity of remote vision workloads, but also solved for the unique challenges of these use cases.  Taking a 'code-first' approach across a number of deep engagements with multiple manufacturing customers, we began to see universal patterns emerge:

1. Build for flexibility:  
Taking a 'code-first' approach meant being deliberate about choices in terms of programming language and the packages used.  For this project, we coded everything in Python, and used only open source elements, such as OpenCV for image capture/manipulation and the Open Neural Network Exchange (ONNX) format for vision models. 

2. Address the 80%:  
Within our vision engagements, we found that 80%+ of the use cases revolved around anomaly detection, so the focus of this repository is on object detection, which could be foreign objects in a production scenario, detection of errors in assembly, safety infractions such as the lack of PPE or a spill/leakage of product.  While image classification and segmentation are also important areas which this repository will expand into eventually, the initial focus is object detection.   We will also, in time, provide patterns for integrating Computer Vision services such as OCR to augement capabilities of a vision system.

3. Plan for model retraining:
What many of the out-of-the-box solutions fail to plan for the eventual need for model retraining.  A vision solution has to have the ability to augement its datasets, as model drift or 'data' drift happens - it's not a question of if, but a question of when.  On the model side, perhaps there is a bias in your classes that gets revealed during production inferencing which requires a rebalancing of the class representation.  On the 'data' side, it could be that a camera gets knocked out of aligment, the lighting in a plant changes or seasonal changes change the available natural light, etc.

4. Always think about the Enterprise perspective:
The other shortcoming we've seen consistently in pre-built solutions is their propensity to create yet another silo in your data estate.  Although the lower layers of the ISA-95 network have traditionally been partially or totally 'airgapped' in Manufacturing, the current trend towards Industry 4.0 has created a paradigm shift to connect OT networks to IT systems.  Vision systems have also traditionally been in that 'air-gapped' mode, but few, if any, have made the transition to Enterprise transparency.  From what we've observed, vision analytics systems provide intrinsic value to the front-line plant engineers and workers, but that unique visibility into operations across an Enterprise has value all the way to the C-suite.  From the supply chain to ERP to MES, visibility changes the way organizations do business for the better.
