from django.shortcuts import render
from rest_framework import viewsets
from .models import Doctor
from .serializers import DoctorSerializer

# Create your views here.
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer