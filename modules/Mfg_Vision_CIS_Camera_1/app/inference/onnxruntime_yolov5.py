import numpy as np
import onnxruntime as ort
from objdict import ObjDict
import time
import os
from datetime import datetime
import torch
import json
from inference.utils.yolo_onnx_preprocessing_utils import letterbox, non_max_suppression, _convert_to_rcnn_output

providers = [
    'CUDAExecutionProvider',
    'CPUExecutionProvider',
]

class ONNXRuntimeObjectDetection():

    def __init__(self, model_path, classes, target_dim, target_prob, target_iou):
        self.target_dim = target_dim
        self.target_prob = target_prob
        self.target_iou = target_iou
        
        self.device_type = ort.get_device()
        print(f"ORT device: {self.device_type}")

        self.session = ort.InferenceSession(model_path, providers=providers)
        self.sess_input = self.session.get_inputs()
        self.sess_output = self.session.get_outputs()
        print(f"No. of inputs : {len(self.sess_input)}, No. of outputs : {len(self.sess_output)}")

        for idx, input_ in enumerate(range(len(self.sess_input))):
            input_name = self.sess_input[input_].name
            input_shape = self.sess_input[input_].shape
            input_type = self.sess_input[input_].type
            print(f"{idx} Input name : { input_name }, Input shape : {input_shape}, \
            Input type  : {input_type}")  

        for idx, output in enumerate(range(len(self.sess_output))):
            output_name = self.sess_output[output].name
            output_shape = self.sess_output[output].shape
            output_type = self.sess_output[output].type
            print(f" {idx} Output name : {output_name}, Output shape : {output_shape}, \
            Output type  : {output_type}")


        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        batch, channel, height_onnx, width_onnx = self.session.get_inputs()[0].shape
        self.batch = batch
        self.channel = channel
        self.height_onnx = height_onnx
        self.width_onnx = width_onnx
    
        self.classes = classes
        self.num_classes = len(classes)
             
    def predict(self, pp_image, pad_list):
        inputs = pp_image
        # predict with ONNX Runtime
        output_names = [output.name for output in self.sess_output]
        outputs = self.session.run(output_names=output_names, input_feed={self.input_name: inputs})
        filtered_outputs = non_max_suppression(torch.from_numpy(outputs[0]), conf_thres = self.target_prob, iou_thres = self.target_iou)

        def _get_box_dims(image_shape, box):
            box_keys = ['left', 'top', 'width', 'height']
            height, width = image_shape[0], image_shape[1]

            bbox = dict(zip(box_keys, [coordinate.item() for coordinate in box]))

            return bbox
        
        def _get_prediction(label, image_shape, classes):
            
            boxes = np.array(label["boxes"])
            labels = np.array(label["labels"])
            labels = [label[0] for label in labels]
            scores = np.array(label["scores"])
            scores = [score[0] for score in scores]

            pred = []
            for box, label_index, score in zip(boxes, labels, scores):
                box_dims = _get_box_dims(image_shape, box)

                prediction = {  
                    'probability': score.item(),
                    'labelId': label_index.item(),
                    'labelName': classes[label_index],
                    'bbox': box_dims
                }
                pred.append(prediction)

            return pred

        ttl_preds = []
        for result_i, pad in zip(filtered_outputs, pad_list):
            label, image_shape = _convert_to_rcnn_output(result_i, self.height_onnx, self.width_onnx, pad)
            ttl_preds.append(_get_prediction(label, image_shape, self.classes))

        if len(ttl_preds) > 0:
            print(json.dumps(ttl_preds, indent=1))
            return ttl_preds
        else:
            print("No predictions passed the threshold")  
            return []

def log_msg(msg):
    print("{}: {}".format(datetime.now(), msg))

def checkModelExtension(fp):
  ext = os.path.splitext(fp)[-1].lower()
  if(ext != ".onnx"):
    raise Exception(fp, "is an unknown file format. Use the model ending with .onnx format")
  if not os.path.exists(fp):
    raise Exception("[ ERROR ] Path of the onnx model file is Invalid")

def initialize_yolov5(model_path, labels_path, target_dim, target_prob, target_iou):
    print('Loading labels...\n', end='')
    checkModelExtension(model_path)
    with open(labels_path) as f:
        classes = json.load(f)    
    print('Loading model...\n', end='')
    global ort_model
    ort_model = ONNXRuntimeObjectDetection(model_path, classes, target_dim, target_prob, target_iou)
    print('Success!')

def predict_yolov5(img_data, pad_list):
    log_msg('Predicting image')

    t1 = time.time()
    predictions = ort_model.predict(img_data, pad_list)
    t2 = time.time()
    t_infer = (t2-t1)*1000
    response = {
        'created': datetime.utcnow().isoformat(),
        'inference_time': t_infer,
        'predictions': predictions
        }
    return response

def warmup_image(batch_size, warmup_dim):
    for _ in range(batch_size):
        yield np.zeros([warmup_dim, warmup_dim, 3], dtype=np.uint8)

