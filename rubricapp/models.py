from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

class Student(models.Model):
    firstname = models.CharField(default="", max_length=1)
    lastname = models.CharField(default="", max_length=1)
    lnumber = models.CharField(default="", unique=True, max_length=4)

    def __str__(self):
        return self.firstname + " " + self.lastname



class Rubric(models.Model):
    name = models.TextField(default="Basic Rubric", unique=True)
    template = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CompletedRubric(Rubric):

    def __str__self(self):
        return self.name

class Semester(models.Model):
    text = models.TextField(default='201530', unique=True)
    #classes = models.ManyToManyField(EdClasses)

    def __str__(self):
        return self.text


class EdClasses(models.Model):

    CHOICES = (
    ('EG', "Graduate Education",),
    ('EGSE', "Special Education",),
    ('EGEL', "English Language Learning"),
    ('MAED', 'Math Education'),
    ('ED', "Undergraduate Education"),
    )

    crn = models.CharField(max_length=5, unique=True, null=False)
    subject = models.CharField(max_length=4, choices=CHOICES, default="EG")
    coursenumber = models.CharField(default='', blank=False, max_length=4)
    sectionnumber = models.CharField(max_length=2, blank=False)
    students = models.ManyToManyField(Student, through="Enrollment")
    #keyrubric = models.ManyToManyField(Rubric)
    semester = models.ForeignKey(Semester)
    teacher = models.ForeignKey(User)

    def __str__(self):
        return "{} {} {} {}".format(self.subject,self.coursenumber, self.sectionnumber, self.semester)


class Assignment(models.Model):
    assignmentname = models.CharField(default="None", max_length=30)
    edclass = models.ForeignKey(EdClasses, null=False)
    keyrubric = models.ForeignKey(Rubric)

    def __str__(self):
        return "{}{}{}{}".format(self.edclass.subject, self.edclass.coursenumber, self.edclass.sectionnumber, self.assignmentname)
      
    class Meta:
        unique_together = ("edclass",  "assignmentname")

class Standard(models.Model):
    name = models.CharField(null=False, max_length=50)
    detail = models.TextField(null=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "detail")

class Row(models.Model):
    CHOICES = (
    ('0', 'Your string for display'),
    ('4','Exemplary'),
    ('3','Proficient'),
    ('2','Partially Proficient'),
    ('1','Incomplete'),
    )
    name = models.CharField(default="None", max_length=100)
    rubric = models.ForeignKey(Rubric)
    row_choice = models.CharField(max_length=20,choices=CHOICES, default="0")
    excellenttext = models.TextField(default="", blank=True)
    proficienttext = models.TextField(default="", blank=True)
    satisfactorytext = models.TextField(default="", blank=True)
    unsatisfactorytext = models.TextField(default="", blank=True)
    standards = models.ManyToManyField(Standard)
    templatename= models.CharField(default="", max_length=100)

    def save(self, *args, **kwargs):
        if self.rubric.template == "True":
            self.templatename = self.rubric.name
            super(Row, self).save(*args,**kwargs)
        else:
            super(Row, self).save(*args,**kwargs)

    def __str__(self):
        return self.row_choice


class Enrollment(models.Model):
    student = models.ForeignKey(Student, null=False)
    edclass = models.ForeignKey(EdClasses, null=False)
    #semester = models.ForeignKey(Semester)
    #Will need to change completedrubric editable to False
    #completedrubric = models.OneToOneField(Rubric, null=True, editable=False)
    #rubriccompleted = models.BooleanField(default=False)
    dataforrubric = models.ManyToManyField(Assignment, through="RubricData")

    def encode_class_name_for_admin(self,obj):
        return self.edclass.name

    def __str__(self):
        return 'Enrollment %s: %s' % (self.student, self.edclass)

    class Meta:
       unique_together = (("student", "edclass"))

class RubricData(models.Model):
    rubriccompleted = models.BooleanField(default=False)
    enrollment = models.ForeignKey(Enrollment)
    assignment = models.ForeignKey(Assignment)
    completedrubric = models.OneToOneField(Rubric, null=True, editable=False)

    def __str__(self):
        return "{} {}".format(self.enrollment, self.assignment)

    class Meta:
        unique_together = ("enrollment", "assignment")


