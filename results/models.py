from django.db import models
# Create your models here.
class Student(models.Model):
    name =models.CharField(max_length=100)
    rollno =models.CharField(max_length=100)
    email =models.EmailField()

    def __str__(self):
        return self.name

class Marks(models.Model):
    student =models.ForeignKey(Student,on_delete=models.CASCADE)#if student deleted marks also deleted
    subject =models.CharField(max_length=100)
    marks =models.IntegerField()

    def __str__(self):
        return f"{self.Student.name}-{self.subject}"
