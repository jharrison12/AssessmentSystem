from django.shortcuts import render, redirect
from rubricapp.models import Student, Enrollment, Row, Rubric, EdClasses, Semester, Assignment, CompletedRubric,RubricData, Standard
import re, logging, collections, copy
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)
from django.contrib.auth.decorators import login_required,user_passes_test
# Create your views here.

@login_required
@user_passes_test(lambda u: u.is_superuser)
def home_page(request):
	return render(request, 'dataview/dataviewhome.html', )

@login_required	
@user_passes_test(lambda u: u.is_superuser)
def student_view(request):
	#enrollmentstrue = Enrollment.objects.filter(rubricdata__rubriccompleted=True)
	students = Student.objects.filter(enrollment__dataforrubric__rubricdata__rubriccompleted=True).distinct()
	if request.method == "POST":
		return redirect(request.POST['studentnames']+ '/')
	return render(request, 'dataview/studentview.html', {"students": students})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def student_data_view(request, lnumber):
	student = Student.objects.get(lnumber=lnumber)
	#enrollments = Rubric.objects.filter(student__lnumber=lnumber)#, rubricdata__rubriccompleted=True)
	rubricdataobj = RubricData.objects.filter(enrollment__student=student, rubriccompleted=True )
	logging.info("Rubricdataobjs are {}".format(rubricdataobj.values()))
	if request.method == "POST":
		return redirect(re.sub('[\s+]', '', request.POST['rubricname'])+'/')
	return render(request, 'dataview/studentdataview.html', {"student": student, "rubricdataobjs":rubricdataobj})

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
	logging.info("Class and assignmentpk: %s %s %s %s " % (edclasssubjectarea, edclasscoursenumber, edclasssectionnumber, assignmentforclass))
	edclasspulled = EdClasses.objects.get(subject=edclasssubjectarea, coursenumber=edclasscoursenumber, sectionnumber=edclasssectionnumber, semester=semesterobj)
	assignment = Assignment.objects.get(pk=assignmentforclass)#, semester__text=semester)
	classrubric = assignment.keyrubric
	templaterows = Row.objects.filter(rubric=classrubric)
	#Questions about whether the below query actually works the way it should
	#logging.info("Semester %s EdClass %s" %(semester, edclasspulled))
	#TODO Figure out why filtering rows by the query object below works in django 1.8 but not 1.10
	#rubrics = Rubric.objects.filter(enrollment__semester__text=semester, enrollment__edclass=edclasspulled)
	#logging.info("Rubric num is %d" % rubrics.count())
	rows = Row.objects.filter(rubric__rubricdata__assignment=assignment)
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
			rowscores = '{:03.2f}'.format(rowscores)
			scores[key] = rowscores	
			logging.info("Rowscores now " + str(rowscores) )
		except ValueError:
			pass
	return render(request, 'dataview/classdataview.html', {'rows': templaterows, 'scores':rows, 'finalscores': scores, 'test':scores1})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def standards_view(request):
    standards = Standard.objects.all()
    semesters = Semester.objects.all()
    if request.POST:
        semester = Semester.objects.get(text=request.POST['semestername'])
        return redirect(semester.text + '/')
    return render(request, 'dataview/standardsview.html', {"standards": standards, "semesters": semesters})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def standards_semester_view(request, semester):
    standards = Standard.objects.all()
    if request.POST:
        logging.info(request.POST['standardsname'])
        standard = Standard.objects.get(name=request.POST['standardsname'])
        return redirect(re.sub(' ', '', standard.name).lower() + '/')
    return render(request, 'dataview/standardssemesterview.html', {"standards": standards})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def standards_semester_standard_view(request, semester, standard):
    standardwithspace = re.sub(r'([a-z]+)', r"\1 ", standard)
    standard = Standard.objects.get(name=standardwithspace.upper())
    semestertext = Semester.objects.get(text=semester)
    ##COMPLETED RUBRICS IN 201530
    semesterrubric = Rubric.objects.filter(rubricdata__rubriccompleted=True, rubricdata__enrollment__edclass__semester=semestertext)
    #Returns correct rubrics below. Two rubrics.
    logging.warning("Rubrics that are completed and are in 201530 {} Num of rubrics: {}. Should be 2\n\n".format(semesterrubric.values(), len(semesterrubric)))
    #But when you filter the rows based upon the rubrics above, it only returns bob's rubric and not both
    logging.warning("THE PROBLEM IS HERE "
					 "ROWS IN RUBRICS completed in 201530 {}\n "
					 "This returns the correct amount {}\n\n".format(Row.objects.filter(rubric__in=semesterrubric).all()
																   ,[rubric.row_set.all() for rubric in semesterrubric]))
    #Templates that use Standards
    templates = Rubric.objects.filter(template=True, row__standards=standard)
    logging.warning("The templates are {}".format(templates))
    rows = Row.objects.filter(standards=standard)
    rowswithstandards = rows.filter(rubric__in=semesterrubric).all()
    logging.warning("Rows with standards are {}".format(rowswithstandards.values()))
    #Default dict creates default value if there isn't one, so you don't have to
    rowdata = collections.defaultdict(dict)
    for row in rowswithstandards:
         if row.templatename not in rowdata:
            rowdata[row.templatename][row.name] = [int(row.row_choice)]
         elif row.name not in rowdata[row.templatename]:
             rowdata[row.templatename][row.name] = [int(row.row_choice)]
         else:
             logging.warning("Made it to else statement.  Adding {}".format(int(row.row_choice)))
             rowdata[row.templatename][row.name].append(int(row.row_choice))
    logging.warning("Rowdata iha {}".format(rowdata))
    # This averages the row for each rubric.
    # This is probably not the best way to do this.
    for rubricname,rowname in rowdata.items():
        for rowname, score in rowname.items():
            rowdata[rubricname][rowname] = '{:03.2f}'.format(sum(score)/len(score))

    logging.warning("Did the average work {}".format(rowdata))
    logging.warning("The values with INTASC1 as a standard are \n{} the num is {}\n\n Rows returned {}".format(rows.values(), len(rows),rowswithstandards))
    #this isn't very efficient with large data set (although it works)
    rowdata = dict(rowdata)
    return render(request, 'dataview/standardssemesterstandardview.html', {"standard": standard, "rubrics":rowdata})

# this display what standards are used for what rubric

@login_required
@user_passes_test(lambda u: u.is_superuser)
def rubric_standard_view(request):
	standards = Standard.objects.all()
	if request.POST:
		standard = Standard.objects.get(name=request.POST['standardselect'])
		return redirect(re.sub(' ', '',standard.name).lower() + '/')
	return render(request, 'dataview/rubricstandardview.html', {'standards': standards})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def rubric_standard_individual_view(request, standard):
	standardwithspace = re.sub(r'([a-z]+)', r"\1 ", standard)
	standard = Standard.objects.filter(name__iexact=standardwithspace)
	rows = Row.objects.filter(standards=standard, rubric__template=True)
	#Set object keeps the list of row names immutable
	rowdata = collections.defaultdict(list)
	for row in rows:
		if row.templatename not in rowdata:
			rowdata[row.templatename] = set([row.name])
		else:
			rowdata[row.templatename].add(row.name)
	logging.critical("Does this work? {}".format(rowdata))
	rowdata = dict(rowdata)
	return render(request, 'dataview/rubricstandardindividual.html', {'rubrics':rowdata})