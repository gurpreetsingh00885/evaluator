from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
import requests
import json
from .models import Question, Answer
from .forms import AnswerForm
from django.forms.formsets import formset_factory



class EvaluateView(View):

	def get(self, request, *args, **kwargs):
		total_marks = sum([x.marks for x in Question.objects.all()])
		marks_obtained = sum([x.marks_awarded for x in Answer.objects.all()])
		

		context = {
		"answers": Answer.objects.all(),
		"total_marks": total_marks,
		"marks_obtained": marks_obtained,
		}
		return render(request, "evaluate.html", context)

class AnswerView(View):

	def get(self, request, *args, **kwargs):
		Answer.objects.all().delete()
		questions = Question.objects.all()
		AnswerFormSet = formset_factory(AnswerForm, extra=questions.count())
		return render(request, 'answer.html',
		                	{'formset': AnswerFormSet(),
		                	'questions': questions})

	def post(self, request, *args, **kwargs):
		AnswerFormSet = formset_factory(AnswerForm)
		formset = AnswerFormSet(request.POST)
		questions = Question.objects.all()
		for form in formset:
			print(form)
			formid = int(form.prefix[5:])
			question = questions[formid]
			text1 = question.answer
			text2 = form.data[form.prefix+"-answer"]
			token = "27cfd17d8c6a46758b2559c2e6df3388"
			marks = question.marks	#set by teacher

			url = "https://api.dandelion.eu/datatxt/sim/v1/?text1=%s&text2=%s&token=%s" %(text1.replace(" ", "%20"), text2.replace(" ", "%20"), token)

			r = requests.get(url).json()
			if "error" not in r:
				Answer.objects.create(question=question, your_response=text2 ,marks_awarded=round(0.5 * round(r["similarity"] * marks / 0.5) , 1))
			else:
				Answer.objects.create(question=question, marks_awarded=0, your_response="Unanswered." , unanswered = True)
		return HttpResponseRedirect("/evaluator/evaluate/")

class HomeView(View):
	def get(self, request, *args, **kwargs):
		return render(request, "home.html", {})