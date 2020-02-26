from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from portal.hub import spawn_server, delete_server, stop_server, encode_name, zip_project, unzip_project
from portal.models import Project, ProjectAccess, PublishedProject, Tag
from portal.serializers import UserSerializer, GroupSerializer, ProjectSerializer, ProjectAccessSerializer, \
    PublishedProjectSerializer, TagSerializer, PublishedProjectGetSerializer, ProjectGetSerializer
from portal.utils import create_tags, create_access, model_from_url, get_copy_path


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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET': return ProjectGetSerializer
        else: return ProjectSerializer

    def list(self, request, *args, **kwargs):
        if request.user.is_staff: queryset = Project.objects.all()
        else: queryset = Project.objects.filter(access__user=request.user)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        dir_name = encode_name(request.data['name'])  # Set the name of the directory to mount
        create_tags(request.data['tags'])             # Lazily create tags for the notebook
        spawn_server(user=request.user, server_name=dir_name, image=request.data['image'])
        response = super(ProjectViewSet, self).create(request, *args, dir_name=dir_name, **kwargs)  # Create the model
        instance = model_from_url(Project, response.data['url'])
        create_access(request.user, instance)  # Grant the user access to the project
        return response

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        create_tags(request.data['tags'])  # Lazily create tags for the notebook
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'GET': return PublishedProjectGetSerializer
        else: return PublishedProjectSerializer

    def create(self, request, *args, **kwargs):
        project = model_from_url(Project, request.data['source'])
        dir_name = encode_name(project.dir_name)      # Set the name of the directory to zip
        id = f"{request.user}-{dir_name}"
        zip_project(id=id, user=request.user, server_name=dir_name)
        return super(PublishedProjectViewSet, self).create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        instance = self.get_object()
        unzip_project(copy='tabor-Crown', user=request.user, server_name=instance.source.dir_name)
        spawn_server(user=request.user, server_name=instance.source.dir_name, image=instance.image)
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)