from django.shortcuts import render

def index(request):
    return render(request, 'app/index.html')
# Create your views here.
