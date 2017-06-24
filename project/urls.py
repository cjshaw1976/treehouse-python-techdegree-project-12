from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.project, name='project'),
    url(r'^new/$', views.project_editor, name='new'),
    url(r'^edit/(?P<pk>\d+)/$', views.project_editor, name='edit'),
    url(r'^apply/$', views.project_apply, name='apply'),
    url(r'^select/$', views.position_select, name='select'),
    url(r'^reject/$', views.position_reject, name='reject'),
    url(r'^recommended/$', views.project_recommended, name='recommended'),
    url(r'^applications/$', views.project_applications, name='applications'),
]
