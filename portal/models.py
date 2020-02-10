from django.contrib.auth.models import User, Group
from django.db import models


class Tag(models.Model):
    label = models.CharField(max_length=64, primary_key=True)
    protected = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)

    def __str__(self): return self.label


class Project(models.Model):
    name = models.CharField(max_length=256)
    image = models.CharField(max_length=64)

    path = models.CharField(max_length=256)
    dir_name = models.CharField(max_length=256)
    default = models.CharField(max_length=128, blank=True)
    tags = models.ManyToManyField(Tag, related_name='projects', blank=True)

    description = models.TextField(blank=True)
    authors = models.CharField(max_length=256, blank=True)
    quality = models.CharField(max_length=32, blank=True)

    def __str__(self): return self.name


class ProjectAccess(models.Model):
    user = models.ForeignKey(User, null=True, related_name='access')
    group = models.ForeignKey(Group, null=True, related_name='access')
    project = models.ForeignKey(Project, related_name='access')
    owner = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'group', 'project')

    def __str__(self): return str(self.user)  # + ' | ' + str(self.group) + ' | ' + str(self.project)


class PublishedProject(models.Model):
    name = models.CharField(max_length=256)
    image = models.CharField(max_length=64)
    source = models.OneToOneField(Project, related_name='published', null=True)

    path = models.CharField(max_length=256)
    default = models.CharField(max_length=128, blank=True)

    description = models.TextField(blank=True)
    authors = models.CharField(max_length=256, blank=True)
    quality = models.CharField(max_length=32, blank=True)

    published = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)
    copied = models.IntegerField(default=1)

    def __str__(self): return self.name
