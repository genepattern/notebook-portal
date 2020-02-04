from rest_framework.permissions import BasePermission, SAFE_METHODS

from portal.models import Tag


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
