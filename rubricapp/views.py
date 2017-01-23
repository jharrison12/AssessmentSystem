from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Row, Rubric, Assignment
from rubricapp.forms import RowForm, RowFormSet
import re, logging
from copy import deepcopy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.core.exceptions import ValidationError

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)



@login_required
def home_page(request):
    semester = Semester.objects.all()
    # TODO CHANGE So that the view doesn't need to check for semester
    # Objects
    if Semester.objects.all().exists():
        pass
    else:
        Semester.objects.create(text="201530")
        Semester.objects.create(text="201610")
    if request.method == "POST":
        return redirect(request.POST['semester'] + '/')
    return render(request, 'rubricapp/home.html', {'semestercode': semester})


# context can be translated as {'html template django variable': variable created in view}

@login_required
def semester_page(request, semester):
    summerclasses = EdClasses.objects.filter(semester__text=semester, teacher=request.user)
    if summerclasses.exists():
        pass
    else:
        return redirect('/assessment/')
    if request.method == "POST":
        return redirect(
            re.sub('[\s+]', '', request.POST['edClass']) + '/')  # removes whitespace from inside the class name
    return render(request, 'rubricapp/semester.html', {'summerclasses': summerclasses})


@login_required
def assignment_page(request, semester, edclass):
    # REGEX below finds EG,ED, EGSE, etc. in edclass and then adds a space to the
    # course code
    logging.warning("In the student page edclass:%s, semester %s" % (edclass, semester))
    edclasssubjectarea = re.match('([A-Z]+)', edclass).group(0)
    logging.warning("In the student page edclass:%s, semester %s" % (edclass, semester))
    edclasscoursenumber = re.search('([0-9]{4})', edclass).group(0)
    edclasssectionnumber = re.search('[0-9]{2}$', edclass).group(0)
    logging.warning("In the student page subject:%s, course %s section %s" % (
    edclasssubjectarea, edclasscoursenumber, edclasssectionnumber))
    # Filter the class basedupon semester and name of the class
    edclassesPulled = get_object_or_404(EdClasses, semester__text=semester,
                                        subject=edclasssubjectarea,
                                        coursenumber=edclasscoursenumber,
                                        teacher=request.user,
                                        sectionnumber=edclasssectionnumber)
    logging.info("The classes pulled are %s" % (edclassesPulled))
    assignments = Assignment.objects.filter(edclass=edclassesPulled,
                                      semester__text=semester)
    for i in assignments:
        logging.info("Assignments are %s" % (i.assignmentname))
    if request.method == 'POST':
        # Why is adding the forward slash unneccessary?
        # Why does the redirect no need the edclass added to the beginning?
        return redirect(re.sub('[\s+]', '', request.POST['assignmentname']) + '/')
    return render(request, 'rubricapp/assignment.html', {'assignments': assignments, 'semester': semester})


@login_required
def student_page(request, edclass, semester, assignmentname):
    # REGEX below finds EG,ED, EGSE, etc. in edclass and then adds a space to the
    # course code
    logging.warning("In the student page edclass:%s, semester %s" % (edclass, semester))
    edclasssubjectarea = re.match('([A-Z]+)', edclass).group(0)
    logging.warning("In the student page edclass:%s, semester %s" % (edclass, semester))
    edclasscoursenumber = re.search('([0-9]{4})', edclass).group(0)
    edclasssectionnumber = re.search('[0-9]{2}$', edclass).group(0)
    logging.warning("In the student page subject:%s, course %s section %s" % (
    edclasssubjectarea, edclasscoursenumber, edclasssectionnumber))
    # Filter the class basedupon semester and name of the class
    edclassesPulled = get_object_or_404(EdClasses, semester__text=semester,
                                        subject=edclasssubjectarea,
                                        coursenumber=edclasscoursenumber,
                                        teacher=request.user,
                                        sectionnumber=edclasssectionnumber)
    logging.info("The classes pulled are %s" % (edclassesPulled))
    students = Student.objects.filter(edclasses=edclassesPulled, enrollment__rubriccompleted=False,
                                      enrollment__semester__text=semester)
    for i in students:
        logging.info("Students are %s" % (i.lnumber))
    if request.method == 'POST':
        # Why is adding the forward slash unneccessary?
        # Why does the redirect no need the edclass added to the beginning?
        return redirect(re.sub('[\s+]', '', request.POST['studentnames']) + '/')
    return render(request, 'rubricapp/student.html', {'students': students, 'semester': semester})


# TODO fix studentname variable.  Change to studentlnumber
# TODO add system log

@login_required
def rubric_page(request, edclass, studentname, semester, assignmentname):
    # edclassspaceadded = re.sub('([A-Z]+)', r'\1 ', edclass)
    edclasssubjectarea = re.match('([A-Z]+)', edclass).group(0)
    edclasscoursenumber = re.search('([0-9]{4})', edclass).group(0)
    edclasssectionnumber = re.search('[0-9]{2}$', edclass).group(0)
    # This returns the class
    edclassenrolled = get_object_or_404(EdClasses, subject=edclasssubjectarea, coursenumber=edclasscoursenumber,
                                        teacher=request.user, sectionnumber=edclasssectionnumber)
    # This returns the student
    student = Student.objects.get(lnumber=studentname)
    # this returns the rubric associated with the class
    edclasssemester = Assignment.objects.get(edclass=edclassenrolled, semester__text=semester, assignmentname=assignmentname)
    rubricforclass = edclasssemester.keyrubric.get()
    # this returns the rows associated with the magic rubric
    rows = Row.objects.filter(rubric=rubricforclass)
    greatEnrollment = Enrollment.objects.get(student=student, edclass=edclassenrolled)
    if request.method == 'POST':
        # this should return a single Enrollment object
        logging.info("Posting")
        RowFormSetWeb = RowFormSet(request.POST)
        try:
            RowFormSetWeb.clean()
            savedFormset = RowFormSetWeb.save(commit=False)
            # Not sure if the below is necessary.  But it works!
            for i in savedFormset:
                # i.rubric = rubricafterpost
                # instead of saving entire formset, this will only update row_choice
                # this keeps the form.text fields from disappearing
                i.save(update_fields=['row_choice'])
                logging.info("The rubric associated with the row is %d" % i.rubric.id)
                rubricid = i.rubric.id
            greatEnrollment.rubriccompleted = True
            # Set the enrollment object to the new rubric created by accessing the page
            greatEnrollment.completedrubric = Rubric.objects.get(pk=rubricid)
            greatEnrollment.save()
            logging.info("Great enrollment rubric completed  is %s" % greatEnrollment.rubriccompleted)
            logging.info("Great enrollment id is %d" % greatEnrollment.pk)
            return redirect('/assessment/' + semester + '/' + edclass + '/')
        except ValidationError:
            # Hard coding error message not ideal, but I was having real issues
            # with having the RowFormSet to post an error message.
            errorrow = "You must choose a value for all rows!"
            RowsForCompletedRubric = RowFormSet(queryset=Row.objects.filter(rubric=rubricforclass))
            # Zipping the two lists allows you to iterate both the RowFormSet and the rows once
            # and not show n^2 rows or form set
            zippedformandrows = zip(RowFormSetWeb, rows)
            return render(request, 'rubricapp/rubricnotcompleted.html', {'studentlnumber': student.lnumber,
                                                                         'studentname': student.lastname + ", " + student.firstname,
                                                                         'RowFormSetWeb': RowsForCompletedRubric,
                                                                         'rows': zippedformandrows,
                                                                         'edclass': edclass,
                                                                         'semester': semester,
                                                                         'errorrow': errorrow,
                                                                         'rubricForClass': rubricforclass.name.title()})
    else:
        # This view returns a brandnew copy of the rubric based upon
        # the rubric associated with the edclass
        # rubricforclass = edclassenrolled.keyrubric.get()
        edclasssemester = Assignment.objects.get(edclass=edclassenrolled, semester__text=semester, assignmentname=assignmentname)
        rubricforclass = edclasssemester.keyrubric.get()
        oldrubricname = rubricforclass.name
        rows = Row.objects.filter(rubric=rubricforclass)
        logging.info("Get Rubric: " + str(rubricforclass.pk) + " " + str(type(rubricforclass)) + " " + str(
            [row for row in rows]) + "\n")
        rubricforclass.pk = None
        rubricforclass.name = "%s%s%s" % (edclass, studentname, semester)
        rubricforclass.template = False
        try:
            rubricforclass.full_clean()
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
            return render(request, 'rubricapp/rubric.html', {'studentlnumber': student.lnumber,
                                                             'studentname': student.lastname + ", " + student.firstname,
                                                             'RowFormSetWeb': RowFormSetWeb, 'rows': rows,
                                                             'edclass': edclass,
                                                             'rubricForClass': rubricForClassText.title(),
                                                             'semester': semester})
        except ValidationError:
            # Validationerror because a name for the rubric as already been completed
            # Checks if rubriccompleted is False.  Shows rubric if it is
            if greatEnrollment.rubriccompleted == False:
                rubricname = "%s%s%s" % (edclass, studentname, semester)
                noncompletedrubric = Rubric.objects.get(name=rubricname)
                rows = Row.objects.filter(rubric=noncompletedrubric)
                RowFormSetWeb = RowFormSet(queryset=Row.objects.filter(rubric=noncompletedrubric))
                return render(request, 'rubricapp/rubric.html', {'studentlnumber': student.lnumber,
                                                                 'studentname': student.lastname + ", " + student.firstname,
                                                                 'RowFormSetWeb': RowFormSetWeb,
                                                                 'rows': rows,
                                                                 'edclass': edclass,
                                                                 'rubricForClass': oldrubricname.title(),
                                                                 'semester': semester,})
            else:
                error = "You have already completed a rubric for this student."
                greatEnrollment.save()
                return render(request, 'rubricapp/rubric.html', {'studentlnumber': student.lnumber,
                                                                 'studentname': student.lastname + ", " + student.firstname,
                                                                 'rows': rows,
                                                                 'edclass': edclass,
                                                                 'rubricForClass': oldrubricname.title(),
                                                                 'semester': semester,
                                                                 'error': error})


@login_required
def user_page(request):
    return render(request, 'rubricapp/userpage.html', {'user': request.user,})
