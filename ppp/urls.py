# project/urls.py (replace with your project's main urls.py or merge)
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import view_auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('login/', view_auth.login_user, name='login'),
    path('logout/', view_auth.logout_user, name='logout'),
    path(
    "accounts/password_reset/",
    auth_views.PasswordResetView.as_view(),
    name="password_reset"
),
path(
    "accounts/password_reset/done/",
    auth_views.PasswordResetDoneView.as_view(),
    name="password_reset_done"
),
path(
    "accounts/reset/<uidb64>/<token>/",
    auth_views.PasswordResetConfirmView.as_view(),
    name="password_reset_confirm"
),
path(
    "accounts/reset/done/",
    auth_views.PasswordResetCompleteView.as_view(),
    name="password_reset_complete"
),

]
