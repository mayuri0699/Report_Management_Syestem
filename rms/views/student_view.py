from django.shortcuts import render,redirect, get_object_or_404
from master_api.models import UserAuth, StudentMarks, ReportCard
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# Create your views here.  

@login_required
def student_dashboard(request):
    user = request.user
    student = UserAuth.objects.get(id = user.id)
    return render(request, 'student/student_detail.html',{'student':student} )

@login_required
def student_marks(request):
    student_marks = StudentMarks.objects.filter(student_id=request.user).select_related('class_id', 'subject_id')
    student = UserAuth.objects.get(id = request.user.id)
    data = {
        'student_marks': student_marks,
        'class_obj': student.class_id
        }
    return render(request, 'student/studentmarks.html', data)


def student_report_card(request):
    student = request.user  
    report_card = ReportCard.objects.filter(student_id=student).first()  

    context = {
        'student': student,
        'report_card': report_card
    }

    return render(request, 'student/report_card.html', context)

def download_marksheet(request, report_card_id):
    report_card = get_object_or_404(ReportCard, id=report_card_id)

    file_path = report_card.pdf_url.path  

    with open(file_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="marksheet_{report_card.id}.pdf"'
        return response



