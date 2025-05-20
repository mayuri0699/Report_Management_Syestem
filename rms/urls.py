from django.urls import path
from rms.views import admin_view
from rms.views import student_view

urlpatterns = [
# Admin Dashboard
    path('',admin_view.userlogin, name='login'),
    path('logout',admin_view.logout,name='logout'),
    path('dashboard',admin_view.admin_dashboard, name='admin_dashboard'), 

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

# Students Dashboard
    path('student-dashboard/',student_view.student_dashboard, name='student_dashboard'), 
    path('studentmarks/', student_view.student_marks, name='studentmarks'),
    path('student_report_card/', student_view.student_report_card, name='student_report_card'),
    path('download_marksheet/<int:report_card_id>/', student_view.download_marksheet, name='download_marksheet'),

]