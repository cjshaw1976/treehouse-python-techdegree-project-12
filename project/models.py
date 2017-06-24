from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
from profile import models as profile_models


STATUS_CHOICES = (
    ('A', 'Applied'),
    ('S', 'Selected'),
    ('R', 'Rejected'),
)

class Project(models.Model):
    """Projects available"""
    user = models.ForeignKey(User)
    title = models.CharField(max_length=32)
    description = models.TextField()
    timeline = models.TextField(default='')
    requirements = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.title


class ProjectPosition(models.Model):
    """Positions for projects. Quantity = number of positions available"""
    project = models.ForeignKey('Project', verbose_name="Project")
    title = models.CharField(max_length=32)
    description = models.TextField()
    timeline = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return "{} - {}".format(self.project, self.title)

class ProjectPositionSkill(models.Model):
    """Skills needed for the position"""
    position = models.ForeignKey('ProjectPosition', verbose_name="Position")
    skill = models.ForeignKey(profile_models.Skill, verbose_name="Skill")

    class Meta:
        unique_together = (('position', 'skill'),)

    def __str__(self):
        return "{} - {}".format(self.position, self.skill)

class ProjectPositionApplication(models.Model):
    """Applications for positions. A = Applied, S = Selected, R = Rejected"""
    position = models.ForeignKey('ProjectPosition', verbose_name="Position")
    user = models.ForeignKey(User)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')

    class Meta:
        unique_together = (('user', 'position'),)

    def __str__(self):
        return "{}, {} ({})".format(self.position, self.user, self.status)
