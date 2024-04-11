from django.shortcuts import render
from .models import Calendar
from django.core.serializers import serialize

def index(request):
    return render(request, 'base.html' )

def stats(request):
    return render(request, 'stats.html', {"streamlit_url": "http://localhost:8501"})

def ml(request):
    return render(request, 'ml.html' , {"streamlit_url": "http://localhost:8502"})