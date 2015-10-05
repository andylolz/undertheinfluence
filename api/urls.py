from django.conf.urls import url, include
from rest_framework import routers
from api import views


router = routers.DefaultRouter()

router.register(r'actors', views.ActorViewSet)
router.register(r'donations', views.DonationViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'actors/(?P<pk>\d+)/donations_from', views.ActorReceivedDonationsFromListViewSet.as_view()),
    url(r'actors/(?P<pk>\d+)/donations_to', views.ActorDonatedToListViewSet.as_view()),
]
