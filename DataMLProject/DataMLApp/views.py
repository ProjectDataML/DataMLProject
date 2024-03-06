from django.shortcuts import render
from .models import Calendar
from django.core.serializers import serialize

def index(request):
    listings = Calendar.objects.all()
    data = serialize('json', listings, fields=('date', 'price'))
    return render(request, 'base.html', {'data': data})

# def index(request):
#     listings = Calendar.objects.all()
#     data = serialize('json', listings, fields=('date', 'price'))
#     return render(request, 'base.html', {'data': data})