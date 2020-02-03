import json

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from portal.hub import spawn_server, delete_server, stop_server, encode_name
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
        dir_name = encode_name(request.data['name'])  # Set the name of the directory to mount
        spawn_server(user=request.user, server_name=dir_name, image=request.data['image'])
        return super(ProjectViewSet, self).create(request, *args, dir_name=dir_name, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        stop_server(user=request.user, server_name=instance.dir_name)
        return super(ProjectViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_server(user=request.user, server_name=instance.dir_name)
        return super(ProjectViewSet, self).destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        instance = self.get_object()
        spawn_server(user=request.user, server_name=instance.dir_name, image=instance.image)
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)


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
