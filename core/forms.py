# core/forms.py
from django import forms
from .models import Student, PPPEntry, Attendance, FeePayment

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        # exclude user because user created automatically when needed
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'present_address': forms.Textarea(attrs={'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PPPEntryForm(forms.ModelForm):
    class Meta:
        model = PPPEntry
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'activity': forms.Textarea(attrs={'rows': 4}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get("student")
        date = cleaned_data.get("date")
        if student and date and Attendance.objects.filter(student=student, date=date).exists():
            raise forms.ValidationError("Attendance already marked for this student on this date.")
        return cleaned_data

class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['student', 'date', 'amount', 'payment_mode', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }
