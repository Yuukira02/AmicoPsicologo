from types import NoneType
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.forms import ValidationError


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    birth_date = models.DateField(null=True, blank=True)


class PsychologistProfile(UserProfile):
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images/')

    description = models.TextField()
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.avatar.path) # Open image

        # resize image
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size) # Resize image
            img.save(self.avatar.path) # Save it again and override the larger image

class Rating(models.Model):
    user_from = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="ratings")
    psycho_to = models.ForeignKey(PsychologistProfile, on_delete=models.CASCADE, related_name="received_ratings")
    
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    comment = models.CharField(max_length=750, null=True)
    last_updated = models.DateField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_from', 'psycho_to'], name='unique_rating_given_user_and_psy'
            )
        ]
        
    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Valutazione non valida. Deve essere tra 1 e 5.")
    
    def __str__(self):
        return self.comment[:50]

@receiver(post_save, sender=Rating)
def save_psycho_profile(sender, instance, **kwargs):
    psycho = instance.psycho_to
    ratings = psycho.received_ratings.all()
    if ratings.exists():
        valid_ratings = [r.rating for r in ratings if r.rating is not None]
    
    if valid_ratings:  
        avg_rating = sum(valid_ratings) / len(valid_ratings)
    else:
        avg_rating = None

    psycho.average_rating = avg_rating
    psycho.save()
