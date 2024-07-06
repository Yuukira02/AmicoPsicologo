from pyexpat.errors import messages
from typing import Any
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required


from .forms import *
from .models import *

from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.db.models.query import QuerySet

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


import logging

logger = logging.getLogger()
TAG = "USERS-view:"

"""Returns a list of psychologist users that are subscribed to the portal"""
class PsychoList(ListView):
    model = PsychologistProfile
    template_name = "users/psycho_list.html"


class UserCreateView(CreateView):
    form_class = CreateClientUser
    template_name = "users/user_register.html"
    success_url = reverse_lazy("login")


class PsychoCreateView(PermissionRequiredMixin, UserCreateView):
    permission_required = "is_superuser"
    form_class = CreatePsychologistUser


class PublicProfileView(DetailView):
    model = PsychologistProfile
    template_name = "users/public_profile.html"
    
    def get_queryset(self) -> QuerySet[Any]:
        try: 
            pk = self.kwargs["pk"]
            qs = self.model.objects.filter(pk=pk)
        except PsychologistProfile.DoesNotExist:
            return HttpResponseNotFound("Psychologist not found")        
        # --> {{object}}
        return qs


class MyProfile(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/myprofile.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        pk = self.kwargs["pk"]
        user = self.model.objects.get(pk=pk)

        context["error"] = ""

        try: 
            profile = PsychologistProfile.objects.get(user=user)
            context["psycho"] = True
        except PsychologistProfile.DoesNotExist:
            profile = UserProfile.objects.get(user=user)
            context["psycho"] = False

        context["user"] = user
        context["profile"] = profile

        if int(pk) != self.request.user.pk:
            context["error"] = "Non ha l'autorizzazione per accedere a questo profilo privato. "

        return context

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = ChangeUserForm(request.POST, instance=request.user)

        try:
            request.user.profile.psychologistprofile
            profile_form = ChangePsyProfileForm(request.POST, 
                                                request.FILES, 
                                                instance=request.user.profile)
        except PsychologistProfile.DoesNotExist as e:
            profile_form = ChangeClientProfileForm(request.POST, instance=request.user.profile)
        

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('users:myprofile', request.user.pk)
        
        else:
            logging.warning(TAG, "Ooops! non siamo riusciti a salvare i nuoovi dati in DB")
            logging.warning(f"{TAG}: User form errors: {user_form.errors}")
            logging.warning(f"{TAG}: Profile form errors: {profile_form.errors}")

    else:
        user_form = ChangeUserForm(instance=request.user)
        try:
            request.user.profile.psychologistprofile
            profile_form = ChangePsyProfileForm(instance=request.user.profile)
        except PsychologistProfile.DoesNotExist as e:
            profile_form = ChangeClientProfileForm(instance=request.user.profile)

    return render(request, 'users/change_profile.html', context={
        'user_form': user_form,
        'profile_form': profile_form
    })


"""View for accessing all of a user's ratings from profile: """
@login_required
def myRatings(request):
    user_profile = request.user.profile
    user_ratings = Rating.objects.filter(user_from=user_profile)
    context = {
        "user_profile":user_profile, 
        "ratings": user_ratings,
    }

    template_name = "my_ratings.html"
    return render(request, "users/my_ratings.html", context)


"""View: update if exists or create a rating"""
@login_required
def create_or_update_rating(request, pk):
    psycho = get_object_or_404(PsychologistProfile, id=pk)
    rating, created = Rating.objects.get_or_create(user_from=request.user.profile, psycho_to=psycho, rating=5)

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.save()
            return redirect('users:public_profile', pk=pk)
    else:
        form = RatingForm(instance=rating)

    return render(request, 'users/create_rating.html', {'form': form, 'psycho': psycho})


"""View for deleting a rating"""
class DeleteRating(DeleteView):
    model = Rating
    success_url = reverse_lazy('users:myratings')
