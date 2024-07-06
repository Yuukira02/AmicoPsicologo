from typing import Any
from django.db.models.query import QuerySet
from braces.views import GroupRequiredMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from users.models import PsychologistProfile
from .forms import ChatForm
from .models import *
import logging

logger = logging.getLogger()
TAG = "CHAT-view:"


class MyChatList(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chat/my_chat_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        my_chats = self.model.objects.filter(client=self.request.user) | self.model.objects.filter(psycho=self.request.user)
        
        return my_chats.distinct()

@login_required
def myChat(request, psy_pk, cli_pk):
    psycho = User.objects.get(id=psy_pk)
    client = User.objects.get(id=cli_pk)
    my_chat, created = Chat.objects.get_or_create(client=client, psycho=psycho)
    print(TAG, f"My_chat dati client={client} e psycho={psycho} è: {my_chat.pk}")

    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.rel_chat = my_chat
            message.author = request.user
            message.save()
        return redirect('chat:my_chat_with', psy_pk, cli_pk)
    else: 
        form = ChatForm()
        
    if created: 
        messages = None
    else: 
        messages = Message.objects.filter(rel_chat=my_chat)

    context = {
        "my_chat":my_chat, 
        "form":form, 
        "messages":messages, 
    }

    is_psy=None 
    try: 
        is_psy = request.user.profile.psychologistprofile
    except PsychologistProfile.DoesNotExist as e:
        logger.warning("Questa riga non viene mai eseguita") 
        is_psy: None

    if is_psy: 
        context["user_from"] = my_chat.psycho
        context["user_to"] = request.user
    else: 
        context["user_from"] = request.user
        context["user_to"] = my_chat.psycho
    
    return render(request, template_name="chat/my_chat.html", context=context)