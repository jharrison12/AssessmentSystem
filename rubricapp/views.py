from django.shortcuts import render, redirect
from django.http import HttpResponse
from rubricapp.models import Semester

def home_page(request):
	
	semester = Semester.objects.all()
	#TODO CHANGE So that the view doesn't need to check for semester
	#Objects
	if (Semester.objects.all()):
		pass
	else:
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
	bob = Semester.objects.get(text="201530")
	if request.method == "POST":
		return redirect(bob.text+'/')
	return render(request, 'home.html', {'semestercode': semester })

def semester_page(request):
	return render(request, 'semester.html')


# Create your views here.
