"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url

from lease_it import views

urlpatterns = [  # pylint: disable=invalid-name
    # Default dashboard view
    url(r'^$', views.dashboard, name='dashboard'),

    # Flavors view
    url(r'^flavors', views.flavors, name='flavors'),

    # Instances view
    url(r'^instances[/]?$', views.instances, name='instances'),
    url(r'^instances/(?P<instance_id>[\w-]+)$', views.instance, name='instance'),

    # Database view
    url(r'^database[/]?$', views.databases, name='databases'),
    url(r'^database/(?P<instance_id>[\w-]+)$', views.database, name='database'),

    # Users view
    url(r'^users', views.users, name='users')
]
