import numpy as np
import cv2
import torch
import math
        
from inference.utils.yolo_onnx_preprocessing_utils import letterbox
        
def frame_resize(img, target, model):
    if model in ('yolov5'):
        img_processed_list = []
        pad_list = []
        batch_size = 1
        for i in range(batch_size):
            img0, ratio, pad = letterbox(img, new_shape=target, auto=False, scaleup=False)
            img0 = img0[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3xHxW
            img0 = np.ascontiguousarray(img0)
            np_image = torch.from_numpy(img0)
            np_image = np.expand_dims(np_image, axis=0)
            np_image = np_image.astype(np.float32) / 255.0
            img_processed_list.append(np_image)
            pad_list.append(pad)
        if len(img_processed_list) > 1:
            img_data = np.concatenate(img_processed_list)
        elif len(img_processed_list) == 1:
            img_data = img_processed_list[0]
        else:
            img_data = None
        assert batch_size == img_data.shape[0]
        return img_data, ratio, pad_list

    elif model in ('acv'):
        padColor = [0,0,0]
        h, w = img.shape[:2]
        sh, sw = (target, target)
        if h > sh or w > sw: # shrinking 
            interp = cv2.INTER_AREA
        else: # stretching 
            interp = cv2.INTER_CUBIC
        aspect = w/h  
        # compute scaling and pad sizing
        if aspect > 1: # horizontal image
            new_w = sw
            new_h = np.round(new_w/aspect).astype(int)
            pad_vert = (sh-new_h)/2
            pad_top, pad_bot = np.floor(pad_vert).astype(int), np.ceil(pad_vert).astype(int)
            pad_left, pad_right = 0, 0
        elif aspect < 1: # vertical image
            new_h = sh
            new_w = np.round(new_h*aspect).astype(int)
            pad_horz = (sw-new_w)/2
            pad_left, pad_right = np.floor(pad_horz).astype(int), np.ceil(pad_horz).astype(int)
            pad_top, pad_bot = 0, 0
        else: # square image
            new_h, new_w = sh, sw
            pad_left, pad_right, pad_top, pad_bot = 0, 0, 0, 0
        scaled_frame = cv2.resize(img, (new_w, new_h), interpolation=interp)
        scaled_frame = cv2.copyMakeBorder(scaled_frame, pad_top, pad_bot, pad_left, pad_right, borderType=cv2.BORDER_CONSTANT, value=padColor)        
        return scaled_frame