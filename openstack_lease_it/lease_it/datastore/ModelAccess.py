# -*- coding: utf-8 -*-
"""
ModelAccess module is a interface between Django model and view
"""
import os

from dateutil.relativedelta import relativedelta

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from lease_it.models import Instances

from lease_it.datastore.Exceptions import StillRunning

from openstack_lease_it.settings import LOGGER_INSTANCES
from openstack_lease_it.settings import GLOBAL_CONFIG

# Default lease duration in day
LEASE_DURATION = 90
# Number of day we keep instance in database
HEARTBEAT_TIMEOUT = 7


class InstancesAccess(object):  # pylint: disable=too-few-public-methods
    """
    ModelAccess is a class will abstract model access for application. It
    will get / save / ... information in a format expected by views
    """
    @staticmethod
    def get(instance):
        """
        Get or Create instance on model backend

        :param instance: instance to get
        :return: Instance model
        """
        try:
            model = Instances.objects.get(id=instance['id'])  # pylint: disable=no-member
        except ObjectDoesNotExist:
            LOGGER_INSTANCES.info('Instance %s as never been seen before', instance['id'])
            model = Instances()
            model.id = instance['id']
            model.leased_at = timezone.now()
            model.heartbeat_at = timezone.now()
            model.lease_duration = LEASE_DURATION
            if instance['id'] in GLOBAL_CONFIG['SPECIAL_LEASE_DURATION']:
                model.lease_duration = GLOBAL_CONFIG['SPECIAL_LEASE_DURATION'][instance['id']]
            elif instance['name'] in GLOBAL_CONFIG['SPECIAL_LEASE_DURATION']:
                model.lease_duration = GLOBAL_CONFIG['SPECIAL_LEASE_DURATION'][instance['name']]
            # The different lease durations according to users and projects
            # will be adapted once spy_instance has run once
        return model

    @staticmethod
    def get_all():
        """
        Return all data on database

        :return: dict of data
        """
        response = list()
        model = Instances.objects.all()  # pylint: disable=no-member
        for instance in model:
            response.append({
                'instance_id': instance.id,
                'leased_at': instance.leased_at,
                'heartbeat_at': instance.heartbeat_at,
                'lease_end': instance.leased_at + relativedelta(days=+instance.lease_duration)
            })
        return response

    @staticmethod
    def show(instances):
        """
        Return a list of instances store on database

        :return: dict of instances
        """
        response = dict()
        for instance in instances:
            try:
                models = Instances.objects.get(id=instances[instance]['id'])  # pylint: disable=no-member
                leased_at = models.leased_at
                heartbeat_at = models.heartbeat_at
                lease_end = leased_at + relativedelta(days=+models.lease_duration)
            except ObjectDoesNotExist:
                LOGGER_INSTANCES.info("Instance %s not exists", instance)
                leased_at = None
                heartbeat_at = None
                lease_end = None

            response[instances[instance]['id']] = {
                'name': instances[instance]['name'],
                'id': instances[instance]['id'],
                'user_id': instances[instance]['user_id'],
                'project_id': instances[instance]['project_id'],
                'created_at': instances[instance]['created_at'],
                'leased_at': leased_at,
                'heartbeat_at': heartbeat_at,
                'lease_end': lease_end
            }
        return response

    @staticmethod
    def heartbeat(instance):
        """
        get a instance and update the heartbeat value. This method is called by
        instance-spy when it find a instance running. Heartbeat can be use to retrieve
        old Virtual Machine

        :param instance: instance to update
        :return: None
        """
        model = InstancesAccess.get(instance)
        model.heartbeat_at = timezone.now()
        model.save()
        LOGGER_INSTANCES.info('Instance %s as been heartbeated (%s)', model.id, model.heartbeat_at)

    @staticmethod
    def lease(instance):
        """
        get a instance and update the leased_at value.

        :param instance: instance to lease
        :return: None
        """
        model = InstancesAccess.get(instance)
        model.leased_at = timezone.now()
        model.save()
        LOGGER_INSTANCES.info('Instance %s as been leased (%s)', model.id, model.heartbeat_at)

    @staticmethod
    def delete(instance_id):
        """
        Remove instance entry on database. If the VM is still running, the VM will be recreated
        on next spy instance running

        :param instance_id: instance to delete
        :return: None
        """
        try:
            model = Instances.objects.get(id=instance_id)  # pylint: disable=no-member
            if model.leased_at + relativedelta(days=+model.lease_duration) >\
                    timezone.now().date():
                raise StillRunning(model.id, model.heartbeat_at)
            model.delete()
        except ObjectDoesNotExist:
            LOGGER_INSTANCES.info('Instance %s does not exist', instance_id)
