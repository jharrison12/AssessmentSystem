from django.shortcuts import render, redirect
from rubricapp.models import Student, Enrollment, Row, Rubric, EdClasses, Semester
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

def semester_ed_class_view(request):
	semesters = Semester.objects.all()
	if request.method == "POST":
		return redirect(request.POST['semesterselect'] +'/')
	return render(request, 'dataview/semesterclassview.html',{'semesters':semesters})

def ed_class_view(request, semester):
	edclasses = EdClasses.objects.filter(semester__text=semester)
	if request.method == "POST":
		return redirect(re.sub('[\s+]', '', request.POST['edclass'])+'/')
	return render(request, 'dataview/classview.html', {'edclasses':edclasses})

def ed_class_data_view(request, edclass, semester):
	edclassspaceadded = re.sub('([A-Z]+)', r'\1 ', edclass)
	edclasspulled = EdClasses.objects.get(name=edclassspaceadded)
	classrubric = edclasspulled.keyrubric.get()
	templaterows = Row.objects.filter(rubric=classrubric)
	#Questions about whether the below query actually works the way it should
	rubrics = Rubric.objects.filter(enrollment__semester__text=semester, enrollment__edclass=edclasspulled)
	rows = Row.objects.filter(rubric=rubrics)
	scores = {}
	for row in rows:
		if row.name not in scores:
			scores[row.name] = list((row.row_choice))
		else:
			scores[row.name].append((row.row_choice))
	#average the scores for all of the items in scores
	for key, rowscores in scores.items():
		rowscores = [int(x) for x in rowscores]
		rowscores = sum(rowscores)/len(rowscores)
		scores[key] = rowscores
	return render(request, 'dataview/classdataview.html', {'rows': templaterows, 'scores':rows, 'finalscores': scores})