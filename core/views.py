
import io
import json
import tempfile
import calendar
import datetime
import pandas as pd
from numbers_parser import Document
import json


from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.http import HttpResponse

from .models import Student, Attendance, FeePayment, PPPEntry, Notice
from .forms import StudentForm, AttendanceForm, PPPEntryForm, FeePaymentForm

User = get_user_model()


# -------------------------
# Helpers & decorators
# -------------------------
def teacher_required(view_func):
    """Decorator: only staff users (teachers)"""
    return user_passes_test(lambda u: u.is_authenticated and u.is_staff, login_url="core:login")(view_func)


# -------------------------
# AUTH
# -------------------------
def login_view(request):
    next_url = request.GET.get("next")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Only staff can use next=/
            if next_url and user.is_staff:
                return redirect(next_url)

            # Role-based redirect
            if user.is_staff:
                return redirect("core:dashboard")
            else:
                return redirect("core:student_dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "core/login.html")




def logout_view(request):
    logout(request)
    return redirect("core:login")


# -------------------------
# Dashboard (teacher) — charts + cards
# -------------------------
@teacher_required
def dashboard(request):
    # basic cards
    total_students = Student.objects.count()
    total_ppp = PPPEntry.objects.count()
    total_fees = FeePayment.objects.aggregate(total=Sum("amount"))["total"] or 0

    # attendance summary (today)
    today = timezone.now().date()
    today_att = Attendance.objects.filter(date=today)
    present_count = today_att.filter(status="present").count()
    absent_count = today_att.filter(status="absent").count()
    leave_count = today_att.filter(status="leave").count()

    # latest students & notices
    latest_students = Student.objects.order_by("-id")[:5]
    latest_notices = Notice.objects.order_by("-created_at")[:5]

    # PPP status counts (for bar chart)
    ppp_stats_qs = PPPEntry.objects.values("status").annotate(count=Count("id"))
    ppp_status_map = {"pending": 0, "ongoing": 0, "completed": 0}
    for item in ppp_stats_qs:
        ppp_status_map[item["status"]] = item["count"]

    ppp_labels = ["Pending", "Ongoing", "Completed"]
    ppp_values = [ppp_status_map["pending"], ppp_status_map["ongoing"], ppp_status_map["completed"]]

    # Fees timeline (last 6 months) — line chart
    today_dt = timezone.now()
    months = []
    fees_values = []
    for i in range(5, -1, -1):  # 5 months ago -> this month
        month_dt = (today_dt - datetime.timedelta(days=today_dt.day - 1)) - datetime.timedelta(days=30 * i)
        year = month_dt.year
        month = month_dt.month
        label = f"{calendar.month_abbr[month]} {str(year)[-2:]}"
        months.append(label)
        month_start = datetime.date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        month_end = datetime.date(year, month, last_day)
        total = FeePayment.objects.filter(date__range=(month_start, month_end)).aggregate(total=Sum("amount"))["total"] or 0
        fees_values.append(float(total))

    # Attendance pie data (today)
    attendance_labels = ["Present", "Absent", "Leave"]
    attendance_values = [present_count, absent_count, leave_count]

    context = {
        "total_students": total_students,
        "total_ppp": total_ppp,
        "total_fees": total_fees,
        "present_count": present_count,
        "absent_count": absent_count,
        "leave_count": leave_count,
        "latest_students": latest_students,
        "latest_notices": latest_notices,
        # chart payloads (json)
        "ppp_labels_json": json.dumps(ppp_labels),
        "ppp_values_json": json.dumps(ppp_values),
        "fees_months_json": json.dumps(months),
        "fees_values_json": json.dumps(fees_values),
        "attendance_labels_json": json.dumps(attendance_labels),
        "attendance_values_json": json.dumps(attendance_values),
    }
    return render(request, "core/dashboard.html", context)


# -------------------------
# Student dashboard (for student users)
# -------------------------
@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect("core:dashboard")

    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        messages.error(request, "No student profile found.")
        return redirect("core:login")

    total_present = student.attendance_records.filter(status="present").count()
    total_absent = student.attendance_records.filter(status="absent").count()
    total_leave = student.attendance_records.filter(status="leave").count()
    total_paid = student.fees.aggregate(total=Sum("amount"))["total"] or 0
    recent_fees = student.fees.order_by("-date")[:6]
    ppp_entries = student.ppp_entries.order_by("-date")[:6]
    notices = Notice.objects.order_by("-created_at")[:5]

    return render(request, "core/student_dashboard.html", {
        "student": student,
        "total_present": total_present,
        "total_absent": total_absent,
        "total_leave": total_leave,
        "total_paid": total_paid,
        "recent_fees": recent_fees,
        "ppp_entries": ppp_entries,
        "notices": notices,
    })


# -------------------------
# Students CRUD (teacher)
# -------------------------
@teacher_required
def student_list(request):
    students = Student.objects.all().order_by("class_roll_no")
    return render(request, "core/student_list.html", {"students": students})


@teacher_required
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            # create a user account if email present
            if student.email and not student.user:
                base_username = student.email.strip()
                username = base_username
                count = 1
                while User.objects.filter(username=username).exists():
                    parts = base_username.split("@")
                    username = f"{parts[0]}{count}@{parts[1]}"
                    count += 1
                user = User.objects.create_user(username=username, email=student.email, password="student@123", first_name=student.admission_name)
                student.user = user
                messages.success(request, f"Student user created: {username}")
            student.save()
            messages.success(request, "Student added successfully.")
            return redirect("core:student_list")
    else:
        form = StudentForm()
    return render(request, "core/add_student.html", {"form": form})


@teacher_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated.")
            return redirect("core:student_list")
    else:
        form = StudentForm(instance=student)
    return render(request, "core/add_student.html", {"form": form, "student": student})


@teacher_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, "Student deleted.")
    return redirect("core:student_list")


@login_required
def student_profile(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "core/student_profile.html", {
        "student": student,
        "attendance": student.attendance_records.all(),
        "fees": student.fees.all(),
        "ppp": student.ppp_entries.all(),
    })


# -------------------------
# Import Students (Excel / CSV / .numbers)
# -------------------------
def convert_numbers_to_df(uploaded_file):
    """Convert Apple Numbers file to pandas DataFrame (numbers_parser)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".numbers") as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    doc = Document(tmp_path)
    sheet = doc.sheets()[0]
    table = sheet.tables()[0]
    data = []
    for row in table.rows():
        data.append([cell.value for cell in row])
    headers = data[0]
    rows = data[1:]
    return pd.DataFrame(rows, columns=headers)


@teacher_required
def upload_students_excel(request):
    summary = {"imported": 0, "duplicates": 0, "errors": 0, "error_rows": []}

    if request.method == "POST":
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            messages.error(request, "No file uploaded.")
            return redirect("core:student_upload")

        # -------- READ FILE --------
        try:
            fname = excel_file.name.lower()

            # Your Excel has header at row index 4
            if fname.endswith(".xlsx") or fname.endswith(".xls"):
                df = pd.read_excel(excel_file, header=4)

            elif fname.endswith(".csv"):
                df = pd.read_csv(excel_file)

            elif fname.endswith(".numbers"):
                df = convert_numbers_to_df(excel_file)

            else:
                messages.error(request, "Allowed formats: .xlsx, .csv, .numbers")
                return redirect("core:student_upload")

        except Exception as e:
            messages.error(request, f"Error reading file: {e}")
            return redirect("core:student_upload")

        # -------- COLUMN NORMALIZER --------
        def normalize(col):
            c = str(col).strip().lower().replace(" ", "").replace(".", "").replace("_", "")

            if c.startswith("sl"):
                return "slno"

            if "name" in c and "student" in c:
                return "admission_name"

            if "doj" in c or "dateofjoining" in c:
                return "date_of_joining"

            if "classrollno" in c or "classroll" in c:
                return "class_roll_no"

            if "examrollno" in c or "examroll" in c:
                return "exam_roll_no"

            if "email" in c:
                return "email"

            if "mobile" in c or "phone" in c:
                return "mobile"

            if "dept" in c or "department" in c:
                return "department"

            return None  # ignore everything else

        # Apply normalizer
        df.columns = [normalize(c) for c in df.columns]
        df = df[[c for c in df.columns if c]]  # remove None columns

        # -------- REQUIRED FIELDS --------
        required = ["admission_name", "class_roll_no", "exam_roll_no"]
        missing = [c for c in required if c not in df.columns]

        if missing:
            messages.error(request, f"Missing required columns: {', '.join(missing)}")
            return redirect("core:student_upload")

        # -------- PROCESS EACH ROW --------
        for index, row in df.iterrows():
            try:
                exam_roll = str(row.get("exam_roll_no", "")).strip()
                if not exam_roll:
                    summary["errors"] += 1
                    summary["error_rows"].append(f"Row {index+2}: Missing Exam Roll No")
                    continue

                # RE-IMPORT PROTECTION (skip existing student)
                if Student.objects.filter(exam_roll_no=exam_roll).exists():
                    summary["duplicates"] += 1
                    summary["error_rows"].append(
                        f"Row {index+2}: Student with Exam Roll No '{exam_roll}' already exists"
                    )
                    continue

                

                # -------- FIX DATE FORMAT --------
                date_raw = row.get("date_of_joining")
                date_val = None

                if pd.notna(date_raw):
                    try:
                        date_val = pd.to_datetime(date_raw, dayfirst=True).date()
                    except:
                        summary["errors"] += 1
                        summary["error_rows"].append(
                            f"Row {index+2}: Invalid date '{date_raw}'"
                        )
                        continue

                # -------- FIX EMAIL (empty → None) --------
                email_raw = row.get("email")
                email_clean = str(email_raw).strip() if email_raw is not None else None
                email_clean = (
                    email_clean if email_clean not in ["", "nan", "None", None] else None
                )

                # -------- CREATE STUDENT --------
                student = Student.objects.create(
                    slno=row.get("slno"),
                    admission_name=row.get("admission_name"),
                    class_roll_no=row.get("class_roll_no"),
                    exam_roll_no=exam_roll,
                    date_of_joining=date_val,
                    email=email_clean,
                    mobile=str(row.get("mobile", "")).strip(),
                    department=row.get("department", "BCA"),
                )

                # -------- CREATE USER ACCOUNT (only if email exists) --------
                if email_clean:
                    base = email_clean
                    username = base
                    count = 1

                    while User.objects.filter(username=username).exists():
                        parts = base.split("@")
                        username = f"{parts[0]}{count}@{parts[1]}"
                        count += 1

                    user = User.objects.create_user(
                    username=username,
                    email=email_clean,
                    password="student@123",  # student will set password themselves
                    first_name=student.admission_name
                )


                    student.user = user
                    student.save()

                summary["imported"] += 1

            except Exception as e:
                summary["errors"] += 1
                summary["error_rows"].append(f"Row {index+2}: {e}")

    return render(request, "core/upload_students.html", {"summary": summary})



# -------------------------
# EXPORT helpers & views
# -------------------------
def _df_to_http_response(df, filename, fmt="xlsx"):
    if fmt == "csv":
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        resp.write(df.to_csv(index=False))
        return resp

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    resp = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="{filename}.xlsx"'
    return resp


@teacher_required
def export_students(request):
    qs = Student.objects.all().order_by("class_roll_no")
    data = [{
        "slno": s.slno,
        "admission_name": s.admission_name,
        "department": s.department,
        "class_roll_no": s.class_roll_no,
        "exam_roll_no": s.exam_roll_no,
        "email": s.email,
        "mobile": s.mobile,
    } for s in qs]
    df = pd.DataFrame(data)
    fmt = request.GET.get("fmt", "xlsx")
    return _df_to_http_response(df, "students_export", fmt)


@teacher_required
def export_attendance(request):
    qs = Attendance.objects.select_related("student").all().order_by("-date")
    data = [{
        "date": a.date,
        "student": a.student.admission_name if a.student else "",
        "roll": a.student.class_roll_no if a.student else "",
        "status": a.status,
        "remarks": a.remarks,
    } for a in qs]
    df = pd.DataFrame(data)
    fmt = request.GET.get("fmt", "xlsx")
    return _df_to_http_response(df, "attendance_export", fmt)


@teacher_required
def export_fees(request):
    qs = FeePayment.objects.select_related("student").all().order_by("-date")
    data = [{
        "date": f.date,
        "student": f.student.admission_name if f.student else "",
        "roll": f.student.class_roll_no if f.student else "",
        "amount": f.amount,
        "mode": f.payment_mode,
        "status": f.status,
    } for f in qs]
    df = pd.DataFrame(data)
    fmt = request.GET.get("fmt", "xlsx")
    return _df_to_http_response(df, "fees_export", fmt)


@teacher_required
def export_ppp(request):
    qs = PPPEntry.objects.select_related("student").all().order_by("-date")
    data = [{
        "date": p.date,
        "student": p.student.admission_name if p.student else "",
        "activity": p.activity,
        "status": p.status,
        "created_by": p.created_by.username if p.created_by else "",
    } for p in qs]
    df = pd.DataFrame(data)
    fmt = request.GET.get("fmt", "xlsx")
    return _df_to_http_response(df, "ppp_export", fmt)


# -------------------------
# Attendance
# -------------------------
@teacher_required
def attendance_list(request):
    records = Attendance.objects.select_related("student").order_by("-date")
    return render(request, "core/attendance_list.html", {"records": records})


@teacher_required
def attendance_add(request):
    if request.method == "POST":
        form = AttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.marked_by = request.user
            att.save()
            messages.success(request, "Attendance marked.")
            return redirect("core:attendance_list")
    else:
        form = AttendanceForm()
    return render(request, "core/attendance_mark.html", {"form": form})


@teacher_required
def upload_attendance_excel(request):
    summary = {"saved": 0, "skipped": 0, "errors": []}

    if request.method == "POST":
        file = request.FILES.get("excel_file")
        if not file:
            messages.error(request, "No file uploaded.")
            return redirect("core:attendance_upload")

        try:
            df = pd.read_excel(file)
        except Exception as e:
            messages.error(request, f"Invalid file: {e}")
            return redirect("core:attendance_upload")

        required_cols = {"department", "class_roll_no", "date", "status"}
        if not required_cols.issubset(df.columns):
            messages.error(request, "Required columns missing in Excel.")
            return redirect("core:attendance_upload")

        for idx, row in df.iterrows():
            try:
                dept = str(row["department"]).strip()
                roll = str(row["class_roll_no"]).strip()
                status = str(row["status"]).strip().lower()
                remarks = str(row.get("remarks", "")).strip()
                date = pd.to_datetime(row["date"]).date()

                if status not in ["present", "absent", "leave"]:
                    summary["skipped"] += 1
                    continue

                student = Student.objects.filter(
                    class_roll_no=roll,
                    department=dept
                ).first()

                if not student:
                    summary["skipped"] += 1
                    continue

                Attendance.objects.update_or_create(
                    student=student,
                    date=date,
                    defaults={
                        "status": status,
                        "remarks": remarks,
                        "marked_by": request.user,
                    }
                )

                summary["saved"] += 1

            except Exception as e:
                summary["errors"].append(f"Row {idx+2}: {e}")

        messages.success(
            request,
            f"Attendance uploaded: {summary['saved']} saved, {summary['skipped']} skipped"
        )

        return redirect("core:attendance_list")

    return render(request, "core/attendance_upload.html")




# -------------------------
# PPP
# -------------------------
@teacher_required
def ppp_list(request):
    ppp_entries = PPPEntry.objects.select_related("student", "created_by").order_by("-date")
    return render(request, "core/ppp_list.html", {"ppp_entries": ppp_entries})


@teacher_required
def ppp_add(request):
    if request.method == "POST":
        form = PPPEntryForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.created_by = request.user
            p.save()
            messages.success(request, "PPP entry added.")
            return redirect("core:ppp_list")
    else:
        form = PPPEntryForm()
    return render(request, "core/ppp_add.html", {"form": form})


# -------------------------
# Fees
# -------------------------
@teacher_required
def fees_list(request):
    payments = FeePayment.objects.select_related("student", "received_by").order_by("-date")
    return render(request, "core/fees_list.html", {"payments": payments})


@teacher_required
def fees_add(request):
    if request.method == "POST":
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.received_by = request.user
            f.save()
            messages.success(request, "Fee recorded.")
            return redirect("core:fees_list")
    else:
        form = FeePaymentForm()
    return render(request, "core/fees_add.html", {"form": form})

@teacher_required
def upload_fees_excel(request):
    summary = {"saved": 0, "skipped": 0, "errors": []}

    if request.method == "POST":
        file = request.FILES.get("excel_file")

        if not file:
            messages.error(request, "No file uploaded.")
            return redirect("core:fees_upload")

        try:
            df = pd.read_excel(file)
        except Exception as e:
            messages.error(request, f"Invalid file: {e}")
            return redirect("core:fees_upload")

        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        required = {"date", "class_roll_no", "amount"}
        if not required.issubset(df.columns):
            messages.error(
                request,
                "Required columns: date, class_roll_no, amount"
            )
            return redirect("core:fees_upload")

        for idx, row in df.iterrows():
            try:
                roll = str(row["class_roll_no"]).strip()
                student = Student.objects.filter(class_roll_no=roll).first()

                if not student:
                    summary["skipped"] += 1
                    continue

                FeePayment.objects.create(
                    student=student,
                    date=pd.to_datetime(row["date"]).date(),
                    amount=float(row["amount"]),
                    payment_mode=row.get("payment_mode", "cash"),
                    status=row.get("status", "paid"),
                    remarks=row.get("remarks", ""),
                    received_by=request.user,
                )

                summary["saved"] += 1

            except Exception as e:
                summary["skipped"] += 1
                summary["errors"].append(f"Row {idx+2}: {e}")

        messages.success(
            request,
            f"Fees uploaded: {summary['saved']} saved, {summary['skipped']} skipped"
        )
        return redirect("core:fees_list")
    return render(request, "core/fees_upload.html")





# -------------------------
# Notices
# -------------------------
@teacher_required
def notice_list(request):
    notices = Notice.objects.order_by("-created_at")
    return render(request, "core/notice_list.html", {
        "notices": notices
    })



@teacher_required
def notice_add(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        Notice.objects.create(title=title, message=message, created_by=request.user)
        messages.success(request, "Notice created.")
        return redirect("core:notices")
    return render(request, "core/notice_add.html")


@teacher_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    notice.delete()
    messages.success(request, "Notice deleted.")
    return redirect("core:notices")