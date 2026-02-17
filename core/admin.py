# core/admin.py
from django.contrib import admin
from .models import Student, Attendance, FeePayment, PPPEntry, Notice


# =============================
# STUDENT ADMIN
# =============================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "admission_name",
        "class_roll_no",
        "exam_roll_no",
        "department",
        "email",
        "mobile",
    )
    search_fields = (
        "admission_name",
        "class_roll_no",
        "exam_roll_no",
        "email",
        "mobile",
        "aadhaar",
    )
    # gender removed until you add it in model
    list_filter = ("department", "category")
    ordering = ("class_roll_no",)

    fieldsets = (
        ("Basic Information", {
            "fields": ("slno", "admission_name", "department", "photo")
        }),
        ("Joining / Roll Numbers", {
            "fields": ("date_of_joining", "class_roll_no", "exam_roll_no")
        }),
        ("Personal Details", {
            # remove gender until added to model
            "fields": ("category", "dob", "aadhaar")
        }),
        ("Parents", {
            "fields": ("father_name", "mother_name")
        }),
        ("Contact Information", {
            "fields": ("mobile", "email")
        }),
        ("Addresses", {
            "fields": ("present_address", "permanent_address")
        }),
        ("10th Details", {
            "fields": (
                "school_10", "board_10", "year_10",
                "percentage_10",
            )
        }),
        ("12th / Intermediate Details", {
            "fields": (
                "school_12", "board_12", "year_12",
                "stream_12", "percentage_12",
                "regd_no_12", "clc_no",
            )
        }),
        ("Graduation Details", {
            "fields": (
                "grad_stream", "grad_percentage",
                "grad_regd_no", "grad_college"
            )
        }),
        ("System Fields", {
            "fields": ("user", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ("created_at", "updated_at")


# =============================
# ATTENDANCE ADMIN
# =============================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "marked_by")
    list_filter = ("status", "date")
    search_fields = ("student__admission_name", "student__class_roll_no")
    ordering = ("-date",)


# =============================
# FEES ADMIN
# =============================
@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "student", "date",
        "amount", "payment_mode",
        "status", "received_by"
    )
    search_fields = ("student__admission_name", "student__class_roll_no")
    list_filter = ("payment_mode", "status")
    ordering = ("-date",)


# =============================
# PPP ENTRY ADMIN
# =============================
@admin.register(PPPEntry)
class PPPEntryAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "status", "created_by")
    search_fields = ("student__admission_name", "student__class_roll_no")
    list_filter = ("status", "date")
    ordering = ("-date",)


# =============================
# NOTICE ADMIN
# =============================
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at", "valid_from", "valid_until")
    search_fields = ("title", "message")
    ordering = ("-created_at",)   # FIXED

