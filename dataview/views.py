from django.shortcuts import render, redirect
from rubricapp.models import Student, Enrollment, Row, Rubric
import re, logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
# Create your views here.


def home_page(request):
	return render(request, 'dataview/dataviewhome.html', )
	
def student_view(request):
	students = Student.objects.all()
	if request.method == "POST":
		return redirect(request.POST['studentnames']+ '/')
	return render(request, 'dataview/studentview.html', {"students": students})

def student_data_view(request, lnumber):
	student = Student.objects.get(lnumber=lnumber)
	enrollments = Enrollment.objects.filter(student__lnumber=lnumber)
	if request.method == "POST":
		return redirect(re.sub('[\s+]', '', request.POST['rubricname'])+'/')
	return render(request, 'dataview/studentdataview.html', {"student": student, "enrollments":enrollments})
	
def student_rubric_data_view(request,lnumber,rubricname):
	logging.info("The rubric name is %s " % (rubricname))
	rows = Row.objects.filter(rubric__name=rubricname)
	return render(request, 'dataview/studentrubricview.html', {'rows':rows, 'rubricname':rubricname})

def ed_class_view(request):
	return render(request, 'dataview/classview.html')