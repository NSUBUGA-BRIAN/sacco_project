from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username=os.environ.get('ADMIN_USER', 'admin'),
                password=os.environ.get('ADMIN_PASS', 'admin123'),
                email=''
            )
