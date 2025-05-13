from django.contrib import admin

from master_api.models import (Classes, Subject, UserAuth, ClassSubject, StudentMarks, ReportCard)

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = Classes.DisplayList
    
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = Subject.DisplayList

@admin.register(UserAuth)
class UserAuthAdmin(admin.ModelAdmin):
    list_display = UserAuth.DisplayList

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ClassSubject.DisplayList

@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = StudentMarks.DisplayList

@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ReportCard.DisplayList



