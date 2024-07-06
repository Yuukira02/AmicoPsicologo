from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django import forms
from .models import *


# NOTA: aggiunto i gruppi Clients e Psychologists da pannello admin

class CreateUser(UserCreationForm):
    first_name = forms.CharField(max_length=50, label="Il suo nome")
    last_name = forms.CharField(max_length=50, label="Il suo cognome")
    email = forms.EmailField()
    birth_date = forms.DateField()

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name', ]

    def username_clean(self):  
        username = self.cleaned_data['username'].lower()  
        new = User.objects.filter(username = username)  
        if new.count():  
            raise forms.ValidationError("User Already Exist")  
        return username  
  
    def email_clean(self):  
        email = self.cleaned_data['email'].lower()  
        new = User.objects.filter(email=email)  
        if new.count():  
            raise forms.ValidationError("Email Already Exist")  
        return email


class CreateClientUser(CreateUser):    
    # valid date example: 10/25/2006
    def save(self, commit=True):
        user = super().save(commit)

        user_profile = UserProfile.objects.create(
            user=user,
            birth_date=self.cleaned_data['birth_date']
        )
        user_profile.save()

        # TODO: unit testing
        g = Group.objects.get(name="Clients") 
        g.user_set.add(user) 
        return user 
    
class CreatePsychologistUser(CreateUser):
    def save(self, commit=True):
        user = super().save(commit) 
        user.is_staff = True
        user.save()

        psychologist_profile = PsychologistProfile.objects.create(
            user=user,
            birth_date=self.cleaned_data['birth_date'],
        )
        psychologist_profile.save()

        g = Group.objects.get(name="Psychologists") 
        g.user_set.add(user) 
        return user 


#  nota: devo fare l'opzione di EDITARE il profilo. 
class ChangeUserForm(forms.ModelForm):    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ChangeClientProfileForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ('birth_date',)

class ChangePsyProfileForm(forms.ModelForm):
    def save(self, commit=True):
        user_profile = super().save(commit) 
        user_profile.birth_date = self.cleaned_data["birth_date"]
        try:
            psyprofile = user_profile.psychologistprofile
            psyprofile.description = self.cleaned_data["description"]
            psyprofile.avatar = self.cleaned_data["avatar"]
        except PsychologistProfile.DoesNotExist:
            errors += "You are trying to save data that is not inherent to a client..."
            print(errors)
        finally: 
            if commit==True:
                psyprofile.save()
            return psyprofile 
    
    class Meta:
        model = PsychologistProfile
        fields = ('birth_date', 'description', 'avatar',)

    def __init__(self, *args, **kwargs):
        super(ChangePsyProfileForm, self).__init__(*args, **kwargs)
        try:
            self.fields['description'].initial = self.instance.psychologistprofile.description
            self.fields['avatar'].initial = self.instance.psychologistprofile.avatar   
        except PsychologistProfile.DoesNotExist:
            errors = "You are trying to save data that is not inherent to a client..."
            print(errors)

        print("Descrizione iniziale è :"+str(self.instance.psychologistprofile.description))

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']

        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.5, }),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

        labels = {
            'rating':'Valutazione',
            'comment':'Commento'
        }


    # widgets = {
    #     'description': forms.widgets.Textarea()
    # }