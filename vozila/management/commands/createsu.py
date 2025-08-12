from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='user').exists(): #popravi username
            User.objects.create_superuser(
                username='user', #popravi username
                email='mail', #popravi email
                password='geslo' #popravi geslo
            )
            self.stdout.write(self.style.SUCCESS('Superuser created'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))
