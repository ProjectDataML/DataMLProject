from django.shortcuts import render
from .models import Calendar
from django.core.serializers import serialize

def index(request):
    return render(request, 'base.html' )

def stats(request):
    listings = Calendar.objects.all()
    data = serialize('json', listings, fields=('date', 'price'))
    return render(request, 'stats.html', {'data': data})

def ml(request):
    return render(request, 'ml.html' )