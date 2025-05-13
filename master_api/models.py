from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

# Class Model
class Classes (models.Model):
    class_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.class_name
    
    DisplayList = ['id', 'class_name']


# Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    DisplayList = ['id', 'name']


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_admin(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

        
    def get_by_natural_key(self, email):
        return self.get(email=email)


# UserAuth Model (can represent Student/Teacher/Admin)
class UserAuth(AbstractBaseUser, PermissionsMixin):
    class_id = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional required fields

    def __str__(self):
        return self.name
    
    DisplayList = ['id', 'name', 'email', 'roll_number', 'class_id', 'is_staff', 'is_admin', 'is_active']


# ClassSubject Model 
class ClassSubject(models.Model):
    class_id = models.ForeignKey(Classes, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('class_id', 'subject_id')
    
    DisplayList = ['id', 'class_id', 'subject_id']

# # StudentMarks Model
class StudentMarks(models.Model):
    student_id = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Classes, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.IntegerField()
    max_marks = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student_id', 'class_id', 'subject_id')
    
    DisplayList = ['id', 'student_id', 'class_id', 'subject_id', 'marks_obtained', 'max_marks']


# ReportCard Model
class ReportCard(models.Model):
    student_id = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Classes, on_delete=models.CASCADE)
    total_marks = models.IntegerField()
    obtained_marks_total = models.IntegerField()
    overall_grade = models.CharField(max_length=2)
    percentage = models.FloatField(null=True, blank=True)
    pdf_url = models.FileField(upload_to='reportcards/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ReportCard - {self.student_id.name} of {self.class_id.class_name}"

    DisplayList = ['id', 'student_id', 'class_id', 'total_marks', 'obtained_marks_total', 'overall_grade', 'percentage']

