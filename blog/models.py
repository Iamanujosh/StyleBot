from django.db import models
from django.contrib.auth.models import User
# Profile model to extend the User model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to the User model
    BODY_TYPE_CHOICES = [
        ('Apple', 'Apple'),
        ('Pear', 'Pear'),
        ('Hourglass', 'Hourglass'),
        ('Rectangle', 'Rectangle'),
        ('Curvy', 'Curvy'),
        ('Plus Size', 'Plus Size')
    ]
    SKIN_TONE_CHOICES = [
        ('Fair', 'Fair'),
        ('Medium', 'Medium'),
        ('Olive', 'Olive'),
        ('Dark', 'Dark')
    ]
    AGE_GROUP_CHOICES = [
        ('Teens', 'Teens (13-19)'),
        ('20s', '20s'),
        ('30s', '30s'),
        ('40s', '40s and above')
    ]
    body_type = models.CharField(max_length=20, choices=BODY_TYPE_CHOICES)
    skin_tone = models.CharField(max_length=20, choices=SKIN_TONE_CHOICES)
    height = models.IntegerField()  # Height in cm
    weight = models.IntegerField()  # Weight in kg
    location = models.CharField(max_length=100)  # User's location/climate
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES)
    def __str__(self):
        return f'{self.user.username} Profile'
#To ensure a profile is created or updated when a user is created or updated
from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()