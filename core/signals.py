# core/signals.py
import random, string
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()

def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))

@receiver(post_save, sender=Student)
def create_user_for_student(sender, instance, created, **kwargs):
    if created and instance.user is None:
        # build base username
        base = (instance.admission_name or 'student').split()[0].lower()
        candidate = f"{base}{instance.exam_roll_no or instance.class_roll_no or instance.pk}"
        username = candidate
        i = 0
        while User.objects.filter(username=username).exists():
            i += 1
            username = f"{candidate}{i}"

        password = generate_password(10)
        user = User.objects.create_user(username=username, password=password, email=(instance.email or ''))
        instance.user = user
        instance.save(update_fields=['user'])

        # IMPORTANT: For development we print to console (don’t do in prod)
        print(f"[Student->User] created user for {instance.admission_name}: {username} / {password}")
        # In production, consider sending email to student with credentials