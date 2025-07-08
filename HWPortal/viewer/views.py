from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'viewer/home.html')

def components(request):
    return render(request, 'viewer/components.html')

def reviews(request):
    return render(request, 'viewer/reviews.html')