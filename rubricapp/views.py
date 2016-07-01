from django.shortcuts import render
from django.http import HttpResponse


def home_page(request):
	return render(request, 'home.html', {
	'semestercode': request.POST.get('submit', ''),
})



# Create your views here.
