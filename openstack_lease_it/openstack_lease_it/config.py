"""
This module manage configuration file.

    - /etc/openstack-lease-it/config.ini
    - $HOME/.lease-it.ini

This module also provide **GLOBAL_CONFIG** variable used to share configuration across module /
django apps.
"""
import ConfigParser
import os

BASE_CONFIG_DIR = '/etc/openstack-lease-it'
"""
To avoid some typo mistake, we use **BASE_CONFIG_DIR** to define the base directory for
configuration files
"""

CONFIG_FILES = (
    BASE_CONFIG_DIR + '/config.ini',
    os.path.expanduser('~') + '/.lease-it.ini',
)
"""
The list of configuration file we will parse to load openstack-lease-it configuration
"""

GLOBAL_CONFIG = {
    # Django parameters
    'DJANGO_DEBUG': 'False',
    'DJANGO_LOGDIR': '/var/log/openstack-lease-it/',
    'DJANGO_LOGLEVEL': 'INFO',
    'DJANGO_SECRET_KEY': 'Must_be_defined',  # Must be defined to allow sphinx to run

    # OpenStack parameters
    'OS_USERNAME': 'admin',
    'OS_TENANT_NAME': 'admin',
    'OS_PASSWORD': 'admin_password',  # Must be defined to allow sphinx to run
    'OS_PROJECT_NAME': 'admin',
    'OS_AUTH_URL': 'https://keystone.example.com',  # Must be defined to allow sphinx to run
    'OS_IDENTITY_API_VERSION': '3',
    'OS_USER_DOMAIN_NAME': 'default',
    'OS_PROJECT_DOMAIN_NAME': 'default',
    'OS_CACERT': None,  # If certificate is signed by a legit CA, we don't need to define it

    # memcached parameter
    'MEMCACHED_HOST': '127.0.0.1',
    'MEMCACHED_PORT': '11211',

    # plugins parameter
    'BACKEND_PLUGIN': 'Openstack',

    # notification parameter
    'NOTIFICATION_DEBUG': 'False',
    'NOTIFICATION_DOMAIN': '',
    'NOTIFICATION_DELETE_CONTENT': BASE_CONFIG_DIR + '/delete-notification.txt',
    'NOTIFICATION_LEASE_CONTENT': BASE_CONFIG_DIR + '/lease-notification.txt'
}
"""
We use the global variable GLOBAL_CONFIG to share openstack-lease-it configuration to all user. Some
value have default value.
"""

DJANGO_OPTIONS = {
    'DJANGO_SECRET_KEY': 'secret_key',
    'DJANGO_DEBUG': 'debug',
    'DJANGO_LOGDIR': 'log_dir',
    'DJANGO_LOGLEVEL': 'log_level'
}
"""
    - **DJANGO_SECRET_KEY**: The secret key used by django (file option: *secret_key*)
    - **DJANGO_DEBUG**: The DEBUG value for django (file option: *debug*)
    - **DJANGO_LOGDIR**: Directory where log file will be write (file option: *log_dir*)
    - **DJANGO_LOGLEVEL**: The log level used for django (file option: *log_level*)

"""

PLUGINS_OPTIONS = {
    'BACKEND_PLUGIN': 'backend'
}
"""
    - **BACKEND_PLUGIN**: Backend we will use (file option: *backend*)
"""

OPENSTACK_OPTIONS = {
    'OS_USERNAME': 'OS_USERNAME',
    'OS_PASSWORD': 'OS_PASSWORD',
    'OS_TENANT_NAME': 'OS_TENANT_NAME',
    'OS_PROJECT_NAME': 'OS_PROJECT_NAME',
    'OS_AUTH_URL': 'OS_AUTH_URL',
    'OS_CACERT': 'OS_CACERT',
    'OS_IDENTITY_API_VERSION': 'OS_IDENTITY_API_VERSION',
    'OS_PROJECT_DOMAIN_NAME': 'OS_PROJECT_DOMAIN_NAME',
    'OS_USER_DOMAIN_NAME': 'OS_USER_DOMAIN_NAME'
}
"""
    - **OS_USERNAME**: Openstack admin username (file option: *OS_USERNAME*)
    - **OS_PASSWORD**: Openstack admin password (file option: *OS_PASSWORD*)
    - **OS_TENANT_NAME**: Openstack admin project name (file option: *OS_TENANT_NAME*)
    - **OS_PROJECT_NAME**: Openstack admin project name (file option: *OS_PROJECT_NAME*)
    - **OS_AUTH_URL**: Cloud keystone URL (file option: *OS_AUTH_URL*)
    - **OS_CACERT**: CA certificate filename (file option: *OS_CACERT*)
    - **OS_IDENTITY_API_VERSION**: Keystone version (file option: *OS_IDENTITY_API_VERSION*)
    - **OS_PROJECT_DOMAIN_NAME**: project domain name (file option: *OS_PROJECT_DOMAIN_NAME*)
    - **OS_USER_DOMAIN_NAME**: user domain name (file option: *OS_USER_DOMAIN_NAME*)

"""

MEMCACHED_OPTIONS = {
    'MEMCACHED_HOST': 'host',
    'MEMCACHED_PORT': 'port'
}
"""
    - **MEMCACHED_HOST**: hostname of memcached server (file option: *host*)
    - **MEMCACHED_PORT**: port of memcached server (file option: *port*)

"""

NOTIFICATION_OPTIONS = {
    'NOTIFICATION_SSL': 'ssl',
    'NOTIFICATION_SMTP': 'smtp',
    'NOTIFICATION_USERNAME': 'username',
    'NOTIFICATION_PASSWORD': 'password',
    'NOTIFICATION_EMAIL_HEADER': 'email_header',
    'NOTIFICATION_SUBJECT': 'subject',
    'NOTIFICATION_LINK': 'link',
    'NOTIFICATION_DEBUG': 'debug',
    'NOTIFICATION_DOMAIN': 'default_domain',
    'NOTIFICATION_DELETE_CONTENT': 'delete_content',
    'NOTIFICATION_LEASE_CONTENT': 'lease_content'
}
"""

    - **NOTIFICATION_SSL**: enable / disable ssl for smtp connection (file option: *ssl*)
    - **NOTIFICATION_SMTP**: hostname of smtp server (file option: *smtp*)
    - **NOTIFICATION_USERNAME**: username for smtp connection (file option: *username*)
    - **NOTIFICATION_PASSWORD**: password for smtp connection (file option: *password*)
    - **NOTIFICATION_EMAIL_HEADER**: email sender (file option: *email_header*)
    - **NOTIFICATION_SUBJECT**: subject of the mail (file option: *subject*)
    - **NOTIFICATION_LINK**: url of lease-it server (file option: *link*)
    - **NOTIFICATION_DEBUG**: enable/disable user notification (file option: *debug*)
    - **NOTIFICATION_DOMAIN**: default domain if email field not match email regexp
      (file option: *default_domain*)
    - **NOTIFICATION_DELETE_CONTENT**: filename for mail content template
      (file option: *delete_content*)
    - **NOTIFICATION_LEASE_CONTENT**: filename for mail content template
      (file option: *lease_content*)

"""

SECTIONS = {
    'django': DJANGO_OPTIONS,
    'openstack': OPENSTACK_OPTIONS,
    'memcached': MEMCACHED_OPTIONS,
    'plugins': PLUGINS_OPTIONS,
    'notification': NOTIFICATION_OPTIONS
}
"""

    - **django**: section [django]
    - **openstack**: section [openstack]
    - **memcached**: section [memcached]
    - **plugins**: section [plugins]
    - **notification**: section [notification]

"""


def load_config_option(config, section):
    """
    This function overwrite the current global_config[name] value
    with option

    :param config: Configuration file we read
    :param section: The section of configuration file we compute
    :return: void
    """
    options = SECTIONS[section]
    for option in options:
        try:
            GLOBAL_CONFIG[option] = config.get(section,
                                               options[option])
        except ConfigParser.NoSectionError:
            pass
        except ConfigParser.NoOptionError:
            pass


def load_config():
    """
    Define default configuration, *NOT* all value have a default

    :return: void
    """
    config = ConfigParser.RawConfigParser()

    for config_file in CONFIG_FILES:
        config.read(config_file)
        for section in SECTIONS:
            load_config_option(config, section)
