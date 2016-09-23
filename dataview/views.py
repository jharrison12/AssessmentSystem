from django.shortcuts import render, redirect
from rubricapp.models import Student, Enrollment, Row, Rubric, EdClasses, Semester
import re, logging, collections, copy
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)
from django.contrib.auth.decorators import login_required,user_passes_test
# Create your views here.

@login_required
@user_passes_test(lambda u: u.is_superuser)
def home_page(request):
	return render(request, 'dataview/dataviewhome.html', )

@login_required	
@user_passes_test(lambda u: u.is_superuser)
def student_view(request):
	students = Student.objects.all()
	if request.method == "POST":
		return redirect(request.POST['studentnames']+ '/')
	return render(request, 'dataview/studentview.html', {"students": students})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def student_data_view(request, lnumber):
	student = Student.objects.get(lnumber=lnumber)
	enrollments = Enrollment.objects.filter(student__lnumber=lnumber, rubriccompleted=True)
	if request.method == "POST":
		return redirect(re.sub('[\s+]', '', request.POST['rubricname'])+'/')
	return render(request, 'dataview/studentdataview.html', {"student": student, "enrollments":enrollments})

@login_required	
@user_passes_test(lambda u: u.is_superuser)
def student_rubric_data_view(request,lnumber,rubricname):
	logging.info("The rubric name is %s " % (rubricname))
	rows = Row.objects.filter(rubric__name=rubricname)
	return render(request, 'dataview/studentrubricview.html', {'rows':rows, 'rubricname':rubricname})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def semester_ed_class_view(request):
	semesters = Semester.objects.all()
	if request.method == "POST":
		return redirect(request.POST['semesterselect'] +'/')
	return render(request, 'dataview/semesterclassview.html',{'semesters':semesters})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ed_class_view(request, semester):
	edclasses = EdClasses.objects.filter(semester__text=semester)
	if request.method == "POST":
		return redirect(re.sub('[\s+]', '', request.POST['edclass'])+'/')
	return render(request, 'dataview/classview.html', {'edclasses':edclasses})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ed_class_data_view(request, edclass, semester):
	edclasssubjectarea = re.match('([A-Z]+)', edclass).group(0)
	edclasscoursenumber = re.search('([0-9]+)', edclass).group(0)
	edclasspulled = EdClasses.objects.get(subject=edclasssubjectarea, coursenumber=edclasscoursenumber)
	classrubric = edclasspulled.keyrubric.get()
	templaterows = Row.objects.filter(rubric=classrubric)
	#Questions about whether the below query actually works the way it should
	#logging.info("Semester %s EdClass %s" %(semester, edclasspulled))
	#TODO Figure out why filtering rows by the query object below works in django 1.8 but not 1.10
	#rubrics = Rubric.objects.filter(enrollment__semester__text=semester, enrollment__edclass=edclasspulled)
	#logging.info("Rubric num is %d" % rubrics.count())
	rows = Row.objects.filter(rubric__enrollment__semester__text=semester, rubric__enrollment__edclass=edclasspulled)
	logging.info("Row num is %d" % rows.count())
	for row in rows:
		logging.info("Row choices %s" % (row.row_choice))
	#Must be ordereddict or the rows will rearrange themselves in alphabetical order on page
	scores = collections.OrderedDict()
	for row in rows:
		if row.name not in scores:
			logging.info("First if for row in rows %s" % row.row_choice)
			scores[row.name] = list((row.row_choice))
		else:
			logging.info("Adding %s" % row.row_choice)
			scores[row.name].append((row.row_choice))
	scores1 = copy.deepcopy(scores)
	#average the scores for all of the items in scores
	for key, rowscores in scores.items():
		try:
			logging.info("Rowscores processed " + str(rowscores) )
			rowscores = [int(x) for x in rowscores]
			rowscores = sum(rowscores)/len(rowscores)
			scores[key] = rowscores	
			logging.info("Rowscores now " + str(rowscores) )
		except ValueError:
			pass
	return render(request, 'dataview/classdataview.html', {'rows': templaterows, 'scores':rows, 'finalscores': scores, 'test':scores1})
