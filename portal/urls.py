from rest_framework import routers

from portal.views import UserViewSet, GroupViewSet, ProjectViewSet, PublishedProjectViewSet, ProjectAccessViewSet, TagViewSet

router = routers.DefaultRouter()

router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'tags', TagViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'access', ProjectAccessViewSet)
router.register(r'notebooks', PublishedProjectViewSet)
