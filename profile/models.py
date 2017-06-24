from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Extra info for user. """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(blank=True)


class Skill(models.Model):
    """Skills available to users and positions"""
    title = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.title


class UserSkill(models.Model):
    """Skills to user"""
    user = models.ForeignKey(User)
    skill = models.ForeignKey('Skill')

    class Meta:
        unique_together = (('user', 'skill'),)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
