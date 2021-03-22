import tempfile

from django.shortcuts import render
from django.http import FileResponse
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.data.detect import detect_yolov5


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


# return image of detections
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
        data_response, output_images = detect_yolov5(images)

        # print(f'There are {len(output_images)} generated images')
        # # for output in output_images:
        # #     output

        # save first image to temporary file
        first_image = output_images[0]
        tmpfile = tempfile.NamedTemporaryFile(suffix='.jpg')
        # print(f'Generated File: {tmpfile.name}')
        print(tmpfile)
        first_image.save(tmpfile, first_image.format, quality=100)
        tmpfile.seek(0)

        # return Response(data_response)
        return FileResponse(open(tmpfile.name, 'rb'))


# return metadata of detections
class YoloV5UploadMetadataView(APIView):
    parser_classes = (ImageUploadParser,)

    def post(self, request, format=None):
        file = request.data['file']
        images = [file.temporary_file_path()]
        data_response, output_images = detect_yolov5(images)
        return Response(data_response)