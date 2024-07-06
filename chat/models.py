from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_w_psy")
    psycho = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_w_client")
    def __str__(self):
        return str(self.pk)


class Message(models.Model):
    rel_chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_messages")
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.message)
    class Meta:
        ordering = ['-created']
