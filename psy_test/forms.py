from django import forms
from django.shortcuts import get_object_or_404
from .models import PsyTest

class UploadAnswerTest(forms.Form):
    questions = forms.ModelChoiceField
    def __init__(self, slug, *args, **kwargs):
        super().__init__(*args, **kwargs)
        test = get_object_or_404(PsyTest, slug=slug)
        questions = test.questions.all()
        
        for i, question in enumerate(questions): 
            self.fields[f'question_{i}'] = forms.ModelChoiceField(
                queryset=question.answers.all(),
                required=True,
                label=f"{i+1})   {question.question}",
                )
    #TODO: controllo che i dati immessi siamo tutti e validi
        

