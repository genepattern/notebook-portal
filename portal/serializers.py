from django.contrib.auth.models import User, Group
from rest_framework import serializers

from portal.models import Tag, Project, ProjectAccess, PublishedProject


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('url', 'label', 'protected', 'pinned')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Tag.objects.all())

    class Meta:
        model = Project
        fields = ('url', 'name', 'image', 'path', 'default', 'tags', 'description', 'authors', 'quality')


class ProjectAccessSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=False, queryset=User.objects.all(), slug_field='username', allow_null=True)
    group = serializers.SlugRelatedField(many=False, read_only=False, queryset=Group.objects.all(), slug_field='name', allow_null=True)

    class Meta:
        model = ProjectAccess
        fields = ('url', 'user', 'group', 'project', 'owner')


class PublishedProjectSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Tag.objects.all())
    owners = serializers.SlugRelatedField(many=True, read_only=False, queryset=User.objects.all(), slug_field='username', allow_null=True)
    groups = serializers.SlugRelatedField(many=True, read_only=False, queryset=Group.objects.all(), slug_field='name', allow_null=True)

    class Meta:
        model = PublishedProject
        fields = ('url', 'name', 'image', 'path', 'default', 'description', 'authors', 'quality', 'published', 'updated', 'owners', 'groups', 'tags')
