"""
Mail notification system
"""

import smtplib
import ast
import re
from email.mime.text import MIMEText
from openstack_lease_it.settings import GLOBAL_CONFIG, EMAIL_REGEXP, LOGGER_NOTIFICATION


class MailNotification(object):  # pylint: disable=too-few-public-methods
    """
    A class to abstract e-mail notification
    """
    def __init__(self, users):
        """
        Not implemented yet
        """
        self.users = users
        try:
            self.smtp = smtplib.SMTP_SSL(GLOBAL_CONFIG['NOTIFICATION_SMTP'])
            self.smtp.login(GLOBAL_CONFIG['NOTIFICATION_USERNAME'],
                            GLOBAL_CONFIG['NOTIFICATION_PASSWORD'])
            delete_content = open(GLOBAL_CONFIG['NOTIFICATION_DELETE_CONTENT'], 'r')
            lease_content = open(GLOBAL_CONFIG['NOTIFICATION_LEASE_CONTENT'], 'r')
            self.notification = {
                'delete': delete_content.read(),
                'notify': lease_content.read()
            }
        except:
            self.notification = {
                'delete': open("/dev/null").read(),
                'notify': open("/dev/null").read()
            }

            pass

    @staticmethod
    def format_user_instances(user):
        """
        Create a string w/ the list of instance formatted to be mailed
        :param user: user we currently notify
        :return: string
        """
        text = ""
        for instance in user:
            text += "  - {name} started {created_at} and expire {lease_end} \n".format(**instance)
        return text

    def format_mail(self, user, notification_type, instances):
        """
        Format the mail content
        :param user: user we currently notify
        :param notification_type: notification type (delete or notify)
        :param instances: list of instance for the user
        :return: string
        """
        try:
            user_name = self.users[user]['name']
        except KeyError:
            user_name = 'Unknown User'
            LOGGER_NOTIFICATION.info("User %s as not be found", user)
        core_text = self.notification[notification_type]
        instances_text = self.format_user_instances(instances)
        try:
            return core_text.format(username=user_name,
                                link=GLOBAL_CONFIG['NOTIFICATION_LINK'],
                                instances=instances_text)
        except KeyError:
            LOGGER_NOTIFICATION.info("Notification link not found")
            pass

    def send(self, notifications):
        """
        The all notifications give in parameter, each notifications type (delete or notify) are
        a dictionnary of users with a list of instance to notify per user
        :param notifications: dict of users and instances
        :return: void
        """
        for notification in notifications:
            for user in notifications[notification]:
                mail_text = self.format_mail(user, notification, notifications[notification][user])
                try:
                    mail = MIMEText(mail_text)
                except AttributeError:
                    LOGGER_NOTIFICATION.info("Mail text None type")
                    mail = dict()
                try:
                    mail['Subject'] = GLOBAL_CONFIG['NOTIFICATION_SUBJECT']
                except KeyError:
                    LOGGER_NOTIFICATION.info("Email subject not found")
                    mail['Subject'] = "/"
                try:
                    mail['From'] = GLOBAL_CONFIG['NOTIFICATION_EMAIL_HEADER']
                except KeyError:
                    LOGGER_NOTIFICATION.info("Email header not found")
                    mail['From'] = "/"
                try:
                    email = self.users[user]['email']
                    if not re.match(EMAIL_REGEXP, email) and GLOBAL_CONFIG['NOTIFICATION_DOMAIN'] != "":
                        LOGGER_NOTIFICATION.info("email %s not match a email format"
                                                 " (name@domain.com). Add @%s",
                                                 email, GLOBAL_CONFIG['NOTIFICATION_DOMAIN'])
                        email = "{0}@{1}".format(email, GLOBAL_CONFIG['NOTIFICATION_DOMAIN'])
                    mail['To'] = email
                    if ast.literal_eval(GLOBAL_CONFIG['NOTIFICATION_DEBUG']):
                        LOGGER_NOTIFICATION.info("Only notify administrator instead of %s", email)
                        recipient = [GLOBAL_CONFIG['NOTIFICATION_EMAIL_HEADER']]
                    else:
                        recipient = [GLOBAL_CONFIG['NOTIFICATION_EMAIL_HEADER'],
                                     email]
                except KeyError:
                    LOGGER_NOTIFICATION.info("email field of %s as not be found", user)
                    try:
                        mail['To'] = GLOBAL_CONFIG['NOTIFICATION_EMAIL_HEADER']
                        recipient = [GLOBAL_CONFIG['NOTIFICATION_EMAIL_HEADER']]
                    except KeyError:
                        LOGGER_NOTIFICATION.info("Email header not found")
                        recipient = "/"
                LOGGER_NOTIFICATION.info("Notification %s to %s", notification, ''.join(recipient))
                try:
                    self.smtp.sendmail(GLOBAL_CONFIG['NOTIFICATION_EMAIL_HEADER'],
                                   recipient,
                                   mail.as_string())
                except AttributeError:
                    LOGGER_NOTIFICATION.info("Smtp not found")
