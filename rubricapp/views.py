from django.shortcuts import render, redirect
from django.http import HttpResponse
from rubricapp.models import Semester, EdClasses

def home_page(request):
	
	semester = Semester.objects.all()
	#TODO CHANGE So that the view doesn't need to check for semester
	#Objects
	if (Semester.objects.all().exists()):
		pass
	else:
		Semester.objects.create(text="201530")
		Semester.objects.create(text="201610")
	if request.method == "POST":
		return redirect('/' + request.POST['semester'] +'/')
	return render(request, 'home.html', {'semestercode': semester }) 
	#context can be translated as {'html template django variable': variable created in view}

def semester_page(request, semester):
	summerclasses = EdClasses.objects.filter(semester__text=semester)
	if summerclasses.exists():
		return render(request, 'semester.html', {'summerclasses': summerclasses} ) 
	else:
		return redirect('/')
	


# Create your views here.
