from django.urls import path
from master_api import views

urlpatterns = [
    path('classes/', views.ClassesAPIView.as_view()),
    path('subjesct/', views.SubjectsAPIView.as_view()),
    path('class-subject/', views.ClassSubjectAPIView.as_view()),
    path('student-marks/', views.StudentMarksAPIView.as_view()),
    path('sign-up-superuser/', views.SignUpSuperUserAPIView.as_view()),
    path('sign-up-teacher/', views.SignUpTeacherAPIView.as_view()),
    
]