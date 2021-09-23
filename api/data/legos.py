import os
import time

import matplotlib.pyplot as plt
import numpy as np
import cv2
from PIL import Image

# from .lego_cnn import lego
from .lego_cnn.mrcnn.config import Config
from api.data.lego_cnn.mrcnn import model as modellib, visualize

import logging
from django.conf import settings


def color_map(N=256, normalized=False):
    def bitget(byteval, idx):
        return ((byteval & (1 << idx)) != 0)

    dtype = 'float32' if normalized else 'uint8'
    cmap = np.zeros((N, 3), dtype=dtype)
    for i in range(N):
        r = g = b = 0
        c = i
        for j in range(8):
            r = r | (bitget(c, 0) << 7 - j)
            g = g | (bitget(c, 1) << 7 - j)
            b = b | (bitget(c, 2) << 7 - j)
            c = c >> 3

        cmap[i] = np.array([r, g, b])

    cmap = cmap / 255 if normalized else cmap
    return cmap


def display_results(image, boxes, masks, class_ids, class_names, scores=None,
                    show_mask=True, show_bbox=True, display_img=False,
                    save_img=False, save_dir=None, img_name=None):
    """
    boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
    masks: [height, width, num_instances]
    class_ids: [num_instances]
    class_names: list of class names of the dataset (Without Background)
    scores: (optional) confidence scores for each box
    show_mask, show_bbox: To show masks and bounding boxes or not
    display_img: To display the image in popup
    save_img: To save the predict image
    save_dir: If save_img is True, the directory where you want to save the predict image
    img_name: If save_img is True, the name of the predict image

    """
    n_instances = boxes.shape[0]
    colors = color_map()
    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    for k in range(n_instances):
        color = colors[class_ids[k]].astype(np.uint8)
        if show_bbox:
            box = boxes[k]
            cls = class_names[class_ids[k] - 1]  # Skip the Background
            score = scores[k]
            #                 cv2.rectangle(image, (box[1], box[0]), (box[3], box[2]), color, 1)
            cv2.rectangle(image, (box[1], box[0]), (box[3], box[2]), color.tolist(), 1)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, '{}: {:.3f}'.format(cls, score), (box[1], box[0]),
                        font, 0.4, (0, 255, 255), 1, cv2.LINE_AA)

        if show_mask:
            mask = masks[:, :, k]
            color_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
            color_mask[mask] = color
            image = cv2.addWeighted(color_mask, 0.5, image.astype(np.uint8), 1, 0)

    if display_img:
        plt.imshow(image)
        plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
        plt.show()
    if save_img:
        cv2.imwrite(os.path.join(save_dir, img_name), image)

    return image


class LegoConfig(Config):
    """Configuration0 for training on the toy  dataset.
    Derives from the base Config class and overrides some values.
    """
    # Give the configuration a recognizable name
    NAME = "lego"

    # We use a GPU with 12GB memory, which can fit two images.
    # Adjust down if you use a smaller GPU.
    IMAGES_PER_GPU = 1  # MW kaggle and colab ran out of memory if I set to 2

    # Number of classes (including background)
    NUM_CLASSES = 1 + 14  # Background + lego classes

    # Number of training steps per epoch
    STEPS_PER_EPOCH = 1280  # MW it looks like batch size is always 1, meaning that this should correspond to the nummber of images to train

    VALIDATION_STEPS = 256  # MW it looks like batch size for validation data is also 1, meaning this should correspond to the number of images to evaluate

    # Define number of epochs
    NB_OF_EPOCHS = 5

    # Percent of positive ROIs used to train classifier/mask heads
    ROI_POSITIVE_RATIO = 0.33

    # Skip detections with < 90% confidence
    DETECTION_MIN_CONFIDENCE = 0.7  # default is 0.7, sollte kein Einfluss auf Training haben. Wird nur im DetectionLayer() verwendet, währen Inference.

    # Non-maximum suppression threshold for detection
    DETECTION_NMS_THRESHOLD = 0.3

    # Learning rate and momentum
    LEARNING_RATE = 0.001  # Default 0.001, in Retinanet I set it to 0.00001, if I use default mrcnn_class_losses do not get small enough, use 0.00001

    # Um die NN Grösse zu reduzieren, nimm kleinst mögliche Bildgrösse
    # 800x600px die noch durch 64 teilbar ist -> 832
    IMAGE_MAX_DIM = 832

    # Enable and use RPN ROIs or disable RPN and use externally generated
    # ROIs for training Keep this True for most situations. Set False if
    # you want to train the head branches on ROI generated by code rather
    # than the ROIs from the RPN. For example, to debug the classifier head
    # without having to train the RPN. This esentially freezes the RPN
    # layers, disconnects the RPN losses from backpropagation and adds
    # a new input layer to replace the output from the RPN.
    USE_RPN_ROIS = True  # True = with RPN, False = externally generated

    PRE_NMS_LIMIT = 6000  # default 6000, for LPRN set to 2048

    # Build targets for training (anchors)
    RPN_TRAIN_ANCHOR_IOU_POS_TH = 0.9  # Default 0.9, set slightly higher to show RPN to only accept anchors with high overlap
    RPN_TRAIN_ANCHOR_IOU_NEG_TH = 0.85  # Default 0.85, set much higher, to ensure RPN ignores badly overlaping anchors for training I think with 0.6
    #              I should have still enough anchors

    RPN_NMS_THRESHOLD = 0.3  # Default 0.7, reduce to allow more anchors in final selection. Maybe I would exlude
    # unintentially anchors that match the lego well.

    # Length of square anchor side in pixels
    RPN_ANCHOR_SCALES = (80, 112, 144, 180, 256)

    # If USE_RPN_ROIS = False, choose to generate random ROIs or
    # ROIs from the GT bboxes for training. For inference it
    # will always use the GT boxes, hence this settin is ignored.
    USE_RANDOM_RPN_ROIS = False  # True = GT Boxes, False = Random

    # Enable and use the second stage (head branches including, classifier
    # bbo regressor and mask network). Set False if you want to train
    # RPN only. In this case USE_RPN_ROIS must be True. This will essentially
    # freeze all header layers and disconnect the losses from the header
    # leaving the RPN losses as only feedback for the backpropagation.
    USE_STAGE_TWO = True

    # Enable separate backbone for RPN and MRCNN (classifier, regression
    # and mask) network or use one backbone for all, like in the
    # origninal Mask R-CNN implementation.
    USE_SEPARATE_BACKBONES = False

    # Choose backbone network architecture. Supported values are: resnet50,
    # resnet101 and resnet18 whisch uses keras-resnet library
    BACKBONE_RPN = "resnet18"
    BACKBONE_MRCNN = "resnet18"

    # This are the backbone filter configurations, the default settings
    # and accordinng to wide residual network according to http://arxiv.org/pdf/1605.07146v1.pdf
    # This setting will change the Resnet filter configuration.
    BACKBONE_RESNET_BOTTLE_DEFAULT = {"S2": [64, 64, 256], "S3": [128, 128, 512], "S4": [256, 256, 1024],
                                      "S5": [512, 512, 2048]}
    BACKBONE_RESNET_BOTTLE_WIDER = {"S2": [256, 256, 256], "S3": [512, 512, 512], "S4": [1024, 1024, 1024],
                                    "S5": [1024, 1024, 2048]}
    BACKBONE_RESNET_BASIC_DEFAULT = {"S2": [64, 64], "S3": [128, 128], "S4": [256, 256], "S5": [512, 512]}
    BACKBONE_RESNET_BASIC_WIDER = {"S2": [160, 160], "S3": [320, 320], "S4": [640, 640], "S5": [1280, 1280]}

    # Resnet backbone filter configuration
    BACKBONE_FITLERS_CONFIG = BACKBONE_RESNET_BASIC_DEFAULT

    # FPN_CLASSIF_FC_LAYERS_SIZE = 256                        # With LSTM cannot be more than 256
    # TRAIN_ROIS_PER_IMAGE = 20                               # Test in training (default 200), remove later
    POST_NMS_ROIS_INFERENCE = 1000  # Test in interference (default 1000), remove later

    # Plot and save graph to file.
    PLOT_GRAPH = False  # None: to not plot, False: plot, True: plot nested / details

    USE_MINI_MASK = False


def get_ax(rows=1, cols=1, size=16):
    """Return a Matplotlib Axes array to be used in
    all visualizations in the notebook. Provide a
    central point to control graph sizes.

    Adjust the size attribute to control how big to render images
    """
    _, ax = plt.subplots(rows, cols, figsize=(size * cols, size * rows))
    return ax


def detect(images):
    logger = logging.getLogger(__name__)
    config = LegoConfig()
    class InferenceConfig(config.__class__):
        # Run detection on one image at a time
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
    config = InferenceConfig()

    MODEL_DIR = os.path.join(settings.BASE_DIR, 'logs')
    LEGO_WEIGHTS_PATH = os.path.join(settings.BASE_DIR, "mask_rcnn_lego_0040.h5")
    names = ['BG', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']

    logger.info(f'Loading MODEL_DIR: {MODEL_DIR}')
    logger.info(f'Loading Weights: {LEGO_WEIGHTS_PATH}')
    # print(f'BASE_DIR: {settings.BASE_DIR}')
    # print(f'Loading MODEL_DIR: {MODEL_DIR}')
    # print(f'Loading Weights: {LEGO_WEIGHTS_PATH}')
    # print(images)

    # load binary images
    images = [cv2.cvtColor(cv2.imread(image), cv2.COLOR_BGR2RGB) for image in images]
    print(f'Image shape: {np.shape(images)}')

    # Model
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
    model.load_weights(LEGO_WEIGHTS_PATH, by_name=True)

    # Inference
    t0 = time.monotonic()
    results = model.detect(images, verbose=0)
    t1 = time.monotonic()

    detection_results = []
    result_imgs = []
    det_str = ''
    for image, detection in zip(images, results):
        num_objects = len(detection['rois'])
        if num_objects:  # if detections found
            # detection info
            image_detections = []
            for obj in range(num_objects):
                roi = detection['rois'][obj]
                conf = detection['scores'][obj]
                label = names[detection['class_ids'][obj]]
                xy0 = roi[:2]
                xy1 = roi[2:]
                r = {
                    'conf': conf,
                    'label': label,
                    'xy0': xy0,
                    'xy1': xy1
                }
                image_detections.append(r)

            # detection summary
            for c in np.unique(detection['class_ids']):
                n = (detection['class_ids'] == c).sum()  # detections per class
                det_str += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

            detection_results.append(image_detections)

        result_img = display_results(image, detection['rois'], detection['masks'], detection['class_ids'], names, detection['scores'])
        result_imgs.append(Image.fromarray(result_img))

        # generate image array results
        # plt.figure()
        # ax = get_ax(1)
        # visualize.display_instances(image, detection['rois'], detection['masks'], detection['class_ids'], names,
        #                             detection['scores'], ax=ax)

        # plt.savefig(f'test_{image_name}.png', bbox_inches='tight', pad_inches=-0.5, orientation='landscape')
        # result_imgs.append(Image.fromarray(result))

        # io_buf = io.BytesIO()
        # ax.savefig(io_buf, format='raw')
        # io_buf.seek(0)
        # img_arr = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
        #                      newshape=(int(ax.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1))
        # io_buf.close()

    # # generate image array results
    # for result in results.render():
    #     result_imgs.append(Image.fromarray(result))

    return {
        'inference_time_sec': t1 - t0,
        'detection_summary': det_str,
        'detections': detection_results
    }, result_imgs





'''
    # Model
    model = modellib.MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=config)
    model.load_weights(LEGO_WEIGHTS_PATH, by_name=True)

    # image
    image = cv2.imread(os.path.join(test_images_path, image_name))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # inference
    t0 = time.monotonic()
    results = model.detect([image], verbose=0)
    t1 = time.monotonic()
    r = results[0]

    plt.figure()
    ax = get_ax(1)
    visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], names, r['scores'], ax=ax)
    plt.savefig(f'output_image.png', bbox_inches='tight', pad_inches=-0.5, orientation='landscape')

    return {
        'inference_time_sec': t1 - t0,
        'detection_summary': det_str,
        'detections': detection_results
    }, result_imgs
'''



'''
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
                xy0 = detection[0:2]
                xy1 = detection[2:4]
                conf = detection[4]
                label = names[int(detection[5])]
                r = {
                    'conf': conf,
                    'label': label,
                    'xy0': xy0,
                    'xy1': xy1
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
    }, result_imgs
'''