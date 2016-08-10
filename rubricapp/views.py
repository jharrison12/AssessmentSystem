from django.shortcuts import render, redirect
from django.http import HttpResponse
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Row, Rubric
from rubricapp.forms import RowForm, RowFormSet
import re, logging
from copy import deepcopy
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

@login_required
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
@login_required
def semester_page(request, semester):
	summerclasses = EdClasses.objects.filter(semester__text=semester)
	if summerclasses.exists():
		pass
	else:
		return redirect('/')
	if request.method == "POST":
		return redirect(re.sub('[\s+]', '', request.POST['edClass']) + '/') #removes whitespace from inside the class name
	return render(request, 'semester.html', {'summerclasses': summerclasses} ) 
	
@login_required
def student_page(request, edclass, semester):
	#REGEX below finds EG,ED, EGSE, etc. in edclass and then adds a space to the 
	#course code
	logging.info("In the student page edclass:%s, semester %s" %( edclass, semester))
	edClassSpaceAdded = re.sub('([A-Z]+)', r'\1 ', edclass )
	#Filter the class basedupon semester and name of the class
	edclassesPulled = EdClasses.objects.get(semester__text=semester, name=edClassSpaceAdded)
	logging.info("The classes pulled are %s" % (edclassesPulled))
	students = Student.objects.filter(edclasses=edclassesPulled, enrollment__rubriccompleted=False, enrollment__semester__text=semester)
	for i in students:
		logging.info("Students are %s" % (i.lnumber))
	if request.method == 'POST':
		#Why is adding the forward slash unneccessary?
		#Why does the redirect no need the edclass added to the beginning?
		return redirect(re.sub('[\s+]', '', request.POST['studentnames']) + '/')
	return render(request, 'student.html', {'students': students, 'semester':semester})

#TODO fix studentname variable.  Change to studentlnumber
#TODO add system log

@login_required
def rubric_page(request, edclass, studentname,semester):
	edclassspaceadded = re.sub('([A-Z]+)', r'\1 ', edclass)
	#This returns the class
	edclassenrolled = EdClasses.objects.get(name=edclassspaceadded)
	#This returns the student
	student = Student.objects.get(lnumber=studentname)
	#this returns the rubric associated with the class
	rubricforclass = edclassenrolled.keyrubric.get()
	#this returns the rows associated with the magic rubric
	rows = Row.objects.filter(rubric=rubricforclass)
	if request.method == 'POST':
		#this should return a single Enrollment object
		greatEnrollment = Enrollment.objects.get(student=student, edclass=edclassenrolled)
		logging.info("Posting")
		RowFormSetWeb = RowFormSet(request.POST)#, queryset=Row.objects.filter(rubric=rubricForClass))
		RowFormSetWeb.clean()
		if RowFormSetWeb.is_valid():
			savedFormset = RowFormSetWeb.save(commit=False)
			#Not sure if the below is necessary.  But it works!
			for i in savedFormset:
				#i.rubric = rubricafterpost
				#instead of saving entire formset, this will only update row_choice
				#this keeps the form.text fields from disappearing
				i.save(update_fields=['row_choice'])
				logging.info("The rubric associated with the row is %d" % i.rubric.id)
				rubricid = i.rubric.id
			greatEnrollment.rubriccompleted=True
			#Set the enrollment object to the new rubric created by accessing the page
			greatEnrollment.completedrubric = Rubric.objects.get(pk=rubricid)
			greatEnrollment.save()
			logging.info("Great enrollment rubric completed  is %s" % greatEnrollment.rubriccompleted)
			logging.info("Great enrollment id is %d" % greatEnrollment.pk)
			return redirect('/'+ semester +'/'+ edclass + '/')
		else:
			return render(request, 'rubric.html', {'studentlnumber': student.lnumber,'studentname': student.lastname + ", " + student.firstname, 'RowFormSetWeb':RowFormSetWeb, 'rows':rows, 'edclass':edclass})
	else:
		#This view returns a brandnew copy of the rubric based upon
		#the rubric associated with the edclass
		rubricforclass = edclassenrolled.keyrubric.get()
		oldrubricname = rubricforclass.name
		rows = Row.objects.filter(rubric=rubricforclass)
		logging.info("Get Rubric: " + str(rubricforclass.pk) + " " + str(type(rubricforclass))+ " " + str([row for row in rows]) +"\n")
		rubricforclass.pk = None
		rubricforclass.name= "%s %s %s" %(edclass, studentname, semester)
		rubricforclass.template = False
		if rubricforclass.clean_fields():
			rubricforclass.save()
			logging.info("DID THE RUBRIC UDPATE? %s" % rubricforclass.pk)
			for row in rows:
				row.pk = None
				row.rubric = rubricforclass
				logging.info("THE RUBRIC FOR CLASS IS: %d" % rubricforclass.id)
				row.save()
			RowFormSetWeb = RowFormSet(queryset=Row.objects.filter(rubric=rubricforclass))
			rubricForClassText = re.sub('rubric', ' rubric', oldrubricname)
			logging.info("At the end of the long view, the rubric is %s" % rubricforclass.pk)
			return render(request, 'rubric.html', {'studentlnumber': student.lnumber,
													'studentname': student.lastname + ", " + student.firstname, 
													'RowFormSetWeb':RowFormSetWeb, 'rows':rows, 
													'edclass':edclass, 
													'rubricForClass': rubricForClassText.title(), 
													'semester': semester})
		else:
			error = "You have already completed this rubric"
			return render(request, 'rubric.html', {'studentlnumber': student.lnumber,
													'studentname': student.lastname + ", " + student.firstname, 
													'rows':rows, 
													'edclass':edclass, 
													'rubricForClass': oldrubricname.title(), 
													'semester': semester,
													'error': error})
		