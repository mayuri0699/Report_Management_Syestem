import datetime
import os

# Third-Party Imports
from weasyprint import HTML

# Django Core Imports
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.db.models import Avg, FloatField, Sum
from django.db.models.functions import Coalesce
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password


# Local App Imports
from master_api.models import (
    Classes,
    ClassSubject,
    ReportCard,
    StudentMarks,
    Subject,
    UserAuth,
)
from rms.views.admin_view import calculate_grade


def teacher_dashboard(request):
    user = request.user
    teacher = UserAuth.objects.get(id = user.id)
    return render(request, 'teacher/teacher_detail.html',{'teacher':teacher} )


def studentview(request):
    teacher = request.user
    class_obj = Classes.objects.get(id=teacher.class_id.id)
    students = UserAuth.objects.filter(class_id=class_obj, is_superuser=False, is_active=True, is_staff=False, is_admin=False)
    
    return render(request, 'teacher/studentsview.html', {'students':students, 'class_obj':class_obj})


def studentadd(request):
    teacher = request.user
    class_obj = Classes.objects.get(id=teacher.class_id.id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')

        try:
            UserAuth.objects.create_user(
                class_id=class_obj,
                name=name,
                email=email,
                roll_number=roll_number,
                password='defaultpassword'
            )
            messages.success(request, "Student added successfully.")
        except IntegrityError:
            messages.error(request, "Email or Roll Number already exists.")

        return redirect('student_add')

    return render(request, 'teacher/studentadd.html', {'class_obj': class_obj})


@login_required
def studentedit(request, class_id, student_id):
    class_obj = get_object_or_404(Classes, id=class_id)
    student = get_object_or_404(UserAuth, id=student_id, class_id=class_obj)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        roll_number = request.POST.get('roll_number')

        if UserAuth.objects.exclude(id=student.id).filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif UserAuth.objects.exclude(id=student.id).filter(roll_number=roll_number).exists():
            messages.error(request, "Roll Number already exists.")
        else:
            student.name = name
            student.email = email
            student.roll_number = roll_number
            student.save()
            messages.success(request, "Student updated successfully.")
            return redirect('student_view')

    return render(request, 'teacher/editstudent.html', {
        'student': student,
        'class_obj': class_obj
    })


def studentdelete(request, student_id):
    student = get_object_or_404(UserAuth, id=student_id)
    student.delete()
    return redirect('student_view') 


def studentmarkadd(request, student_id):
    student = UserAuth.objects.get(id=student_id)
    class_obj = Classes.objects.get(id=student.class_id.id)
    class_subjects = ClassSubject.objects.filter(class_id=class_obj)
    existing_marks_qs = StudentMarks.objects.filter(student_id=student)

    marks_qs = {mark.subject_id.id: mark for mark in existing_marks_qs}

    subjects_with_marks = []
    for cs in class_subjects:
        mark = marks_qs.get(cs.subject_id.id)
        subjects_with_marks.append({
            "subject_id": cs.subject_id.id,
            "subject_name": cs.subject_id.name,
            "marks_obtained": mark.marks_obtained if mark else "",
            "max_marks": mark.max_marks if mark else 100
        })

    if request.method == 'POST':
        for subject_data in subjects_with_marks:
            subject_id = subject_data['subject_id']
            marks_obtained = request.POST.get(f'marks_{subject_id}')
            max_marks = request.POST.get(f'max_marks_{subject_id}')
            if marks_obtained is None:
                continue

            subject = Subject.objects.get(id=subject_id)
            StudentMarks.objects.update_or_create(
                student_id=student,
                class_id=class_obj,
                subject_id=subject,
                defaults={
                    'marks_obtained': marks_obtained,
                    'max_marks': max_marks
                }
            )


        updated_marks_qs = StudentMarks.objects.filter(student_id=student, class_id=class_obj)
        total_max = updated_marks_qs.aggregate(max_total=Coalesce(Sum('max_marks'), 0))['max_total']
        total = updated_marks_qs.aggregate(total=Coalesce(Sum('marks_obtained'), 0))['total']
        average = updated_marks_qs.aggregate(avg=Coalesce(Avg('marks_obtained', output_field=FloatField()), 0.0))['avg']
        percentage = round((total / total_max) * 100, 2) if total_max > 0 else 0.0

        grade = calculate_grade(average)

        
        report_card, created  = ReportCard.objects.update_or_create(
            student_id=student,
            class_id=class_obj,
            defaults={
                'total_marks': total_max,
                'obtained_marks_total': total,
                'percentage': percentage,
                'overall_grade': grade
            }
        )
        updated_marks_qs = StudentMarks.objects.filter(student_id=student)

        html_string = render_to_string('adminuser/report_card.html', {
        'student': student,
        'class_obj': class_obj,
        'marks_qs': updated_marks_qs,
        'total': total,
        'total_max': total_max,
        'percentage': percentage,
        'grade': grade,
        'timestamp': datetime.datetime.now()
        })

        html = HTML(string=html_string)
        pdf_file = html.write_pdf()

        # Save PDF file
        filename = f'reportcards/report_card_{student.roll_number}.pdf'
        file_path = default_storage.save(filename, ContentFile(pdf_file))
        report_card.pdf_url = file_path
        report_card.save()

        messages.success(request, "Marks added/updated successfully.")
        return redirect('student_mark_add', student_id=student_id)

    context = {
        'class_obj': class_obj,
        'student': student,
        'subjects_with_marks': subjects_with_marks
    }

    return render(request, 'teacher/studentmarkadd.html', context)


def downloadMarksheet(request, class_id, student_id):
    report = get_object_or_404(ReportCard, class_id=class_id, student_id=student_id)
    
    if report.pdf_url:
        pdf_path = report.pdf_url.path  
        if os.path.exists(pdf_path):
            return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=os.path.basename(pdf_path))
        else:
            raise Http404("PDF file not found.")
    else:
        raise Http404("Report card PDF not available.")

