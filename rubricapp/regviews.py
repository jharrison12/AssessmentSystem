from django.shortcuts import render, redirect ,get_object_or_404
from django.http import HttpResponse
from rubricapp.models import Semester, EdClasses, Student, Enrollment, Row, Rubric
from rubricapp.forms import RowForm, RowFormSet
import re, logging
from copy import deepcopy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import *
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARNING)

@login_required
def password_change(request):
	if request.method == "POST":
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid() and password_validation.validate_password(request.POST, user=request.user):
			user = form.save()
			update_session_auth_hash(request, user)
			#messages.success(request, "Your password was succesful")
			return redirect("rubricapp:home")
		else:
			raise ValidationError
	else:
		form = PasswordChangeForm(request.user)
	return render(request, 'registration/password_change_form.html', {'form': form})