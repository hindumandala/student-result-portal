from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Student,Marks
from .forms import StudentForm
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

def add_marks(request,id):
    student = Student.objects.get(id=id)
    if request.method=='POST':
        subject= request.POST['subject']
        mark_value= int(request.POST['marks'])
        Marks.objects.create(student=student,subject=subject, marks=mark_value)
        return redirect('student_result',id=id)
    return render(request ,'results/add_marks.html',{'student':student})

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
    return render(request, 'results/student_result.html', {
        'student': student,
        'results': results
    })