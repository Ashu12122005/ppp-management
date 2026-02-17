# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # home -> dashboard
    path("", views.dashboard, name="dashboard"),

    # auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),



    # students
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.add_student, name="student_add"),
    path("students/<int:pk>/edit/", views.student_edit, name="student_edit"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("students/<int:pk>/profile/", views.student_profile, name="student_profile"),
    path("students/upload/", views.upload_students_excel, name="student_upload"),
    path("students/export/", views.export_students, name="students_export"),

    # attendance
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/add/", views.attendance_add, name="attendance_add"),
    path("attendance/export/", views.export_attendance, name="attendance_export"),
    path("attendance/upload/", views.upload_attendance_excel, name="attendance_upload"),


    # fees
    path("fees/", views.fees_list, name="fees_list"),
    path("fees/add/", views.fees_add, name="fees_add"),
    path("fees/export/", views.export_fees, name="fees_export"),
    path("fees/upload/", views.upload_fees_excel, name="fees_upload"),


    # ppp
    path("ppp/", views.ppp_list, name="ppp_list"),
    path("ppp/add/", views.ppp_add, name="ppp_add"),
    path("ppp/export/", views.export_ppp, name="ppp_export"),

    # notices
    path("notices/", views.notice_list, name="notices"),
    path("notices/add/", views.notice_add, name="notice_add"),
    path("notices/<int:pk>/delete/", views.notice_delete, name="notice_delete"),
]
