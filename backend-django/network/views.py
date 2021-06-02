import os
from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
dir_path = os.path.dirname(os.path.realpath(__file__))
image_path = os.path.join(dir_path,"../../backend-express/sample.jpg")
image_data = open(image_path, mode='rb').read()
def post_list(request):
	return render(request, 'network/sample.html', {})

def get_html(request):
	return render(request, 'network/sample.html', {})

def get_image(request):
	return HttpResponse(image_data, content_type="image/jpeg")