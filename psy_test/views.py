from typing import Any
from urllib import request
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView
from braces.views import LoginRequiredMixin

from .forms import UploadAnswerTest
from .models import *

from django.http import HttpResponseNotFound


import logging

logger = logging.getLogger()
TAG = "PSY-TEST-view:"

"""List of all psychological tests"""
class ListTest(ListView):
    model = PsyTest
    template_name = "psy_test/home.html"
    #il suo queryset è return self.model.objects.all() --> {{object_list}}

def submitAnswers(request, slug):
    object_test = get_object_or_404(PsyTest.objects.filter(slug=slug))
    print(request.method)
    if request.method == "POST":
        #initialization of counter variable for further analysis of answers' type
        counter = {}
        for elem in ANS_TYPES:
            counter[elem] = 0

        form = UploadAnswerTest(slug, request.POST)
        if form.is_valid():
            for _, value in form.cleaned_data.items():
                counter[value.answer_type]+=1
            
            if request.user.is_authenticated: 
                test_result = TestResult.objects.get(rel_test=object_test.pk, 
                                                          answer_type=max(counter, key=counter.get))
                try: 
                    my_result = MyTestResult(user=request.user, result=test_result)
                except MyTestResult.DoesNotExist: 
                    my_result = MyTestResult()
                my_result.user = request.user
                my_result.result = test_result
                my_result.save()
            # logging.warning("Counter of types of answers: ")
            # for key, value in counter.items(): 
            #     logging.warning("Type of answer is:" + key + " with count of: " + str(value))

            # logging.warning("Risultato che vince è: "+max(counter, key=counter.get))
            return redirect("psy_test:result", slug, max(counter, key=counter.get))
    else:
        form = UploadAnswerTest(slug)
    context={"form":form, "object_test":object_test}
    return render(request, template_name="psy_test/test.html", context=context)


"""Fundamentally debug page to show quickly all test relevant info"""
class DetailTest(DetailView):
    model = PsyTest
    template_name="psy_test/test-info.html"

    def get_queryset(self) -> QuerySet[Any]:
        arg = self.kwargs["pk"]
        qs = self.model.objects.filter(pk=arg)
        # --> {{object}}
        return qs
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        arg = self.kwargs["pk"]

        questions = self.object.questions.all()
        context['questions_with_answers'] = [
            {
                'question': question.question,
                'answers': question.answers.all()
            }
            for question in questions
        ]

        return context
    

"""page with result of test"""
class DetailResult(DetailView):
    model = PsyTest
    template_name = "psy_test/test_result.html"

    def get_queryset(self) -> QuerySet[Any]:
        try: 
            slug = self.kwargs["slug"]
            qs = self.model.objects.filter(slug=slug)
        except PsyTest.DoesNotExist:
            return HttpResponseNotFound("Test not found")
        return qs
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ans_type = self.kwargs["answer_type"]
        testResult = TestResult.objects.get(rel_test=self.object, answer_type=ans_type)

        context = super().get_context_data(**kwargs)
        context["result"] = testResult
        return context

class MyTestResultList(LoginRequiredMixin, ListView):
    model = User
    template_name="psy_test/my_results.html"

    def get_queryset(self) -> QuerySet[Any]:
        all_answers = self.request.user.my_tests.all()
        return all_answers


#USEFUL TOOLS: 

# logger.warning(TAG, "cosa posso accedere da model: "+str(dir(self.model)))
# print(context.keys())
