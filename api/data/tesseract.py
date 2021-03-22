import time
import cv2
import pytesseract
from pytesseract import Output

from PIL import Image


def detect(image):
    # get bounding boxes
    d = pytesseract.image_to_data(Image.open(image), output_type=Output.DICT)

    # draw over original image the bounding boxes
    img = cv2.imread(image)
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # convert cv2 to pillow image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # convert colorspace
    bounding_boxes_image = Image.fromarray(img)

    # parse ocr string
    output_string = pytesseract.image_to_string(Image.open(image))

    # get image osd metadata
    osd = pytesseract.image_to_osd(Image.open(image), output_type=Output.DICT)

    # print(f'osd: {osd}')

    return {
        'osd': osd,
        'ocr_string': output_string,
    }, bounding_boxes_image