"""
Executing this file updates the test_models.json with the data provided by test_models_setup.json.
This simplifies the instances' management during the tests.
"""
import json

# Basic database dictionary
test_models_base = [
  {
    "model": "contenttypes.contenttype",
    "fields": {
      "app_label": "openstack_auth",
      "model": "user"},
    "pk": 1
  },
  {
    "model": "contenttypes.contenttype",
    "fields": {
      "app_label": "admin", "model": "logentry"
    },
    "pk": 2
  },
  {
    "model": "contenttypes.contenttype",
    "fields": {
      "app_label": "auth", "model": "permission"
    },
    "pk": 3
  },
  {
    "model": "contenttypes.contenttype",
    "fields": {
      "app_label": "auth", "model": "group"
    },
    "pk": 4
  },
  {
    "model": "contenttypes.contenttype",
    "fields": {
      "app_label": "auth", "model": "user"
    },
    "pk": 5
  },
  {
    "model": "contenttypes.contenttype",
    "fields":
    {
      "app_label": "contenttypes",
      "model": "contenttype"
    },
    "pk": 6
  },
  {
    "model": "contenttypes.contenttype",
    "fields":
    {
      "app_label": "sessions", "model": "session"
    },
    "pk": 7
  },
  {
    "model": "contenttypes.contenttype",
    "fields":
    {
      "app_label": "lease_it",
      "model": "instances"
    },
    "pk": 8
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add user",
      "content_type": 1,
      "codename": "add_user"
    },
    "pk": 1
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change user",
      "content_type": 1,
      "codename": "change_user"
    },
    "pk": 2
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete user",
      "content_type": 1,
      "codename": "delete_user"
    },
    "pk": 3
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add log entry",
      "content_type": 2,
      "codename": "add_logentry"
    },
    "pk": 4
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change log entry",
      "content_type": 2,
      "codename": "change_logentry"
    },
    "pk": 5
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete log entry",
      "content_type": 2,
      "codename": "delete_logentry"
    },
    "pk": 6
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add permission",
      "content_type": 3,
      "codename": "add_permission"
    },
    "pk": 7
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change permission",
      "content_type": 3,
      "codename": "change_permission"
    },
    "pk": 8
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete permission",
      "content_type": 3,
      "codename": "delete_permission"
    },
    "pk": 9
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add group",
      "content_type": 4,
      "codename": "add_group"
    },
    "pk": 10
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change group",
      "content_type": 4,
      "codename": "change_group"
    },
    "pk": 11
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete group",
      "content_type": 4,
      "codename": "delete_group"
    },
    "pk": 12
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add user",
      "content_type": 5,
      "codename": "add_user"
    },
    "pk": 13
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change user",
      "content_type": 5,
      "codename": "change_user"
    },
    "pk": 14
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete user",
      "content_type": 5,
      "codename": "delete_user"
    },
    "pk": 15
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add content type",
      "content_type": 6,
      "codename": "add_contenttype"
    },
    "pk": 16
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change content type",
      "content_type": 6,
      "codename": "change_contenttype"
    },
    "pk": 17
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete content type",
      "content_type": 6,
      "codename": "delete_contenttype"
    },
    "pk": 18
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add session",
      "content_type": 7,
      "codename": "add_session"
    },
    "pk": 19
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change session",
      "content_type": 7,
      "codename": "change_session"
    },
    "pk": 20
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete session",
      "content_type": 7,
      "codename": "delete_session"
    },
    "pk": 21
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can add instances",
      "content_type": 8,
      "codename": "add_instances"
    },
    "pk": 22
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can change instances",
      "content_type": 8,
      "codename": "change_instances"
    },
    "pk": 23
  },
  {
    "model": "auth.permission",
    "fields":
    {
      "name": "Can delete instances",
      "content_type": 8,
      "codename": "delete_instances"
    },
    "pk": 24
  },
  {
    "model": "auth.user",
    "fields":
    {
      "password": "pbkdf2_sha256$20000$f0kZKtEf9D78$XvUaXte8o9kP5Nu5stefJUXCWltiQRFl7iZD1mB5onI=",
      "last_login": "2021-05-26T11:28:57.063Z",
      "is_superuser": True,
      "username": "yann",
      "first_name": "",
      "last_name": "",
      "email": "test@test.fr",
      "is_staff": True,
      "is_active": True,
      "date_joined": "2021-05-25T10:37:21.225Z",
      "groups": [],
      "user_permissions": []
    },
    "pk": 1
  }
]

# Adding the instances to the basic database dictionary
test_models_setup_file = open("./lease_it/fixtures/test_models_setup.json")
test_models = open("./lease_it/fixtures/test_models.json", "w")
test_models_setup = json.loads(test_models_setup_file.read())

for test_model in test_models_setup:
    test_models_base.append(test_model)

json.dump(test_models_base, test_models)

