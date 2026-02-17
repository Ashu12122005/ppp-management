from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()


def login_user(request):
    """
    Allows login using:
    - username
    - email
    Redirects:
    - Teacher → core:dashboard
    - Student → core:student_dashboard
    """
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        # Try username login first
        user = authenticate(request, username=identifier, password=password)

        # If not found and identifier is email → login via email
        if user is None and "@" in identifier:
            found = User.objects.filter(email__iexact=identifier).first()
            if found:
                user = authenticate(request, username=found.username, password=password)

        if user:
            login(request, user)

            # Teacher
            if user.is_staff:
                return redirect('core:dashboard')

            # Student
            return redirect('core:student_dashboard')

        # Login Failed
        messages.error(request, "Invalid username or password")

    return render(request, 'core/login.html')


def logout_user(request):
    """
    Logs out user and sends back to login page.
    """
    logout(request)
    return redirect('login')
