import tempfile

from django.shortcuts import render
from django.http import FileResponse
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.data import tesseract, yolov5


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


# return image of object detections
class YoloV5UploadImageView(APIView):
    # parser_classes = (FileUploadParser,)
    parser_classes = (ImageUploadParser,)

    def post(self, request, format=None):
        file = request.data['file']

        # print(request.FILES['file'])
        # print(f'Processing file: {file}')
        # print(file)
        # print(type(file))
        # print(dir(file))
        # print(f'name: {file.name}')
        # print(f'size: {file.size}')
        # print(f'content_type: {file.content_type}')
        # print(f'TMP file path: {file.temporary_file_path()}')
        # img = Image.open(file)

        images = [file.temporary_file_path()]
        data_response, output_images = yolov5.detect(images)

        # print(f'There are {len(output_images)} generated images')
        # # for output in output_images:
        # #     output

        # save first image to temporary file
        first_image = output_images[0]
        tmpfile = tempfile.NamedTemporaryFile(suffix='.jpg')
        # print(f'Generated File: {tmpfile.name}')
        # print(tmpfile)
        first_image.save(tmpfile, first_image.format, quality=100)
        tmpfile.seek(0)

        # return Response(data_response)
        return FileResponse(open(tmpfile.name, 'rb'))


# return metadata of object detections
class YoloV5UploadMetadataView(APIView):
    parser_classes = (ImageUploadParser,)

    def post(self, request, format=None):
        file = request.data['file']
        images = [file.temporary_file_path()]
        data_response, output_images = yolov5.detect(images)
        return Response(data_response)


# return image of ocr detections
class TesseractUploadImageView(APIView):
    # parser_classes = (FileUploadParser,)
    parser_classes = (ImageUploadParser,)

    def post(self, request, format=None):
        file = request.data['file']

        image = file.temporary_file_path()
        data_response, output_image = tesseract.detect(image)

        # save first image to temporary file
        tmpfile = tempfile.NamedTemporaryFile(suffix='.jpg')
        output_image.save(tmpfile, output_image.format, quality=100)
        tmpfile.seek(0)

        # return Response(data_response)
        return FileResponse(open(tmpfile.name, 'rb'))


# return metadata of ocr detections
class TesseractUploadMetadataView(APIView):
    parser_classes = (ImageUploadParser,)

    def post(self, request, format=None):
        file = request.data['file']
        image = file.temporary_file_path()
        data_response, output_images = tesseract.detect(image)
        return Response(data_response)
