#  -*- coding: utf-8 -*-
"""
This module manage interaction between application and
OpenStack cloud infrastructure

"""
import math

from datetime import date
from dateutil.relativedelta import relativedelta

from django.core.cache import cache
from django.utils.dateparse import parse_datetime

from keystoneauth1.identity import v3
from keystoneauth1 import session, exceptions as ksexceptions
from keystoneclient.v3 import client as ksclient
from novaclient import client as nvclient

from openstack_lease_it.settings import GLOBAL_CONFIG, LOGGER_INSTANCES
from lease_it.datastore import InstancesAccess, LEASE_DURATION
from lease_it.backend.Exceptions import PermissionDenied

from lease_it.models import Instances

# Define nova client version as a constant
NOVA_VERSION = 2

# Default cache timeout (in sec)
FLAVOR_CACHE_TIMEOUT = 86400
USERS_CACHE_TIMEOUT = 86400
PROJECTS_CACHE_TIMEOUT = 86400
INSTANCES_CACHE_TIMEOUT = 86400


class OpenstackConnection(object):  # pylint: disable=too-few-public-methods
    """
    This class manage interface between OpenStack Cloud infrastructure and
    views.
    """
    def __init__(self):
        """
        During class initialization, we create a connection to
        OpenStack Cloud
        """
        super(OpenstackConnection, self).__init__()
        # We need to be admin to have access to hypervisor list
        credentials = dict()
        credentials['username'] = GLOBAL_CONFIG['OS_USERNAME']
        credentials['password'] = GLOBAL_CONFIG['OS_PASSWORD']
        credentials['auth_url'] = GLOBAL_CONFIG['OS_AUTH_URL']
        credentials['project_name'] = GLOBAL_CONFIG['OS_PROJECT_NAME']
        credentials['project_domain_name'] = GLOBAL_CONFIG['OS_PROJECT_DOMAIN_NAME']
        credentials['user_domain_name'] = GLOBAL_CONFIG['OS_USER_DOMAIN_NAME']

        try:
            auth = v3.Password(**credentials)
            self.session = session.Session(auth=auth,
                                           verify=GLOBAL_CONFIG['OS_CACERT'])
        except:  # pylint: disable=bare-except
            pass

    def _instances(self):
        """
        List of instances actually launched
        :return: dict()
        """
        response = cache.get('instances')
        if not response:
            response = dict()
            nova = nvclient.Client(NOVA_VERSION, session=self.session)
            data_instances = nova.servers.list(search_opts={'all_tenants': 'true'})
            for instance in data_instances:
                response[instance.id] = {
                    'user_id': instance.user_id,
                    'project_id': instance.tenant_id,
                    'id': instance.id,
                    'name': instance.name,
                    'created_at': parse_datetime(instance.created).date()
                }
            cache.set('instances', response, INSTANCES_CACHE_TIMEOUT)
        return response

    def _hypervisors(self):
        """
        List of hypervisors and their details
        :return: dict()
        """
        nova = nvclient.Client(NOVA_VERSION, session=self.session)
        hypervisors = nova.hypervisors.list()
        response = list()
        for hypervisor in hypervisors:
            response.append({
                'status': hypervisor.status,
                'state': hypervisor.state,
                'vcpus': hypervisor.vcpus,
                'vcpus_used': hypervisor.vcpus_used,
                'free_ram': hypervisor.free_ram_mb,
                'memory': hypervisor.memory_mb,
                'free_disk': hypervisor.free_disk_gb,
                'local_disk': hypervisor.local_gb
            })
        return response

    def _flavors(self):
        """
        List of flavors and their details
        """
        # We retrieve information from memcached
        response = cache.get('flavors')
        if not response:
            response = dict()
            nova = nvclient.Client(NOVA_VERSION, session=self.session)
            flavors = nova.flavors.list()
            for flavor in flavors:
                response[flavor.name] = {
                    'name': flavor.name,
                    'disk': int(flavor.disk),
                    'ram': int(flavor.ram),
                    'cpu': int(flavor.vcpus)
                }
            cache.set('flavors', response, FLAVOR_CACHE_TIMEOUT)
        return response

    def _domains(self):
        """
        List all domains available
        :return: dict()
        """
        response = cache.get('domains')
        if not response:
            response = dict()
            keystone = ksclient.Client(session=self.session)
            try:
                data_domains = keystone.domains.list()
            except ksexceptions.ConnectFailure:
                data_domains = list()
            for domain in data_domains:
                response[domain.id] = {
                    'id': domain.id,
                    'name': domain.name
                }
            cache.set('domain', response, USERS_CACHE_TIMEOUT)
        return response

    def _users(self):
        """
        List of users. If not on admin network, we can't retrieve information,
        so we return a None object
        :return: dict()
        """
        response = cache.get('users')
        if not response:
            response = dict()
            keystone = ksclient.Client(session=self.session)
            data_domain = self._domains()
            for domain in data_domain:
                try:
                    data_users = keystone.users.list(domain=domain)
                except ksexceptions.ConnectFailure:
                    data_users = list(domain)
                for user in data_users:
                    try:
                        user_email = user.email
                    except AttributeError:
                        user_email = ""
                    response[user.id] = {
                        'id': user.id,
                        'domain_id': domain,
                        'name': user.name,
                        'email': user_email
                    }
            cache.set('users', response, USERS_CACHE_TIMEOUT)
        return response

    def _projects(self):
        """
        List of projects on OpenStack.
        :return: dict()
        """
        keystone = ksclient.Client(session=self.session)
        try:
            projects = keystone.projects.list()
        except ksexceptions.ConnectFailure:
            projects = None
        return projects

    def flavors(self):
        """
        Return a list of flavor and a detail about

            - Their properties (CPU / Disk / RAM)
            - The actual Cloud state (number of VM we can start, maximum VM we can start if empty)

        :return: dict()
        """
        flavors = self._flavors()
        # Retrieve hypervisor status to populate response
        hypervisors = self._hypervisors()

        # For each flavor, we look @ each hypervisor how many of
        # it can be launch @ the current state and the maximum value
        # based on flavor
        # * disk
        # * CPU
        # * RAM
        for flavor in flavors:
            free_flavor = 0
            max_flavor = 0
            for hypervisor in hypervisors:
                # If hypervisor is disable or down we don't care of it
                if hypervisor['status'] == "enabled" and\
                                hypervisor['state'] == "up":
                    # We round down the number of flavor
                    free_cpu = math.floor((hypervisor['vcpus'] - hypervisor['vcpus_used']) /
                                          flavors[flavor]['cpu'])
                    max_cpu = math.floor(hypervisor['vcpus'] / flavors[flavor]['cpu'])
                    free_ram = math.floor(hypervisor['free_ram'] / flavors[flavor]['ram'])
                    max_ram = math.floor(hypervisor['memory'] / flavors[flavor]['ram'])
                    free_disk = math.floor(hypervisor['free_disk'] / flavors[flavor]['disk'])
                    max_disk = math.floor(hypervisor['local_disk'] / flavors[flavor]['disk'])

                    # We keep the lowest value of ram / cpu / disk as it s
                    # the weak link of the hypervisor
                    if min(free_cpu, free_ram, free_disk) > 0:
                        free_flavor += min(free_cpu, free_ram, free_disk)
                    if min(max_cpu, max_ram, max_disk) > 0:
                        max_flavor += min(max_cpu, max_ram, max_disk)
            flavors[flavor]['free'] = free_flavor
            flavors[flavor]['max'] = max_flavor
        return flavors

    def instances(self, request, filtered=False):
        """
        List all instances started on cluster and owned by user

        :param request: Web request, used to retrieve user id
        :param filtered: True if we only return user_id instances
        :return: dict()
        """
        response = dict()
        data_instances = self._instances()
        # We only display instances that are owned by logged user
        for instance in data_instances:
            if data_instances[instance]['user_id'] == request.user.id or not filtered:
                response[data_instances[instance]['id']] = data_instances[instance]
        return InstancesAccess.show(response)

    def users(self):
        """
        Return a list of users w/ attributes
        id, first_name, last_name and email

        :return: dict of users
        """
        return self._users()

    def projects(self):
        """
        Return a list of project w/ there id and name

        :return: dict()
        """
        # We retrieve information from memcached
        response = cache.get('projects')
        if not response:  # If not on memcached, we ask OpenStack
            response = dict()
            data_projects = self._projects()
            if data_projects is not None:
                for project in data_projects:
                    response[project.id] = {
                        'id': project.id,
                        'name': project.name
                    }
            cache.set('projects', response, PROJECTS_CACHE_TIMEOUT)
        return response

    @staticmethod
    def lease_instance(request, instance_id):
        """
        If instance_id is owned by user_id, then update lease information, if not, raise
        PermissionDenied exception.
        A Openstack administrator can also update a lease for a user

        :param instance_id: id of instance
        :param request: Web request
        :return: void
        """
        data_instances = cache.get('instances')
        if data_instances[instance_id]['user_id'] != request.user.id and \
                not request.user.is_superuser:
            raise PermissionDenied(request.user.id, instance_id)
        InstancesAccess.lease(data_instances[instance_id])
        InstancesAccess.heartbeat(data_instances[instance_id])
        return data_instances[instance_id]

    def delete(self, instance_id):
        """
        Deletes the VM with the id given in parameter

        :param instance_id: id of instance to delete
        :return: void
        """
        if bool(GLOBAL_CONFIG['OS_DELETE']):
            nova = nvclient.Client(NOVA_VERSION, session=self.session)
            to_delete = nova.servers.list(search_opts={'id': instance_id})
            for instance in to_delete:
                instance.delete()
        else:
            print("Deleted the instance " + instance_id + " from Openstack")

    def spy_instances(self):
        """
        spy_instances is started by instance_spy module and check all running VM + notify user
        if a VM is close to its lease time + update lease duration according to the lease duration settings

        :return: dict()
        """
        now = date.today()
        data_instances = InstancesAccess.show(self._instances())
        users = self._users()
        response = {
            'delete': list(),  # List of instance we must delete
            'notify': list()  # List of instance we must notify user to renew the lease
        }
        for instance in data_instances:
            # We mark the VM as shown
            InstancesAccess.heartbeat(data_instances[instance])
            user_name = users[data_instances[instance]['user_id']]['name']
            instance_name = data_instances[instance]['name']
            if data_instances[instance]['project_id'] not in GLOBAL_CONFIG["EXCLUDE"] and \
                    user_name not in GLOBAL_CONFIG["EXCLUDE"]:
                leased_at = data_instances[instance]['leased_at']
                lease_end = data_instances[instance]['lease_end']
                lease_duration = LEASE_DURATION
                # If the instance benefits from a special lease (from its user_name, instance_id or project_id),
                # we update the lease_duration (used to determine whether to delete it or not)
                # and the instance's lease duration
                if user_name in GLOBAL_CONFIG['SPECIAL_LEASE_DURATION']:
                    lease_duration = GLOBAL_CONFIG['SPECIAL_LEASE_DURATION'][user_name]
                if instance_name in GLOBAL_CONFIG['SPECIAL_LEASE_DURATION']:
                    lease_duration = GLOBAL_CONFIG['SPECIAL_LEASE_DURATION'][instance_name]
                elif data_instances[instance]['project_id'] in GLOBAL_CONFIG['SPECIAL_LEASE_DURATION']:
                    lease_duration = GLOBAL_CONFIG['SPECIAL_LEASE_DURATION'][data_instances[instance]['project_id']]
                elif data_instances[instance]['id'] in GLOBAL_CONFIG['SPECIAL_LEASE_DURATION']:
                    lease_duration = GLOBAL_CONFIG['SPECIAL_LEASE_DURATION'][data_instances[instance]['id']]
                model = Instances.objects.get(id=data_instances[instance]['id'])
                model.lease_duration = lease_duration
                model.save()

                # If it's a new instance, we put lease value as today
                # it's not necessary to lease on model as heartbeat should have create and
                # lease the virtual machine
                if leased_at is None:
                    lease_end = now + relativedelta(days=+lease_duration)
                first_notification_date = lease_end - relativedelta(days=+lease_duration/3)
                second_notification_date = lease_end - relativedelta(days=+lease_duration/6)
                LOGGER_INSTANCES.info(
                    "Instance: %s will be notify %s and %s",
                    data_instances[instance]['id'],
                    first_notification_date,
                    second_notification_date,
                )
                # If lease has expired and it's not in the excluded projects, we tag it as delete
                if lease_end < now:
                    response['delete'].append(data_instances[instance])
                elif first_notification_date == now or \
                        second_notification_date == now or \
                        lease_end < now - relativedelta(days=-6):
                    response['notify'].append(data_instances[instance])
        return response
