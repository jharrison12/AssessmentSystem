from django.shortcuts import render, redirect
from rubricapp.models import Student, Enrollment

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
		return redirect(request.POST['rubricname']+'/')
	return render(request, 'dataview/studentdataview.html', {"student": student, "enrollments":enrollments})
	
