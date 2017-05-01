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

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$', 'lease_it.views.dashboard', name='dashboard'),
    url(r'^flavors', 'lease_it.views.flavors', name='flavors'),
    url(r'^instances', 'lease_it.views.instances', name='instances'),
    url(r'^users', 'lease_it.views.users', name='users')
]
