from django.urls import path
from rms.views import admin_view
from rms.views import student_view

urlpatterns = [
    # Admin 
    path('',admin_view.userlogin, name='login'),
    path('logout',admin_view.logout,name='logout'),
    path('dashboard',admin_view.admin_dashboard, name='admin_dashboard'), 
    path('studentsview/<int:id>',admin_view.studentsview, name='studentsview'), 
    path('studentadd/<int:id>',admin_view.studentadd, name='studentadd'), 
    path('deletestudent/<int:id>/', admin_view.deletestudent, name='deletestudent'),
    path('editstudent/<int:class_id>/<int:student_id>/', admin_view.editstudent, name='editstudent'),
    path('studentmarkadd/<int:id>',admin_view.studentmarkadd, name='studentmarkadd'), 
    path('download/<int:class_id>/<int:student_id>/', admin_view.downloadMarksheet, name='download'),

    # Students
    path('student-dashboard/',student_view.student_dashboard, name='student_dashboard'), 
    path('studentmarks/', student_view.student_marks, name='studentmarks'),
    path('student_report_card/', student_view.student_report_card, name='student_report_card'),
    path('download_marksheet/<int:report_card_id>/', student_view.download_marksheet, name='download_marksheet'),

]