#!/usr/local/bin/python2.7
"""
Views module manage interface between user and openstack-lease-it.

lease_it.views provide interaction based on REST good practice.
"""
import ast

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from lease_it import backend
from lease_it.backend import Exceptions as bckExceptions  # pylint: disable=ungrouped-imports
from lease_it.datastore.ModelAccess import InstancesAccess
from lease_it.datastore.Exceptions import StillRunning

from openstack_lease_it.settings import GLOBAL_CONFIG, LOGGER
from openstack_lease_it.decorators import superuser_required

# We load backend specify by configuration file
BACKEND_PLUGIN = getattr(backend, "{0}Connection".format(GLOBAL_CONFIG['BACKEND_PLUGIN']))
BACKEND = BACKEND_PLUGIN()  # pylint: disable=not-callable


@login_required
def dashboard(request):
    """
    The default dashboard

    :param request: Web request
    :return: HTML Rendering
    """
    return render(request, 'dashboard/dashboard.html')


@login_required
def flavors(request):  # pylint: disable=unused-argument
    """
    View for flavors request

    :param request: Web request
    :return: JsonResponse w/ list of flavor and details values
    """
    # We call our method
    response = BACKEND.flavors()
    return JsonResponse(response)


@login_required
def instances(request):  #pylint: disable=unused-argument
    """
    View for instances list

    :param request: Web request
    :return: JsonResponse w/ list of instances and details
    """
    response = list()
    # Retrieve filtered parameter on GET. It's used to display all instances or just user instances
    # In all cases, if user is not superuser, only user instances are displayed
    if 'filtered' in request.GET:
        filtered = ast.literal_eval(request.GET['filtered'])
    else:
        # By default, we filter based on user_id
        filtered = True
    # By default, we just list user instances, not all instances
    if not request.user.is_superuser:
        # If user is superuser and user are requesting admin view of instances
        # We ask a full list of instances
        filtered = True

    # We retrieve data from backend
    data_instances = BACKEND.instances(request, filtered)
    data_users = BACKEND.users()
    data_projects = BACKEND.projects()

    # We merge user and project information w/ instances
    for data_instance in data_instances:
        try:
            project = "{name}".format(
                **data_projects[data_instances[data_instance]['project_id']])
        except KeyError:
            project = data_instances[data_instance]['project_id']

        try:
            user = "{name}".format(
                **data_users[data_instances[data_instance]['user_id']])
        except KeyError:
            user = data_instances[data_instance]['user_id']
        response.append({
            'id': data_instances[data_instance]['id'],
            'name': data_instances[data_instance]['name'],
            'created_at': data_instances[data_instance]['created_at'],
            'lease_end': data_instances[data_instance]['lease_end'],
            'project': project,
            'user': user
        })
    return JsonResponse(response, safe=False)


@login_required
def instance(request, instance_id):
    """
    This is view used to for a new lease on a specific instance (http://url/instances/instance_id)
    a PermissionDenied exception is raised decided by backend. Mainly if instance is not owned by
    user but see Backend comment.

    :param request: Web request
    :param instance_id: retrieve from url
    :return: JsonResponse
    """
    response = {
        'status': 'success'
    }
    try:
        instance_info = BACKEND.lease_instance(request, instance_id)
        response['instance'] = instance_info
    except bckExceptions.PermissionDenied as error:
        LOGGER.info("Permission Denied to lease %s", instance_id)
        response = {
            'status': 'error',
            'message': error.message
        }
    return JsonResponse(response)


@superuser_required
def users(request):  # pylint: disable=unused-argument
    """
    View for users

    :param request: Web request
    :return: JsonResponse w/ list of users and details
    """
    response = BACKEND.users()
    return JsonResponse(response)


@superuser_required
def databases(request):  # pylint: disable=unused-argument
    """
    View for all entries on database, used to delete old instances data

    :param request: Web request
    :return: JSonResponse w/ list of database entries
    """
    response = InstancesAccess.get_all()
    # By default, JsonResponse refuse to serialize a list to a Json list. safe=False allow it.
    return JsonResponse(response, safe=False)


@login_required
def database(request, instance_id):  # pylint: disable=unused-argument
    """
    This view is used to delete instance from database

    :param request: Web request
    :param instance_id: instance id
    :return: JSonResponse w/ status of deletion
    """
    response = {
        'status': 'success',
        'instance': {'id': instance_id}
    }
    try:
        # We retrieve data from backend
        user_instances = BACKEND.instances(request, True)
        if request.user.is_superuser or instance_id in [k for k in user_instances]:
            InstancesAccess.delete(instance_id)
            BACKEND.delete([{'id': instance_id}])
            cache.delete('instances')

    except StillRunning as error:
        response = {
            'status': 'failed',
            'message': error.message
        }
    return JsonResponse(response)
