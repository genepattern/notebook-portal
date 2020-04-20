from rest_framework import routers
from django.conf.urls import url
from portal.views import UserViewSet, GroupViewSet, ProjectViewSet, PublishedProjectViewSet, ProjectAccessViewSet, \
    TagViewSet, SharingInviteViewSet

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'tags', TagViewSet)
router.register(r'invites', SharingInviteViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'access', ProjectAccessViewSet)
router.register(r'notebooks', PublishedProjectViewSet)

urlpatterns = [
    url(r'^projects/user/(?P<user>.*)/dir/(?P<dir>.*)/', ProjectViewSet.as_view({'get': 'user'}))
]