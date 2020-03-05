import json

from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from portal.hub import spawn_server, delete_server, stop_server, encode_name, zip_project, unzip_project
from portal.models import Project, ProjectAccess, PublishedProject, Tag
from portal.serializers import UserSerializer, GroupSerializer, ProjectSerializer, ProjectAccessSerializer, \
    PublishedProjectSerializer, TagSerializer, PublishedProjectGetSerializer, ProjectGetSerializer
from .utils import create_tags, create_access, model_from_url, is_email, get_owner


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
    filterset_fields = '__all__'


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_fields = '__all__'

    def get_serializer_class(self):
        if self.request.method == 'GET': return ProjectGetSerializer
        else: return ProjectSerializer

    def list(self, request, *args, **kwargs):
        #if request.user.is_staff: queryset = Project.objects.all()
        #else: queryset = Project.objects.filter(access__user=request.user)
        queryset = Project.objects.filter(access__user=request.user)

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
        owner = get_owner(instance)
        spawn_server(user=request.user, server_name=instance.dir_name, image=instance.image, owner=owner)
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['put'])
    def share(self, request, pk=None):
        instance = self.get_object()
        messages = []

        # Summarize the list of users with existing access
        existing_access = []
        for access in instance.access.all():
            if access.user: existing_access.append(access.user.username)

        # Create new ProjectAccess objects as requested
        new_access = []
        for access in request.data:
            new_access.append(access['user'])
            if access['user'] not in existing_access:
                # Get the user, if available, and add it to the access list
                try:
                    user = User.objects.get(username=access['user'])
                    ProjectAccess(project=instance, user=user, group=None, owner=False).save()

                # Otherwise, check to see if this is an email
                except User.DoesNotExist:
                    if is_email(access['user']):
                        # TODO: Send email
                        pass
                # Otherwise, report error
                    else:
                        messages.append(f'User {access["user"]} could not be found')
        instance.save()

        # Remove old ProjectAccess objects as requested
        to_remove = [a for a in existing_access if a not in new_access]
        for username in to_remove:
            user = User.objects.get(username=username)
            if user != request.user:
                pa = ProjectAccess.objects.get(user=user, project=instance)
                ProjectAccess.delete(pa)

        return Response(data=messages, status=status.HTTP_202_ACCEPTED)


class ProjectAccessViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project access objects to be viewed or edited.
    """
    queryset = ProjectAccess.objects.all()
    serializer_class = ProjectAccessSerializer
    permission_classes = (permissions.IsAdminUser,)
    filterset_fields = '__all__'


class PublishedProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows published projects to be viewed or edited.
    """
    queryset = PublishedProject.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filterset_fields = '__all__'

    def get_serializer_class(self):
        if self.request.method == 'GET': return PublishedProjectGetSerializer
        else: return PublishedProjectSerializer

    def create(self, request, *args, **kwargs):
        project = model_from_url(Project, request.data['source'])
        zip_project(id=project.id, user=request.user, server_name=project.dir_name)
        return super(PublishedProjectViewSet, self).create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        instance = self.get_object()
        dir_name = unzip_project(copy=str(instance.source.id), user=request.user, server_name=instance.source.dir_name)
        url = spawn_server(user=request.user, server_name=dir_name, image=instance.image)
        project = Project(name=instance.name, image=instance.image, path='/', dir_name=dir_name,
                              default=instance.default, description=instance.description, authors=instance.authors,
                              quality=instance.quality)
        project.save()
        for tag in instance.source.tags.all():
            project.tags.add(tag)
        project.save()
        create_access(request.user, project)  # Grant the user access to the project

        return Response(data={'url': url}, status=status.HTTP_201_CREATED)