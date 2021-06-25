#  -*- coding: utf-8 -*-
"""
instance-spy should be put on a crontab to check running instance, notify user if lease is close
to expire and destroy instance when lease is over
"""
import os
from collections import defaultdict


os.environ['DJANGO_SETTINGS_MODULE'] = "openstack_lease_it.settings"

from lease_it.notification.MailNotification import MailNotification
from lease_it.datastore.ModelAccess import InstancesAccess


from lease_it import backend  # pylint: disable=wrong-import-position
from openstack_lease_it.settings import GLOBAL_CONFIG  # pylint: disable=wrong-import-position

# We load backend specify by configuration file
BACKEND_PLUGIN = getattr(backend, "{0}Connection".format(GLOBAL_CONFIG['BACKEND_PLUGIN']))
BACKEND = BACKEND_PLUGIN()  # pylint: disable=not-callable


def instance_spy():
    """
    Function used to run the script

    :return: void
    """
    instances = BACKEND.spy_instances()
    users = BACKEND.users()
    notification = dict()
    for notification_type in "delete", "notify":
        notification[notification_type] = defaultdict(list)
        for instance in instances[notification_type]:
            notification[notification_type][instance['user_id']].append(instance)
            if notification_type == "delete":
                InstancesAccess.delete(instance['id'])
    BACKEND.delete(instances['delete'])
    notify = MailNotification(users)
    notify.send(notification)


def admin_cli():
    """
    Admin Command Line Interface

    :return: void
    """
    return True
