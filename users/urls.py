app_name = "users"

from django.contrib import admin
from django.urls import include, path

from .views import *

urlpatterns = [
    path("psychologists/", PsychoList.as_view(), name="psychologists"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("registerpsy", PsychoCreateView.as_view(), name="registerpsy"),

    path("public_profile/<str:pk>", PublicProfileView.as_view(), name="public_profile"),

    path("myratings", myRatings, name="myratings"),
    path("rating/<str:pk>", create_or_update_rating, name="create_or_update_rating"),
    path("rating/update/<str:pk>", DeleteRating.as_view(), name="delete_rating"),
    
    path("change_profile", update_profile, name="change_profile"),
    path("myprofile/<str:pk>", MyProfile.as_view() , name="myprofile"),

]