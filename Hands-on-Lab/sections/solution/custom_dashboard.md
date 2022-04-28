## Mfr_Vision_Dashboard_Custom

One of the most requested pieces of functionality from a manufacturing setting is the ability to visualize NRT results from the inferencing at the point of inspection.  This helps plant engineers understand if they have an issue very quickly.

The custom dashboard module is an example of a very simple dashboard that allows you to define, via the deployment manifest, how many cameras you would like to visualize (up to four).  This module queries the last value for the most recent camera used, and surfaces either the annotated image or raw un-annotated frame, along with data about the camera and inference outputs.  It also displays whether or not the image passed or failed, based on the inference output. 

This is included as a simple, getting started dashboard, but could be modified and enhanced to your liking.  Written in python, the module incorporates Flask, Jinja2, HTML and SQL to create the output.  

If you want a more robust dashboard, the Grafana dashboard may be well suited, although it does add a layer of complexity.  Grafana is included in this repository as just an example, not an endorsement, by any means.

[Back to HoL main](../../Hands-on-Lab.md)