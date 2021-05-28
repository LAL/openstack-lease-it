"""
This file tests the instances model with some plausible values.
The database created for the test is destroyed right after.
"""

# pylint: skip-file
import django.core.exceptions
from django.test import TestCase
from lease_it.models import Instances
from lease_it.client.run import instance_spy
from openstack_lease_it.settings import GLOBAL_CONFIG, load_config

# Create your tests here.


class InstancesTest(TestCase):
    def setUp(self):
        """
        Filling the database with plausible values

        :return: void
        """
        Instances.objects.create(id="instance-01", heartbeat_at="2021-08-28", leased_at="2021-05-28", lease_duration=90)
        Instances.objects.create(id="instance-02", heartbeat_at="2020-08-28", leased_at="2020-05-28", lease_duration=90)
        Instances.objects.create(id="instance-03", heartbeat_at="2020-08-28", leased_at="2020-05-28", lease_duration=90)
        Instances.objects.create(id="instance-04", heartbeat_at="2020-08-28", leased_at="2020-05-28", lease_duration=90)
        Instances.objects.create(id="instance-05", heartbeat_at="2020-08-28", leased_at="2020-05-28", lease_duration=90)

    def test_instance_spy(self):
        """
        Testing the instance_spy function

        :return: void
        """

        instance_spy()

        # Only the instance with id "instance-02" should be deleted, as it's not excluded nor leased
        self.assertIsInstance(Instances.objects.get(id="instance-01"),Instances)
        self.assertRaisesMessage(django.core.exceptions.ObjectDoesNotExist, "Instances matching query does not exist.",
                                 Instances.objects.get, id="instance-02")
        self.assertIsInstance(Instances.objects.get(id="instance-03"), Instances)
        self.assertIsInstance(Instances.objects.get(id="instance-04"), Instances)
        self.assertIsInstance(Instances.objects.get(id="instance-05"), Instances)

        load_config()
        GLOBAL_CONFIG['EXCLUDED_USERS_ID'] = []
        instance_spy()
        # Now instance_03 should be deleted, because it no longer benefit from the user exclusion
        self.assertIsInstance(Instances.objects.get(id="instance-01"), Instances)
        self.assertRaisesMessage(django.core.exceptions.ObjectDoesNotExist, "Instances matching query does not exist.",
                                 Instances.objects.get, id="instance-03")
        self.assertIsInstance(Instances.objects.get(id="instance-04"), Instances)
        self.assertIsInstance(Instances.objects.get(id="instance-05"), Instances)

        load_config()
        GLOBAL_CONFIG['EXCLUDED_PROJECTS'] = ['LAL']
        GLOBAL_CONFIG['EXCLUDED_USERS_ID'] = []
        instance_spy()
        # Now that all the exclusions are disabled, instance 04 and 05 should be deleted
        self.assertIsInstance(Instances.objects.get(id="instance-01"), Instances)
        self.assertRaisesMessage(django.core.exceptions.ObjectDoesNotExist, "Instances matching query does not exist.",
                                 Instances.objects.get, id="instance-04")
        self.assertRaisesMessage(django.core.exceptions.ObjectDoesNotExist, "Instances matching query does not exist.",
                                 Instances.objects.get, id="instance-05")
