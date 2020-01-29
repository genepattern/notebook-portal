import json

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions

from portal.hub import spawn_server, delete_server
from portal.models import Project, ProjectAccess, PublishedProject, Tag
from portal.serializers import UserSerializer, GroupSerializer, ProjectSerializer, ProjectAccessSerializer, PublishedProjectSerializer, TagSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAdminUser,)


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        spawn_server(user=request.user, server_name=request.data['name'], image=request.data['image'])
        return super(ProjectViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_server(user=request.user, server_name=instance.name)
        return super(ProjectViewSet, self).destroy(request, *args, **kwargs)


class ProjectAccessViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project access objects to be viewed or edited.
    """
    queryset = ProjectAccess.objects.all()
    serializer_class = ProjectAccessSerializer
    permission_classes = (permissions.IsAdminUser,)


class PublishedProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows published projects to be viewed or edited.
    """
    queryset = PublishedProject.objects.all()
    serializer_class = PublishedProjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
