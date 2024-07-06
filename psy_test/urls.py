app_name = "psy_test"

from django.urls import path
from .views import *

urlpatterns = [
    path("", ListTest.as_view(), name="home"), 
    path("<slug:slug>/", submitAnswers, name="specific_test"),
    path("info/<str:pk>/", DetailTest.as_view(), name="info_test"),
    path("result/<str:slug>/<str:answer_type>", DetailResult.as_view(), name="result"), 
    path("myresult/<str:pk>", MyTestResultList.as_view(), name="myresult"), 

]