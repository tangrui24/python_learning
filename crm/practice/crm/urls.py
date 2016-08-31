from django.conf.urls import url,include
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^logout/$', views.acc_logout),
    url(r'^(\w+)/$', views.show_class_info, name='show'),
    url(r'^(\w+)/add/$', views.add, name='add'),
    url(r'^(\w+)/(\d+)/$', views.change, name='change'),
]