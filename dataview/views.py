from django.shortcuts import render

# Create your views here.


def home_page(request):
	return render(request, 'dataview/dataviewhome.html', )
	
def student_view(request):
	return render(request, 'dataview/studentview.html',)
	
