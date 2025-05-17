from rest_framework import serializers
from master_api.models import Classes, Subject, ClassSubject, UserAuth, StudentMarks, ReportCard


class ClassesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classes
        fields = ['id', 'class_name']

    
    def create(self, validated_data):
        if Classes.objects.filter(class_name__iexact=validated_data['class_name']).exists():
            raise Exception('class is Already Exits.'.title())
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('class_name'):
            if Classes.objects.filter(class_name__iexact=validated_data['class_name']).exclude(pk=instance.id).exists():
                raise Exception('class is Already Exits.'.title())

        return super().update(instance=instance, validated_data=validated_data)


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ['id', 'name']
    
    def create(self, validated_data):
        if Subject.objects.filter(name__iexact=validated_data['name']).exists():
            raise Exception('Subject is Already Exits.'.title())
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('name'):
            if Subject.objects.filter(name__iexact=validated_data['name']).exclude(pk=instance.id).exists():
                raise Exception('subject is Already Exits.'.title())

        return super().update(instance=instance, validated_data=validated_data)


class ClassSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassSubject
        fields = '__all__'
    
    def create(self, validated_data):
        if ClassSubject.objects.filter(
            class_id=validated_data['class_id'],
            subject_id=validated_data['subject_id']
        ).exists():
            raise Exception("This class-subject mapping already exists.")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        class_id = validated_data.get('class_id', instance.class_id)
        subject_id = validated_data.get('subject_id', instance.subject_id)

        if ClassSubject.objects.filter(class_id=class_id, subject_id=subject_id).exclude(id=instance.id).exists():
            raise Exception("This class-subject mapping already exists.")
        return super().update(instance, validated_data)

    
    def get_classes(self, obj):
        try:
            classes = obj.class_id
            serializer = ClassesSerializer(classes).data
            return serializer
        except Classes.DoesNotExist:
            return None
    
    def get_subject(self, obj):
        try:
            subject = obj.subject_id
            serializer = SubjectSerializer(subject).data
            return serializer
        except Subject.DoesNotExist:
            return None
        

class UserAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAuth
        fields = '__all__'
    
    def get_classes(self, obj):
        try:
            classes = obj.class_id
            serializer = ClassesSerializer(classes).data
            return serializer
        except Classes.DoesNotExist:
            return None


class UserAuthReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAuth
        exclude = ('password', 'created_at', 'updated_at')
    

class StudentMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMarks
        fields = '__all__'

    def create(self, validated_data):
        if StudentMarks.objects.filter(
            student_id=validated_data['student_id'],
            class_id=validated_data['class_id'],
            subject_id=validated_data['subject_id']
        ).exists():
            raise serializers.ValidationError("Marks already exist for this student, class, and subject.".title())
        return super().create(validated_data)

    def update(self, instance, validated_data):
        student = validated_data.get('student_id', instance.student_id)
        class_ = validated_data.get('class_id', instance.class_id)
        subject = validated_data.get('subject_id', instance.subject_id)

        if StudentMarks.objects.filter(
            student_id=student,
            class_id=class_,
            subject_id=subject
        ).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("Marks already exist for this student, class, and subject.".title())
        return super().update(instance, validated_data)
    
     
class StudentMarksReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentMarks
        fields = '__all__'
    
    def get_classes(self, obj):
        try:
            classes = obj.class_id
            serializer = ClassesSerializer(classes).data
            return serializer
        except Classes.DoesNotExist:
            return None
    
    def get_subject(self, obj):
        try:
            subject = obj.subject_id
            serializer = SubjectSerializer(subject).data
            return serializer
        except Subject.DoesNotExist:
            return None
    
    def get_student(self, obj):
        try:
            student = obj.subject_id
            serializer = UserAuthReadSerializer(student).data
            return serializer
        except UserAuth.DoesNotExist:
            return None
    

class ReportCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportCard
        fields = '__all__'

    def get_classes(self, obj):
        try:
            classes = obj.class_id
            serializer = ClassesSerializer(classes).data
            return serializer
        except Classes.DoesNotExist:
            return None
    
    def get_student(self, obj):
        try:
            student = obj.subject_id
            serializer = UserAuthReadSerializer(student).data
            return serializer
        except UserAuth.DoesNotExist:
            return None


class SignUpSuperUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if UserAuth.objects.filter(email=attrs['email']).exists():
            raise Exception('User already exist with this email address.'.title())

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('password and confirm-password should be same.'.title())

        return attrs

    def create(self, validated_data):
        validated_data['email'] = validated_data['email'].lower()
        user = UserAuth.objects.create_superuser(email=validated_data['email'], password=validated_data['password'])
        return user
    

class SignUpTeacherSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class_id = serializers.PrimaryKeyRelatedField(queryset=Classes.objects.all(), required=False, allow_null=True)
    name = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if UserAuth.objects.filter(email=attrs['email']).exists():
            raise Exception('User already exist with this email address.'.title())
        
        if not Classes.objects.filter(id=attrs['class_id'].id).exists():
            raise Exception('Class does not exits.'.title())

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError('password and confirm-password should be same.'.title())

        return attrs

    def create(self, validated_data):
        validated_data['email'] = validated_data['email'].lower()
        validated_data.pop('confirm_password')
        user = UserAuth.objects.create_admin(
            email=validated_data['email'], 
            password=validated_data['password'],
            class_id=validated_data['class_id'],
            name=validated_data['name']
            )
        return user