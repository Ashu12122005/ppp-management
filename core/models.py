# core/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Student(models.Model):
    # Primary
    slno = models.PositiveIntegerField(null=True, blank=True)
    admission_name = models.CharField("Name of Student", max_length=255)
    date_of_joining = models.DateField("Date of Joining", null=True, blank=True)
    class_roll_no = models.CharField("Class Roll-No", max_length=50, blank=True)
    exam_roll_no = models.CharField("Exam Roll No", max_length=50, blank=True, unique=True)

    # department
    department = models.CharField(
        "Department",
        max_length=20,
        choices=[("BCA", "BCA"), ("BBA", "BBA"), ("MPMIR", "MPMIR")],
        default="BCA",
    )

    # Personal
    mobile = models.CharField("Mobile No", max_length=20, blank=True)

    # IMPORTANT FIX — allow NULL + UNIQUE
    email = models.EmailField("Email", blank=True, null=True, unique=True)

    dob = models.DateField("DOB", null=True, blank=True)
    category = models.CharField("Category", max_length=100, blank=True)
    aadhaar = models.CharField("Aadhaar No", max_length=30, blank=True)

    # Addresses
    present_address = models.TextField("Present Address", blank=True)
    permanent_address = models.TextField("Permanent Address", blank=True)

    # +2 / Intermediate
    inter_stream = models.CharField("+2 Stream", max_length=150, blank=True)
    inter_percentage = models.DecimalField("+2 % / CGPA", max_digits=6, decimal_places=3, null=True, blank=True)
    inter_regd_no = models.CharField("+2 Regd No", max_length=80, blank=True)
    inter_college = models.CharField("+2 College Name", max_length=255, blank=True)

    # Graduation
    grad_stream = models.CharField("Graduation Stream", max_length=150, blank=True)
    grad_percentage = models.DecimalField("Graduation % / CGPA", max_digits=6, decimal_places=3, null=True, blank=True)
    grad_regd_no = models.CharField("Graduation Regd No", max_length=80, blank=True)
    grad_college = models.CharField("Graduation College Name", max_length=255, blank=True)

    # Photo & user link
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='student_profile'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['class_roll_no', 'admission_name']
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"{self.admission_name} ({self.class_roll_no or self.exam_roll_no or '—'})"


class PPPEntry(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ONGOING = 'ongoing'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ONGOING, 'Ongoing'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='ppp_entries')
    date = models.DateField(default=timezone.now)
    activity = models.TextField()
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.student.admission_name} - {self.date} ({self.status})"


class Attendance(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_ABSENT = 'absent'
    STATUS_LEAVE = 'leave'

    STATUS_CHOICES = [
        (STATUS_PRESENT, 'Present'),
        (STATUS_ABSENT, 'Absent'),
        (STATUS_LEAVE, 'Leave'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.CharField(max_length=255, blank=True)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', '-marked_at']

    def __str__(self):
        return f"{self.student.admission_name} - {self.date} - {self.status}"


class FeePayment(models.Model):
    MODE_CASH = 'cash'
    MODE_UPI = 'upi'
    MODE_BANK = 'bank'

    PAYMENT_MODES = [
        (MODE_CASH, 'Cash'),
        (MODE_UPI, 'UPI'),
        (MODE_BANK, 'Bank Transfer'),
    ]

    STATUS_PAID = 'paid'
    STATUS_PARTIAL = 'partial'
    STATUS_PENDING = 'pending'

    STATUS_CHOICES = [
        (STATUS_PAID, 'Paid'),
        (STATUS_PARTIAL, 'Partial'),
        (STATUS_PENDING, 'Pending'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PAID)
    remarks = models.CharField(max_length=255, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.student.admission_name} - {self.amount} ({self.status})"


class Notice(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
