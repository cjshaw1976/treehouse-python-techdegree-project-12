from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'accounts/login/$', views.sign_in),
    url(r'signin/$', views.sign_in, name='signin'),
    url(r'signup/$', views.sign_up, name='signup'),
    url(r'signout/$', views.sign_out, name='signout'),
    url(r'profile/$', views.profile, name='my_profile'),
    url(r'profile/(?P<pk>\d+)/$', views.profile, name='profile'),
    url(r'profile/edit/$', views.profile_edit, name='profile_edit'),
    url(r'profile/crop/$', views.profile_crop, name='profile_crop'),
    url(r'^ajax/skills/$', views.list_skills, name='list_skills'),
    url(r'^ajax/skills/add/$', views.list_skills_add, name='list_skills_add'),
    url(r'^ajax/skills/remove/$', views.list_skills_remove, name='list_skills_remove'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
]
