import sys
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission

from esmond.api.models import UserIpAddress

class Command(BaseCommand):
    help = 'Associate IP subnet(s) with a user account'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('ip', nargs='+')

    def handle(self, *args, **options):
        user = options['username']

        u = None

        try:
            u = User.objects.get(username=user)
            print('User {0} exists'.format(user))
        except User.DoesNotExist:
            print('User {0} does not exist - creating'.format(user))
            u = User(username=user, is_staff=True)
            u.save()

        print('Setting metadata POST permissions.')
        for model_name in ['psmetadata', 'pspointtopointsubject', 'pseventtypes', 'psmetadataparameters', 'psnetworkelementsubject']:
            for perm_name in ['add', 'change', 'delete']:
                perm = Permission.objects.get(codename='{0}_{1}'.format(perm_name, model_name))
                print(perm)
                u.user_permissions.add(perm)
        
        print('Setting timeseries permissions.')
        for resource in ['timeseries']:
            for perm_name in ['view', 'add', 'change', 'delete']:
                perm = Permission.objects.get(
                    codename="esmond_api.{0}_{1}".format(perm_name, resource))
                u.user_permissions.add(perm)
                
        u.save()
        
        for ip_addr in options['ip']:
            try:
                userip = UserIpAddress.objects.get(ip=ip_addr)
                print('IP {0} already assigned to {1}, skipping creation'.format(userip.ip, userip.user))
            except UserIpAddress.DoesNotExist:
                print('Creating entry for IP {0} belonging to {1}'.format(ip_addr, user))
                userip = UserIpAddress(ip=ip_addr, user=u)
                userip.save()
