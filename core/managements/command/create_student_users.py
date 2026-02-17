# core/management/commands/create_student_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Student
import random, string

User = get_user_model()

def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))

class Command(BaseCommand):
    help = 'Create Django user accounts for existing students without a user and print credentials.'

    def handle(self, *args, **options):
        students = Student.objects.filter(user__isnull=True)
        created = 0
        for s in students:
            base_username = (s.admission_name or 'student').split()[0].lower()
            candidate = f"{base_username}{s.exam_roll_no or s.class_roll_no or s.pk}"

            username = candidate
            i = 0
            while User.objects.filter(username=username).exists():
                i += 1
                username = f"{candidate}{i}"

            password = generate_password(10)
            user = User.objects.create_user(username=username, password=password, email=(s.email or ''))
            s.user = user
            s.save(update_fields=['user'])
            created += 1
            self.stdout.write(f"Created user for {s.admission_name}: username={username} password={password}")

        self.stdout.write(self.style.SUCCESS(f"Created {created} users."))
