from django.shortcuts import render

# Create your views here.
def index(request):
    """
    Render the main page of the PWA.
    """
    return render(request, 'base.html')