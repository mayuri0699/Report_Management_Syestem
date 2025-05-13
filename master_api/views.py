from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.db.models import Sum, Count

from master_api.models import Classes, Subject, ClassSubject, StudentMarks
from master_api.serializers import ClassSubjectSerializer, ClassesSerializer, StudentMarksReadSerializer, StudentMarksSerializer, SubjectSerializer
from master_api import util



class ClassesAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ClassesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, 'Class saved successfully.'.title()))
            else:
                errors = util.format_serializer_errors(serializer.errors)
                raise ValueError(errors)
        except Exception as e:
            return Response(util.error(self, 'Something went wrong.', str(e)))

    def get(self, request):
        try:
            search = request.query_params.get("search")
            id = request.query_params.get("id")
            items_per_page = 10
            paginator = PageNumberPagination()
            paginator.page_size = items_per_page

            if id:
                class_obj = Classes.objects.get(id=id)
                serializer = ClassesSerializer(class_obj).data
                return Response(util.success(self, serializer))

            elif search :
                q_object = Q(class_name__icontains=search)
                classes = Classes.objects.filter(q_object).order_by('-id')
                paginated_queryset = paginator.paginate_queryset(classes, request)
                serializers = ClassesSerializer(paginated_queryset, many=True).data
                class_count = classes.count()

                data = {
                    "classes": serializers,
                    "class_count": class_count
                }
                return Response(util.success(self, data))
            else:
                subjects = Classes.objects.all().order_by('-id')
                paginated_queryset = paginator.paginate_queryset(subjects, request)
                serializers = ClassesSerializer(paginated_queryset, many=True).data
                class_count = subjects.count()

                data = {
                    "classes": serializers,
                    "class_count": class_count
                }
                return Response(util.success(self, data))

        except Classes.DoesNotExist:
            return Response(util.error(self, "Class not found".title(), f"No class with id={id}"))
        except Exception as e:
            return Response(util.error(self, 'Something went wrong.', str(e)))

    def put(self, request):
        try:
            id = request.query_params.get("id")
            if not id:
                raise Exception('Required query-param: class_id.')

            class_obj = Classes.objects.get(id=id)
            serializer = ClassesSerializer(instance=class_obj, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, 'Class updated successfully.'))
            else:
                errors = util.format_serializer_errors(serializer.errors)
                return Response(util.error(self, errors), status=400)

        except Classes.DoesNotExist:
            return Response(util.error(self, "Class does not exist.".title()))
        except Exception as e:
            return Response(util.error(self, "Something went wrong!", str(e)))

    def delete(self, request):
        try:
            id = request.query_params.get("id")
            if not id:
                raise Exception('Required query-param: class_id.')

            Classes.objects.get(id=id).delete()
            return Response(util.success(self, "Class deleted successfully.".title()))

        except Classes.DoesNotExist:
            return Response(util.error(self, "Class does not exist.".title()))
        except Exception as e:
            return Response(util.error(self, "Something went wrong!", str(e)))


class SubjectsAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = SubjectSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, 'Subject save successfully.'.title()))
            else:
                errors = util.format_serializer_errors(ser_errors=serializer.errors)
                raise ValueError(errors)
        except Exception as e:
            return Response(util.error(self, 'something went wrong.'.title(), str(e)))
    

    def get(self, request,):
        try:
            search = request.query_params.get("search")
            id = request.query_params.get("id")
            items_per_page = 10
            paginator = PageNumberPagination()
            paginator.page_size = items_per_page

            if id:
                subject = Subject.objects.get(id=id)
                serializers = SubjectSerializer(subject).data
                return Response(util.success(self, serializers))

            elif search:
                q_object = Q(name__icontains=search)
                subjects = Subject.objects.filter(q_object).order_by('-id')
                paginated_queryset = paginator.paginate_queryset(subjects, request)
                serializers = SubjectSerializer(paginated_queryset, many=True).data
                subject_count = subjects.count()

                data = {
                    "subjects": serializers,
                    "subject_count": subject_count
                }
                return Response(util.success(self, data))
            else:
                subjects = Subject.objects.all().order_by('-id')
                paginated_queryset = paginator.paginate_queryset(subjects, request)
                serializers = SubjectSerializer(paginated_queryset, many=True).data
                subject_count = subjects.count()

                data = {
                    "subjects": serializers,
                    "subject_count": subject_count
                }
                return Response(util.success(self, data))
        
        except Subject.DoesNotExist:
            return Response(util.error(self, "Subject not found", f"No subject with id={id}"))
        except Exception as e:
            return Response(util.error(self, 'something went wrong.'.title(), str(e)))
        
    def put(self, request):
        try:
            id = request.query_params.get("id")
            if not id:
                raise Exception('Required query-param: subject_id.')

            subject = Subject.objects.get(id=id)
            serializer = SubjectSerializer(data=request.data, instance=subject, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, 'subject updated successfully.'.title()))
            else:
                errors = util.format_serializer_errors(ser_errors=serializer.errors)
                return Response(util.error(self, errors), status=400)

        except Subject.DoesNotExist:
            return Response(util.error(self, "Subject Does Not Exits.".title()))
        except Exception as e:
            return Response(util.error(self, "Something went wrong!", str(e)))

    def delete(self, request):
        try:
            id = request.query_params.get("id")
            if not id:
                raise Exception('Required query-param: subject_id.')

            Subject.objects.get(id=id).delete()
            return Response(util.success(self, "subject deleted.".title()))

        except Subject.DoesNotExist:
            return Response(util.error(self, "subject Does Not Exits.".title()), status=404)
        except Exception as e:
            return Response(util.error(self, "Something went wrong!", str(e)), status=400)


class ClassSubjectAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = ClassSubjectSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, "Class-Subject mapping saved successfully.".title()))
            else:
                errors = util.format_serializer_errors(serializer.errors)
                raise ValueError(errors)
        except Exception as e:
            return Response(util.error(self, "Something went wrong.", str(e)))
    
    def get(self, request):
        try:
            search = request.query_params.get("search")
            id = request.query_params.get("id")
            paginator = PageNumberPagination()
            paginator.page_size = 10
            q_object = Q()

            if id:
                mapping = ClassSubject.objects.get(id=id)
                serializer = ClassSubjectSerializer(mapping).data
                return Response(util.success(self, serializer))

            elif search:
                q_object |= Q(class_id__class_name__icontains=search)
                q_object |= Q(subject_id__name__icontains=search)

                mappings = ClassSubject.objects.filter(q_object).select_related("class_id", "subject_id").order_by("-id")
                paginated = paginator.paginate_queryset(mappings, request)
                serializer = ClassSubjectSerializer(paginated, many=True).data

                data = {
                    "class_subjects": serializer,
                    "count": mappings.count()
                }
                return Response(util.success(self, data))
            
            else:
                mappings = ClassSubject.objects.all().order_by('-id')
                paginated = paginator.paginate_queryset(mappings, request)
                serializer = ClassSubjectSerializer(paginated, many=True).data

                data = {
                    "class_subjects": serializer,
                    "count": mappings.count()
                }
                return Response(util.success(self, data))

        except ClassSubject.DoesNotExist:
            return Response(util.error(self, "Mapping not found.".title(), f"No mapping with id={id}"))
        except Exception as e:
            return Response(util.error(self, "Something went wrong.", str(e)))

    def put(self, request):
        try:
            id = request.query_params.get("id")
            mapping = ClassSubject.objects.get(id=id)
            serializer = ClassSubjectSerializer(instance=mapping, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, "Class-Subject mapping updated successfully.".title()))
            else:
                errors = util.format_serializer_errors(serializer.errors)
                return Response(util.error(self, errors), status=400)
        except ClassSubject.DoesNotExist:
            return Response(util.error(self, "Mapping does not exist.".title()))
        except Exception as e:
            return Response(util.error(self, "Something went wrong!", str(e)))
    
    def delete(self, request):
        try:
            id = request.query_params.get("id")
            mapping = ClassSubject.objects.get(id=id)
            mapping.delete()
            return Response(util.success(self, "Class-Subject mapping deleted.".title()))
        except ClassSubject.DoesNotExist:
            return Response(util.error(self, "Mapping does not exist.".title()))
        except Exception as e:
            return Response(util.error(self, "Something went wrong!", str(e)))


class StudentMarksAPIView(APIView):

    def post(self, request):
        try:
            serializer = StudentMarksSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, "Marks added successfully.".title()))
            return Response(util.error(self, "Validation failed.".title(), serializer.errors))
        except Exception as e:
            return Response(util.error(self, "Something went wrong.", str(e)))


    def get(self, request):
        try:
            id = request.query_params.get("id")
            search = request.query_params.get("search")
            paginator = PageNumberPagination()
            paginator.page_size = 10
            q_object = Q()
            
            if id:
                marks = StudentMarks.objects.get(id=id)
                serializer = StudentMarksReadSerializer(marks).data
                return Response(util.success(self, serializer))
            
            elif search:
                q_object |= Q(student_id__email__icontains=search)
                q_object |= Q(subject_id__name__icontains=search)
                q_object |= Q(class_id__class_name__icontains=search)

                queryset = StudentMarks.objects.filter(q_object).order_by("-id")
                paginated = paginator.paginate_queryset(queryset, request)
                serializer = StudentMarksReadSerializer(paginated, many=True).data

                return Response(util.success(self, {
                    "marks": serializer,
                    "count": queryset.count()
                }))
            else:
                queryset = StudentMarks.objects.all().order_by("-id")
                paginated = paginator.paginate_queryset(queryset, request)
                serializer = StudentMarksReadSerializer(paginated, many=True).data

                return Response(util.success(self, {
                    "marks": serializer,
                    "count": queryset.count()
                }))

        except StudentMarks.DoesNotExist:
            return Response(util.error(self, "Marks not found.", f"No entry with id={id}"))
        except Exception as e:
            return Response(util.error(self, "Something went wrong.", str(e)))

    def put(self, request):
        try:
            id = request.query_params.get("id")
            marks = StudentMarks.objects.get(id=id)
            serializer = StudentMarksSerializer(instance=marks, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(util.success(self, "Marks updated successfully.".title()))
            return Response(util.error(self, "Validation failed.".title(), serializer.errors))
        except StudentMarks.DoesNotExist:
            return Response(util.error(self, "Marks entry does not exist.".title()))
        except Exception as e:
            return Response(util.error(self, "Something went wrong.", str(e)))
        
    def delete(self, request):
        try:
            id = request.query_params.get("id")
            marks = StudentMarks.objects.get(id=id)
            marks.delete()
            return Response(util.success(self, "Marks deleted successfully.".title()))
        except StudentMarks.DoesNotExist:
            return Response(util.error(self, "Marks entry does not exist.".title()))
        except Exception as e:
            return Response(util.error(self, "Something went wrong.", str(e)))



