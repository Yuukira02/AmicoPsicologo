app_name = "chat"

from django.urls import path
from .views import *

urlpatterns = [
    path("", MyChatList.as_view(), name="all"),
    path("<str:psy_pk>/<str:cli_pk>", myChat, name="my_chat_with")
    # to-do: inizia una conversazione
    # leggi chat + invia un messaggio 
]
