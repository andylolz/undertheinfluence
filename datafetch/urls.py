from django.conf.urls import url

from .views import ActorRedirectView, ActorView, SearchView


urlpatterns = [
    url(r'^search/$', SearchView.as_view(), name='search'),

    # url(r'^api/(?P<rel_type>.+)/(?P<direction>.+)/(?P<id>\d+)/?$', ApiView.as_view()),

    url(r'^actor/(?P<pk>\d+)(?:/(?P<slug>.*))?$', ActorRedirectView.as_view(), name='actor-detail'),
    url(r'^person/(?P<pk>\d+)(?:/(?P<slug>.*))?$', ActorView.as_view(), name='person-detail'),
    url(r'^organization/(?P<pk>\d+)(?:/(?P<slug>.*))?$', ActorView.as_view(), name='organization-detail'),
]
