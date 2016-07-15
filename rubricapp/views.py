from django.shortcuts import render, redirect
from django.http import HttpResponse
from rubricapp.models import Semester, EdClasses, Student
import re

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
		pass
	else:
		return redirect('/')
	if request.method == "POST":
		return redirect('/'+ re.sub('[\s+]', '', request.POST['edClass']) + '/') #removes whitespace from inside the class name
	return render(request, 'semester.html', {'summerclasses': summerclasses} ) 
	

def student_page(request, edclass):
	#REGEX below finds EG,ED, EGSE, etc. in edclass and then adds a space to the 
	#course code
	edClassSpaceAdded = re.sub('([A-Z]+)', r'\1 ', edclass )
	students = Student.objects.filter(edclasses__name=edClassSpaceAdded)
	if request.method == 'POST':
		#Why is adding the forward slash unneccessary?
		#Why does the redirect no need the edclass added to the beginning?
		return redirect(re.sub('[\s+]', '', request.POST['studentnames']).lower() + '/')
	return render(request, 'student.html', {'students': students})
# Create your views here

def rubric_page(request, edclass, studentname):
	student = Student.objects.get(name="Bob DaBuilder")
	return render(request, 'rubric.html', {'studentname': student.name})
