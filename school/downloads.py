import io
import csv
import zipfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from .models import Grade, Student, Guardian, Staff, Subject, Class, User
from rest_framework.views import APIView, status, Response
from wkhtmltopdf.views import PDFTemplateResponse
from collections import defaultdict

from django.shortcuts import get_object_or_404

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



@api_view(['GET'])
def download_class_list(request, class_id):
    cls = Class.objects.filter(id=class_id).first()

    if not cls:
        return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{cls.level.name} {cls.class_name}.csv"'
    
    
    writer = csv.writer(response)
    writer.writerow(['Full Name', 'Username', 'Email', 'Date Joined'])
    
    students = cls.students.all().order_by('user__first_name')
    
    for student in students:
        writer.writerow([f'{student.user.first_name} {student.user.last_name}', student.user.username, student.user.email, student.user.created_at])

    return response


def download_users_as_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    # Retrieve all users
    users = User.objects.all()

    # Write CSV headers
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Username', 'Email', 'Date Joined'])

    # Write user data
    for user in users:
        writer.writerow([user.first_name, user.last_name, user.username, user.email, user.created_at])

    return response

@api_view(['GET'])
def download_student_result_for_term(request,cls_id, term_id, stud_id):
    student_grades = get_object_or_404(Grade, classroom=cls_id, student=stud_id, term=term_id)
    
    grade_list = student_grades.grade_list.all()

    grades_by_sequence = {}
    for grade in grade_list:
        sequence_id = grade.sequence.id
        if sequence_id not in grades_by_sequence:
            grades_by_sequence[sequence_id] = []


    subject_data = defaultdict(list)

    for entry in grade_list:
        subject = entry.subject.name
        sequence = entry.sequence
        sequences = {
            sequence: entry
        }
        subject_data[subject].append(entry)

    ctx = {
            'grades_by_sequence': grades_by_sequence, 
            'results': dict(subject_data),
            'position': student_grades.position, 
            'average': round(student_grades.average, 2), 
            'student': student_grades.student
        }
    
    return PDFTemplateResponse(
        request=request,
        template='results/template-one.html',
        context=ctx,
        filename='report_card.pdf'
    )
    return Response({'test response. downloading student data'})