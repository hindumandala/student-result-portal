from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Student,Marks
from .forms import StudentForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
# Create your views here.

@login_required
def home(request):
    students=Student.objects.all()
    return render(request,'results/home.html',{'students':students})

def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StudentForm()
    return render(request,'results/add_student.html',{'form':form})

def delete_student(request,id):
    student =Student.objects.get(id=id)
    student.delete()
    return redirect('home')

def edit_student(request,id):
    student = Student.objects.get(id=id)
    if request.method=='POST':
        form=StudentForm(request.POST,instance=student)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = StudentForm(instance=student)
    return render(request,'results/edit_student.html',{'form':form})   

def add_marks(request, id):
    student = Student.objects.get(id=id)
    if request.method == 'POST':
        subject = request.POST['subject']
        mark_value = int(request.POST['marks'])
        Marks.objects.update_or_create(
            student=student,
            subject=subject,
            defaults={'marks': mark_value}
        )
        return redirect('student_result', id=id)
    return render(request, 'results/add_marks.html', {'student': student})

def calculate_grade(marks):
    if marks >= 90:
        return 'A'
    elif marks >= 75:
        return 'B'
    elif marks >= 60:
        return 'C'
    elif marks >= 40:
        return 'D'
    else:
        return 'F'

def student_result(request, id):
    student = Student.objects.get(id=id)
    marks = Marks.objects.filter(student=student)
    results = []
    for m in marks:
        results.append({
            'subject': m.subject,
            'marks': m.marks,
            'grade': calculate_grade(m.marks)
        })
    overall_pass = all(m.marks >= 40 for m in marks)
    return render(request, 'results/student_result.html', {
        'student': student,
        'results': results,
        'overall_pass': overall_pass
    })

@login_required
def home(request):
    query = request.GET.get('search', '')
    if query:
        students = Student.objects.filter(name__icontains=query)
    else:
        students = Student.objects.all()
    
    # Dashboard stats
    total_students = Student.objects.count()
    
    # Get all marks and calculate pass/fail
    all_students = Student.objects.all()
    passed = 0
    failed = 0
    for student in all_students:
        marks = Marks.objects.filter(student=student)
        if marks.exists():
            if all(m.marks >= 40 for m in marks):
                passed += 1
            else:
                failed += 1

    return render(request, 'results/home.html', {
        'students': students,
        'search_query': query,
        'total_students': total_students,
        'passed': passed,
        'failed': failed,
    })
def download_result(request, id):
    student = Student.objects.get(id=id)
    marks = Marks.objects.filter(student=student)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.name}_result.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, height - 60, "Student Result Portal")

    # Student Info
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 100, f"Name: {student.name}")
    p.drawString(50, height - 120, f"Roll No: {student.rollno}")
    p.drawString(50, height - 140, f"Email: {student.email}")

    # Table Header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 180, "Subject")
    p.drawString(250, height - 180, "Marks")
    p.drawString(350, height - 180, "Grade")
    p.drawString(450, height - 180, "Status")
    p.line(50, height - 185, 550, height - 185)

    # Table Rows
    y = height - 205
    overall_pass = True
    failed_subjects = []
    for m in marks:
        grade = calculate_grade(m.marks)
        status = "Pass" if m.marks >= 40 else "Fail"
        if m.marks < 40:
            overall_pass = False
            failed_subjects.append(m.subject)
        p.setFont("Helvetica", 11)
        p.drawString(50, y, m.subject)
        p.drawString(250, y, str(m.marks))
        p.drawString(350, y, grade)
        p.drawString(450, y, status)
        y -= 20

    # Overall Result
    p.line(50, y, 550, y)
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    if overall_pass:
        p.setFillColorRGB(0, 0.5, 0)
        p.drawString(50, y, "Overall Result: PASS")
    else:
        p.setFillColorRGB(1, 0, 0)
        p.drawString(50, y, f"Overall Result: FAIL  (Failed in: {', '.join(failed_subjects)})")

    p.showPage()
    p.save()
    return response
    
