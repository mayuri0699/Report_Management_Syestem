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

# Create your views here.

def userlogin(request):
    if request.method=='POST':
        username=request.POST['email'].lower()
        password=request.POST['password']

        user=authenticate(request, email=username,password=password)

        if user != None:
            userauth = UserAuth.objects.get(id = user.id)

            if userauth.is_superuser ==True and userauth.is_active == True and userauth.is_staff == True and userauth.is_admin == True:
                login(request,user)
                return redirect('admin_dashboard')
            
            elif userauth.is_superuser ==False and userauth.is_active == True and userauth.is_staff == True and userauth.is_admin == True:
                login(request,user)
                return redirect('teacher_dashboard')
            
            elif userauth.is_superuser ==False and userauth.is_active == True and userauth.is_staff == False and userauth.is_admin == False:
                login(request,user)
                return redirect('student_dashboard')
        else:
            return redirect('/')
    
    return render(request, 'common/login.html')


def verifyemail(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').lower()
        try:
            user = UserAuth.objects.get(email=email)
            request.session['reset_email'] = email  # Store email in session
            return redirect('resetpassword')
        except UserAuth.DoesNotExist:
            messages.error(request, 'Email not found. Please try again.')
            return redirect('verifyemail')
    return render(request, 'common/verifyemail.html')    


def resetpassword(request):
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Unauthorized access.")
        return redirect('verifyemail')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('resetpassword')

        try:
            user = UserAuth.objects.get(email=email)
            user.password = make_password(password)
            user.save()
            messages.success(request, "Password reset successfully.")
            request.session.pop('reset_email', None)
            return redirect('login')
        except UserAuth.DoesNotExist:
            messages.error(request, "Something went wrong. Try again.")
            return redirect('verifyemail')

    return render(request, 'common/resetpassword.html')


# ----------------------------------------  Admin Dashboard     --------------------------------------------------------

@login_required
def logout(request):
    user = request.user
    auth.logout(request)
    return redirect('login')


@login_required
def admin_dashboard(request):
    classes = Classes.objects.all()
    return render(request,'adminuser/class.html', {'classes':classes} )


# ---------------------------------------   Student View    -----------------------------------------------------------

@login_required
def studentsview(request, id):
    class_obj = Classes.objects.get(id=id)
    students = UserAuth.objects.filter(class_id=class_obj, is_superuser=False, is_active=True, is_staff=False, is_admin=False)
    
    return render(request, 'adminuser/studentsview.html', {'students':students, 'class_obj':class_obj})


def studentadd(request, id):
    class_obj = Classes.objects.get(id=id)

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

        return redirect('studentadd', id=id)

    return render(request, 'adminuser/studentadd.html', {'class_obj': class_obj})
    

@login_required
def editstudent(request, class_id, student_id):
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
            return redirect('studentsview', id=class_id)

    return render(request, 'adminuser/editstudent.html', {
        'student': student,
        'class_obj': class_obj
    })


def deletestudent(request, id):
    student = get_object_or_404(UserAuth, id=id)
    student.delete()
    return redirect('studentsview', id=student.class_id.id) 


# ---------------------------------------   Student View    -----------------------------------------------------------

@login_required
def teacher_class(request):
    classes = Classes.objects.all()
    return render(request,'adminuser/teacherclass.html', {'classes':classes} )


@login_required
def teacherlist(request, class_id):
    class_obj = Classes.objects.get(id=class_id)
    teachers = UserAuth.objects.filter(class_id=class_obj, is_superuser=False, is_active=True, is_staff=True, is_admin=True)
    
    return render(request, 'adminuser/teachersview.html', {'teachers':teachers, 'class_obj':class_obj})


def teacheradd(request, class_id):
    class_obj = Classes.objects.get(id=class_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        try:
            UserAuth.objects.create_admin(
                class_id=class_obj,
                name=name,
                email=email,
                password='defaultpassword'
            )
            messages.success(request, "Teacher added successfully.")
        except IntegrityError:
            messages.error(request, "Email already exists.")

        return redirect('teacher_add', class_id=class_id)

    return render(request, 'adminuser/teacheradd.html', {'class_obj': class_obj})
    

@login_required
def teacheredit(request, class_id, teacher_id):
    class_obj = get_object_or_404(Classes, id=class_id)
    teacher = get_object_or_404(UserAuth, id=teacher_id, class_id=class_obj)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        if UserAuth.objects.exclude(id=teacher.id).filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            teacher.name = name
            teacher.email = email
            teacher.save()
            messages.success(request, "Teacher updated successfully.")
            return redirect('teacher_list', class_id=class_id)

    return render(request, 'adminuser/teacheredit.html', {
        'teacher': teacher,
        'class_obj': class_obj
    })


def deleteteacher(request, teacher_id):
    teacher = get_object_or_404(UserAuth, id=teacher_id)
    teacher.delete()
    return redirect('teacher_list', class_id=teacher.class_id.id) 


# ----------------------------------------- Class View  ---------------------------------------------------------

@login_required
def classview(request):
    class_obj = Classes.objects.all().order_by('-id')
    return render(request, 'adminuser/classview.html', {'class_obj':class_obj})


@login_required
def classadd(request):
    if request.method == 'POST':
        class_name = request.POST.get('class_name', '').strip()

        if not class_name:
            messages.error(request, 'Class name is required.')
        elif Classes.objects.filter(class_name__iexact=class_name).exists():
            messages.error(request, 'Class already exists.')
        else:
            Classes.objects.create(class_name=class_name)
            messages.success(request, 'Class added successfully.')
            return redirect('classview')

    return render(request, 'adminuser/classadd.html')


@login_required
def editclass(request, id):
    class_instance = get_object_or_404(Classes, id=id)
    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        if not class_name:
            messages.error(request, 'Class name is required.')
        elif Classes.objects.filter(class_name__iexact=class_name).exclude(id=id).exists():
            messages.error(request, 'Another class with this name already exists.')
        else:
            class_instance.class_name = class_name
            class_instance.save()
            messages.success(request, 'Class updated successfully.')
            return redirect('classview')
    return render(request, 'adminuser/classedit.html', {'class_obj': class_instance})


@login_required
def deleteclass(request, id):
    class_instance = get_object_or_404(Classes, id=id)
    class_instance.delete()
    return redirect('classview')


# ----------------------------------------  Subject View    ----------------------------------------------------------

@login_required
def subjectview(request):
    subject = Subject.objects.all().order_by('-id')
    return render(request, 'adminuser/subjectview.html', {'subject':subject})


@login_required
def subjectadd(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name', '').strip()

        if not subject_name:
            messages.error(request, 'Subject name is required.')
        elif Subject.objects.filter(name__iexact=subject_name).exists():
            messages.error(request, 'Subject already exists.')
        else:
            Subject.objects.create(name=subject_name)
            messages.success(request, 'Subject added successfully.')
            return redirect('subjectview')

    return render(request, 'adminuser/subjectadd.html')


@login_required
def editsubject(request, id):
    subject = get_object_or_404(Subject, id=id)
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        if not subject_name:
            messages.error(request, 'Subject name is required.')
        elif Subject.objects.filter(name__iexact=subject_name).exclude(id=id).exists():
            messages.error(request, 'Another Subject with this name already exists.')
        else:
            subject.name = subject_name
            subject.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('subjectview')
    return render(request, 'adminuser/subjectedit.html', {'subject': subject})


@login_required
def deletesubject(request, id):
    subject = get_object_or_404(Subject, id=id)
    subject.delete()
    return redirect('subjectview')


# ------------------------------------------    Class Subject View  --------------------------------------------------------

@login_required
def classsubject_list(request):
    class_subjects = ClassSubject.objects.select_related('class_id', 'subject_id').all().order_by('-id')
    return render(request, 'adminuser/classsubject_list.html', {'class_subjects': class_subjects})


@login_required
def classsubject_add(request):
    classes = Classes.objects.all()
    subjects = Subject.objects.all()

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')

        if ClassSubject.objects.filter(class_id=class_id, subject_id=subject_id).exists():
            messages.error(request, 'This class-subject combination already exists.')
        else:
            ClassSubject.objects.create(class_id_id=class_id, subject_id_id=subject_id)
            messages.success(request, 'Class subject added successfully.')
            return redirect('classsubject_list')

    return render(request, 'adminuser/classsubject_add.html', {'classes': classes, 'subjects': subjects})


@login_required
def classsubject_edit(request, id):
    classsubject = get_object_or_404(ClassSubject, id=id)
    classes = Classes.objects.all()
    subjects = Subject.objects.all()

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')

        if ClassSubject.objects.exclude(id=id).filter(class_id=class_id, subject_id=subject_id).exists():
            messages.error(request, 'This combination already exists.')
        else:
            classsubject.class_id_id = class_id
            classsubject.subject_id_id = subject_id
            classsubject.save()
            messages.success(request, 'Class subject updated successfully.')
            return redirect('classsubject_list')

    return render(request, 'adminuser/classsubject_edit.html', {
        'classsubject': classsubject,
        'classes': classes,
        'subjects': subjects,
    })


@login_required
def classsubject_delete(request, id):
    classsubject = get_object_or_404(ClassSubject, id=id)
    classsubject.delete()
    return redirect('classsubject_list')


# ------------------------------------------ Marks and Generate Marksheet   --------------------------------------------------------

def calculate_grade(average):
    if average >= 90:
        return 'A+'
    elif average >= 80:
        return 'A'
    elif average >= 70:
        return 'B'
    elif average >= 60:
        return 'C'
    elif average >= 50:
        return 'D'
    else:
        return 'F'
    

def studentmarkadd(request, id):
    student = UserAuth.objects.get(id=id)
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
        # average = updated_marks_qs.aggregate(avg=Coalesce(Avg('marks_obtained'), 0))['avg']
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
        return redirect('studentmarkadd', id=id)

    context = {
        'class_obj': class_obj,
        'student': student,
        'subjects_with_marks': subjects_with_marks
    }

    return render(request, 'adminuser/studentmarkadd.html', context)
    

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

