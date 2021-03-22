import time
from PIL import Image
import torch


def detect_yolov5(images):
    # Model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
    names = model.names

    # # Images
    # dir = 'https://github.com/ultralytics/yolov5/raw/master/data/images/'
    # imgs = [dir + f for f in ('zidane.jpg', 'bus.jpg')]  # batch of images
    # imgs = [path]
    # print(f'Images: {imgs}')

    # Inference
    t0 = time.monotonic()
    results = model(images)
    t1 = time.monotonic()

    pred = results.pred
    det_str = ''
    detection_results = []
    for i, det in enumerate(pred):
        image_detections = []
        if len(det):  # if detections found
            # detection info
            image_detections = []
            for detection in det:
                print(detection)
                xy0 = detection[0:2]
                xy1 = detection[2:4]
                conf = detection[4]
                label = names[int(detection[5])]
                r = {
                    'xy0': xy0,
                    'xy1': xy1,
                    'conf': conf,
                    'label': label
                }
                image_detections.append(r)

            # detection summary
            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()  # detections per class
                det_str += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

        detection_results.append(image_detections)

    # generate image array results
    result_imgs = []
    for result in results.render():
        result_imgs.append(Image.fromarray(result))

    return {
        'inference_time_sec': t1 - t0,
        'detection_summary': det_str,
        'detections': detection_results
    }