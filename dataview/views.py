from django.shortcuts import render
from rubricapp.models import Student

# Create your views here.


def home_page(request):
	return render(request, 'dataview/dataviewhome.html', )
	
def student_view(request):
	students = Student.objects.all()
	return render(request, 'dataview/studentview.html',{"students": students})
	
