import io
import zipfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from .models import Grade, Student, Guardian, Staff, Subject
from rest_framework.views import APIView, status, Response
from wkhtmltopdf.views import PDFTemplateResponse

@api_view(['GET'])
def download_zip(request, cls, term):
    student_grades = Grade.objects.filter(classroom=cls, term=term)
    
    pdf_content = render_to_string('results/template-one.html', {'grades': student_grades, 'student': student_grades[0].student})
    
    pdf_bytes = io.BytesIO(pdf_content.encode('utf-8'))
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('report_card.pdf', pdf_bytes.getvalue())
    
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="report_card.zip"'
    
    return response



@api_view(['GET'])
def download_student_profile(request, stud_id):
    student = Student.objects.filter(id=stud_id).first()
    guardians = Guardian.objects.filter(student=student)

    if not student:
        return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    ctx = {
        'student': student,
        'guardians': guardians,
    }
    return PDFTemplateResponse(
        request=request,
        template='profile/student-profile.html',
        context=ctx,
        filename=f'{student.user.first_name} {student.user.last_name}.pdf'
    )

    # return Response({'message': 'Student not found'})


@api_view(['GET'])
def download_staff_profile(request, staff_id):
    staff = Staff.objects.filter(id=staff_id).first()

    if not staff:
        return Response({'message': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
    
    subjects = Subject.objects.filter(instructor=staff)
    ctx = {
        'staff': staff,
        'subjects': subjects,
    }
    print(ctx)
    return PDFTemplateResponse(
        request=request,
        template='profile/staff-profile.html',
        context=ctx,
        filename=f'{staff.user.first_name} {staff.user.last_name}.pdf'
    )
