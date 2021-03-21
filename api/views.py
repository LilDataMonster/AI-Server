from django.shortcuts import render
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from PIL import Image


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


class YoloV5UploadView(APIView):
    # parser_classes = (FileUploadParser,)
    parser_classes = (ImageUploadParser,)

    def post(self, request, format=None):
        file = request.data['file']

        img = Image.open(file)
        # img.show()

        data = file.read()
        print(type(data))

        print(f'name: {file.name}')
        print(f'size: {file.size}')
        print(f'content_type: {file.content_type}')

        print(file)
        print(type(file))
        print(dir(file))

        # print(request.FILES['file'])

        # return Response({'received data': request.data})
        return Response({'received data': '123'})