from django.urls import path
from rms.views import admin_view
from rms.views import student_view
from rms.views import teacher_view

urlpatterns = [
# Admin Dashboard
    path('',admin_view.userlogin, name='login'),
    
    # Reset Password 
    path('verifyemail/',admin_view.verifyemail,name='verifyemail'),
    path('resetpassword/',admin_view.resetpassword,name='resetpassword'),
    path('logout/',admin_view.logout,name='logout'),
    path('dashboard/',admin_view.admin_dashboard, name='admin_dashboard'), 

    #class
    path('classes/', admin_view.classview, name='classview'),
    path('classes/add/', admin_view.classadd, name='classadd'),
    path('classes/edit/<int:id>/', admin_view.editclass, name='editclass'),
    path('classes/delete/<int:id>/', admin_view.deleteclass, name='deleteclass'),

    #Subject
    path('subject/', admin_view.subjectview, name='subjectview'),
    path('subject/add/', admin_view.subjectadd, name='subjectadd'),
    path('subject/edit/<int:id>/', admin_view.editsubject, name='editsubject'),
    path('subject/delete/<int:id>/', admin_view.deletesubject, name='deletesubject'),

    #Class-Subject
    path('classsubjects/', admin_view.classsubject_list, name='classsubject_list'),
    path('classsubjects/add/', admin_view.classsubject_add, name='classsubject_add'),
    path('classsubjects/edit/<int:id>/', admin_view.classsubject_edit, name='classsubject_edit'),
    path('classsubjects/delete/<int:id>/', admin_view.classsubject_delete, name='classsubject_delete'),

    # Student
    path('studentsview/<int:id>',admin_view.studentsview, name='studentsview'), 
    path('studentadd/<int:id>',admin_view.studentadd, name='studentadd'), 
    path('deletestudent/<int:id>/', admin_view.deletestudent, name='deletestudent'),
    path('editstudent/<int:class_id>/<int:student_id>/', admin_view.editstudent, name='editstudent'),
    path('studentmarkadd/<int:id>',admin_view.studentmarkadd, name='studentmarkadd'), 
    path('download/<int:class_id>/<int:student_id>/', admin_view.downloadMarksheet, name='download'),

    #teacher
    path('teacher/class/', admin_view.teacher_class, name='teacher_class'),
    path('teacher/<int:class_id>/', admin_view.teacherlist, name='teacher_list'),
    path('teacher/add/<int:class_id>/', admin_view.teacheradd, name='teacher_add'),
    path('teacher/edit/<int:class_id>/<int:teacher_id>/', admin_view.teacheredit, name='teacher_edit'),
    path('teacher/delete/<int:teacher_id>/', admin_view.deleteteacher, name='teacher_delete'),

# Students Dashboard
    path('student-dashboard/',student_view.student_dashboard, name='student_dashboard'), 
    path('studentmarks/', student_view.student_marks, name='studentmarks'),
    path('student_report_card/', student_view.student_report_card, name='student_report_card'),
    path('download_marksheet/<int:report_card_id>/', student_view.download_marksheet, name='download_marksheet'),

# Teacher Dashboard
    path('teacher-dashboard/',teacher_view.teacher_dashboard, name='teacher_dashboard'), 
    path('teacher/student/view/',teacher_view.studentview, name='student_view'), 
    path('teacher/student/add/',teacher_view.studentadd, name='student_add'), 
    path('teacher/student/edit/<int:class_id>/<int:student_id>/', teacher_view.studentedit, name='student_edit'),
    path('teacher/student/delete/<int:student_id>/', teacher_view.studentdelete, name='student_delete'),
    path('teacher/student/mark/add/<int:student_id>',teacher_view.studentmarkadd, name='student_mark_add'), 
    path('teacher/student/download-marksheet/<int:class_id>/<int:student_id>/', teacher_view.downloadMarksheet, name='download_marksheet'),


]