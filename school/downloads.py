import io
import zipfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from .models import Grade
from rest_framework.views import APIView, status, Response

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
