from django.db import models

# Create your models here.
class User(models.Model):
    GENDER = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        (None, 'None'),
    ]
    userId = models.CharField(max_length=200, unique=True)
    displayName = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    intro = models.TextField()
    gender = models.CharField(max_length=1, choices=GENDER, default=None)
    birthday = models.DateField(null=True)
    phone = models.CharField(max_length=20, unique=True)
    county = models.CharField(max_length=20)
    rating = models.FloatField(null=True, default=None)


class Case(models.Model):
    #caseId = models.IntegerField(unique=True)
    employerId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    text = models.TextField()
    location = models.CharField(max_length=100)
    pay = models.IntegerField()
    status = models.CharField(max_length=50)
    publishTime = models.DateTimeField()
    modifiedTime = models.DateTimeField()


class Application(models.Model):
    caseId = models.ForeignKey(Case, on_delete=models.DO_NOTHING)
    employeeId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    message = models.TextField()
    accepted = models.BooleanField()
    employerRating = models.FloatField()
    employeeRating = models.FloatField()