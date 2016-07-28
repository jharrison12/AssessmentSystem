from django.shortcuts import render, redirect
from django.http import HttpResponse
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Row
from rubricapp.forms import RowForm, RowFormSet
import re

def home_page(request):
	semester = Semester.objects.all()
	#TODO CHANGE So that the view doesn't need to check for semester
	#Objects
	if Semester.objects.all().exists():
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
		return redirect(re.sub('[\s+]', '', request.POST['edClass']) + '/') #removes whitespace from inside the class name
	return render(request, 'semester.html', {'summerclasses': summerclasses} ) 
	

def student_page(request, edclass, semester):
	#REGEX below finds EG,ED, EGSE, etc. in edclass and then adds a space to the 
	#course code
	edClassSpaceAdded = re.sub('([A-Z]+)', r'\1 ', edclass )
	edclassesPulled = EdClasses.objects.filter(semester__text=semester, name=edClassSpaceAdded)
	students = Student.objects.filter(edclasses=edclassesPulled)
	if request.method == 'POST':
		#Why is adding the forward slash unneccessary?
		#Why does the redirect no need the edclass added to the beginning?
		return redirect(re.sub('[\s+]', '', request.POST['studentnames']) + '/')
	return render(request, 'student.html', {'students': students})

#TODO fix studentname variable.  Change to studentlnumber
def rubric_page(request, edclass, studentname,semester):
	edClassSpaceAdded = re.sub('([A-Z]+)', r'\1 ', edclass)
	enrollmentObj = Enrollment.objects.get(edclass__name=edClassSpaceAdded, student__lnumber=studentname)
	rubricForClass = enrollmentObj.keyrubric.get()
	rows = Row.objects.filter(rubric=rubricForClass)
	student = Student.objects.get(lnumber=studentname)
	if request.method == 'POST':
		RowFormSetWeb = RowFormSet(request.POST, queryset=Row.objects.filter(rubric=rubricForClass))
		RowFormSetWeb.clean()
		if RowFormSetWeb.is_valid():
			savedFormset = RowFormSetWeb.save(commit=False)
			#Not sure if the below is necessary.  But it works!
			for i in savedFormset:
				i.rubric = rubricForClass 
				#instead of saving entire formset, this will only update row_choice
				#this keeps the form.text fields from disappearing
				i.save(update_fields=['row_choice'])
			return redirect('/'+ semester +'/'+ edclass + '/')
		else:
			return render(request, 'rubric.html', {'studentlnumber': student.lnumber,'studentname': student.lastname + ", " + student.firstname, 'RowFormSetWeb':RowFormSetWeb, 'rows':rows, 'edclass':edclass})
	else:
		RowFormSetWeb = RowFormSet(queryset=Row.objects.filter(rubric=rubricForClass))
		rubricForClassText = re.sub('rubric', ' rubric', rubricForClass.name)
		return render(request, 'rubric.html', {'studentlnumber': student.lnumber,'studentname': student.lastname + ", " + student.firstname, 'RowFormSetWeb':RowFormSetWeb, 'rows':rows, 'edclass':edclass, 'rubricForClass': rubricForClassText.title(), 'semester': semester})