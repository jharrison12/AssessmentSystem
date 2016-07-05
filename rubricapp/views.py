from django.shortcuts import render
from django.http import HttpResponse
from rubricapp.models import Semester

def home_page(request):
	Semester.objects.create(text='201530')
	Semester.objects.create(text='201610')
	semester = Semester.objects.all()
	return render(request, 'home.html', {'semestercode': semester })



# Create your views here.
