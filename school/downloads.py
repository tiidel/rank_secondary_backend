import io
import csv
import zipfile
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view
from .models import Grade, Student, Guardian, Staff, Subject, Class, User, Terms, School, Program
from rest_framework.views import APIView, status, Response
from wkhtmltopdf.views import PDFTemplateResponse
from collections import defaultdict
from django.db.models import Max, Min

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
    term = get_object_or_404(Terms, id=term_id)
    student_grades = get_object_or_404(Grade, classroom=cls_id, student=stud_id, term=term_id)
    
    grade_list = sorted(student_grades.grade_list.all(), key=lambda grade: grade.sequence.id)

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

    total_coef = 0
    total_weight = 0
    for subject, data in subject_data.items():
        total_coef += data[0].subject.sub_coef
       
    
    # Calculate max and min averages for the given class and term
    max_min_averages = Grade.objects.filter(classroom=cls_id, term=term_id).aggregate(
        max_average=Max('average'), 
        min_average=Min('average')
    )
    
    max_average = max_min_averages['max_average']
    min_average = max_min_averages['min_average']

    print(max_min_averages)
    ctx = {
            'grades_by_sequence': grades_by_sequence, 
            'results': dict(subject_data),
            'position': student_grades.position, 
            'average': round(student_grades.average, 2), 
            'student': student_grades.student,
            "total_coef": total_coef,
            "term": term,
            "max_average": max_average,
            "min_average": min_average
        }
    
    return PDFTemplateResponse(
        request=request,
        template='results/template-one.html',
        context=ctx,
        filename='report_card.pdf'
    )
    return Response({'test response. downloading student data'})




@api_view(['GET'])
def download_all_students_results_for_term(request, cls_id, term_id):
    school = School.objects.first()
    classroom = get_object_or_404(Class, id=cls_id)
    term = get_object_or_404(Terms, id=term_id)
    program = Program.objects.filter(terms=term.id).first()
    print('------------PROGRAM:', program)
    students_grades = Grade.objects.filter(classroom=cls_id, term=term_id)

    all_student_data = []
    subject_grades = defaultdict(list)
    students = []
    class_max_average = float('-inf')
    class_min_average = float('inf')
    total_average = 0

    for student_grade in students_grades:
        students.append(student_grade.student)
        grade_list = student_grade.grade_list.all()
        grades_by_sequence = {}
        subject_data = defaultdict(list)
        
        for entry in grade_list:
            subject = entry.subject.name
            subject_data[subject].append(entry)
            sequence = entry.sequence
            if sequence not in grades_by_sequence:
                grades_by_sequence[sequence] = []
        
        student_results = []
        for subject, grades in subject_data.items():
            if len(grades) == 2:
                avg_grade = (grades[0].grade + grades[1].grade) / 2
                total = avg_grade * grades[0].subject.sub_coef
            else:
                avg_grade = grades[0].grade
                total = avg_grade * grades[0].subject.sub_coef

            appreciation = "Poor"
            if avg_grade > 18:
                appreciation = "Excellent"
            elif avg_grade > 15:
                appreciation = "Very Good"
            elif avg_grade > 13:
                appreciation = "Good"
            elif avg_grade > 9:
                appreciation = "Average"

            student_results.append({
                "subject_name": grades[0].subject.name,
                "grades": grades,
                "avg_grade": avg_grade,
                "sub_coef": grades[0].subject.sub_coef,
                "total": total,
                "appreciation": appreciation
            })

            subject_grades[grades[0].subject.name].append((student_grade.student.id, avg_grade))

        all_student_data.append({
            "grade_sequences": grades_by_sequence,
            "student": student_grade.student,
            "results": student_results,
            "position": student_grade.position,
            "average": round(student_grade.average, 2),
            "total_weight": sum(result["total"] for result in student_results)
        })

        if student_grade.average > class_max_average:
            class_max_average = student_grade.average
        if student_grade.average < class_min_average:
            class_min_average = student_grade.average
        total_average += student_grade.average

    class_mean_average = total_average / len(students_grades)

    # Calculate the position of each student in each subject
    for subject, grades in subject_grades.items():
        grades.sort(key=lambda x: x[1], reverse=True)  # Sort by grade in descending order
        for i, (student_id, avg_grade) in enumerate(grades):
            for student_data in all_student_data:
                if student_data["student"].id == student_id:
                    for result in student_data["results"]:
                        if result["subject_name"] == subject:
                            result["subject_position"] = i + 1

    # Calculate mean subject averages
    subject_averages = {subject: sum(grade for _, grade in grades) / len(grades) for subject, grades in subject_grades.items()}

    class_council_report = {
        "best_average": class_max_average,
        "worst_average": class_min_average,
        "mean_average": class_mean_average,
        "best_subject": max(subject_averages, key=subject_averages.get),
        "best_subject_avg": max(subject_averages.values()),
        "worst_subject": min(subject_averages, key=subject_averages.get),
        "worst_subject_avg": min(subject_averages.values()),
        "subject_averages": subject_averages
    }

    student_list = [{"name": student.user.get_full_name(), "id": student.id, "matricule": student.matricule } for student in students]

    ctx = {
        'term': term,
        'school': school,
        'program': program,
        'all_student_data': all_student_data,
        'class_council_report': class_council_report,
        'student_list': student_list
    }

    return PDFTemplateResponse(
        request=request,
        template='results/multi_student_template.html',
        context=ctx,
        filename='report_cards.pdf'
    )