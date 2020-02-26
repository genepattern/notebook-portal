from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.urls import resolve
from rest_framework.permissions import BasePermission, SAFE_METHODS

from portal.models import Tag, ProjectAccess


class IsOwnerOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated
        )


def create_tags(tag_list):
    if tag_list is None or len(tag_list) == 0: return;
    for label in tag_list:
        label = label.lower()
        try:
            Tag.objects.get(label=label)
        except Tag.DoesNotExist:
            Tag(label=label, protected=False, pinned=False).save()


def create_access(username, project, owner=True):
    user = User.objects.get(username=username)
    access = ProjectAccess(user=user, project=project, owner=owner)
    access.save()


def model_from_url(cls, url):
    source_path = urlparse(url).path
    resolved_func, unused_args, resolved_kwargs = resolve(source_path)
    return cls.objects.get(pk=resolved_kwargs['pk'])


def get_copy_path(data):
    # TODO: Implement
    return True