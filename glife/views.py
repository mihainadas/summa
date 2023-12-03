from django.shortcuts import render
import datetime

# Create your views here.
def index(request):
    return render(request, 'glife/index.html')

def time(request):
    return render(request, 'glife/time.html', context={'datetime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})