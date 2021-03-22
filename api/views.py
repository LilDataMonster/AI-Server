from django.shortcuts import render
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from PIL import Image

from api.data.detect import detect_yolov5


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


class YoloV5UploadView(APIView):
    # parser_classes = (FileUploadParser,)
    parser_classes = (ImageUploadParser,)

    def post(self, request, format=None):
        file = request.data['file']

        print(f'Processing file: {file}')
        print(f'TMP file path: {file.temporary_file_path()}')
        # img = Image.open(file)

        images = [file.temporary_file_path()]
        resp = detect_yolov5(images)

        # data = file.read()
        # print(type(data))

        print(f'name: {file.name}')
        print(f'size: {file.size}')
        print(f'content_type: {file.content_type}')

        print(file)
        print(type(file))
        print(dir(file))

        # print(request.FILES['file'])

        # return Response({'received data': request.data})
        # return Response({'received data': '123'})
        return Response(resp)