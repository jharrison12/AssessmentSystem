from django.shortcuts import render, redirect
from rubricapp.models import Student, Enrollment, Row, Rubric, EdClasses, Semester, Assignment, CompletedRubric
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
	#TODO Still pulls students multiple times
	enrollmentstrue = Enrollment.objects.filter(rubricdata__rubriccompleted=True)
	students = Student.objects.filter(enrollment=enrollmentstrue).distinct()
	logging.info("Students filtered {}".format(students))
	if request.method == "POST":
		return redirect(request.POST['studentnames']+ '/')
	return render(request, 'dataview/studentview.html', {"students": students})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def student_data_view(request, lnumber):
	student = Student.objects.get(lnumber=lnumber)
	enrollments = Enrollment.objects.filter(student__lnumber=lnumber, rubricdata__rubriccompleted=True)
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
def ed_class_assignment_view(request,edclass,semester):
	edclasssubjectarea = re.match('([A-Z]+)', edclass).group(0)
	edclasscoursenumber = re.search('([0-9]{4})', edclass).group(0)
	edclasssectionnumber = re.search('[0-9]{2}$', edclass).group(0)
	semester= Semester.objects.get(text=semester)
	edclasspulled = EdClasses.objects.get(subject=edclasssubjectarea, coursenumber=edclasscoursenumber, sectionnumber=edclasssectionnumber, semester=semester)
	assignment = Assignment.objects.filter(edclass=edclasspulled)#, semester__text=semester)
	if request.POST:
		assignment = Assignment.objects.get(assignmentname=request.POST['assignment'], edclass=edclasspulled)
		return redirect(re.sub(' ', '', assignment.assignmentname).lower() + str(assignment.pk) + '/')
	return render(request,'dataview/classassignmentdataview.html', {'assignments': assignment})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def ed_class_data_view(request, edclass, semester, assignmentname):
	edclasssubjectarea = re.match('([A-Z]+)', edclass).group(0)
	edclasscoursenumber = re.search('([0-9]{4})', edclass).group(0)
	edclasssectionnumber = re.search('[0-9]{2}$', edclass).group(0)
	assignmentforclass = re.search('[0-9]+', assignmentname).group(0)
	semesterobj = Semester.objects.get(text=semester)
	logging.warning("Class and assignmentpk: %s %s %s %s " % (edclasssubjectarea, edclasscoursenumber, edclasssectionnumber, assignmentforclass))
	edclasspulled = EdClasses.objects.get(subject=edclasssubjectarea, coursenumber=edclasscoursenumber, sectionnumber=edclasssectionnumber, semester=semesterobj)
	assignment = Assignment.objects.get(pk=assignmentforclass)#, semester__text=semester)
	classrubric = assignment.keyrubric.get()
	templaterows = Row.objects.filter(rubric=classrubric)
	#Questions about whether the below query actually works the way it should
	#logging.info("Semester %s EdClass %s" %(semester, edclasspulled))
	#TODO Figure out why filtering rows by the query object below works in django 1.8 but not 1.10
	#rubrics = Rubric.objects.filter(enrollment__semester__text=semester, enrollment__edclass=edclasspulled)
	#logging.info("Rubric num is %d" % rubrics.count())
	rows = Row.objects.filter(rubric__rubricdata__assignment=assignment)
	logging.info("Row num is %d" % rows.count())
	for row in rows:
		logging.warning("Row choices %s" % (row.row_choice))
	#Must be ordereddict or the rows will rearrange themselves in alphabetical order on page
	scores = collections.OrderedDict()
	for row in rows:
		if row.name not in scores:
			logging.warning("First if for row in rows %s" % row.row_choice)
			scores[row.name] = list((row.row_choice))
		else:
			logging.info("Adding %s" % row.row_choice)
			scores[row.name].append((row.row_choice))
	scores1 = copy.deepcopy(scores)
	#average the scores for all of the items in scores
	for key, rowscores in scores.items():
		try:
			logging.warning("Rowscores processed " + str(rowscores) )
			rowscores = [int(x) for x in rowscores]
			rowscores = sum(rowscores)/len(rowscores)
			rowscores = '{:03.2f}'.format(rowscores)
			scores[key] = rowscores	
			logging.warning("Rowscores now " + str(rowscores) )
		except ValueError:
			pass
	return render(request, 'dataview/classdataview.html', {'rows': templaterows, 'scores':rows, 'finalscores': scores, 'test':scores1})
