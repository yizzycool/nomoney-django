from django.db import models
from django.utils import timezone as tz

# Create your models here.
class User(models.Model):
    GENDER = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('', 'None'),
    ]
    userId = models.CharField(max_length=200, unique=True)
    displayName = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    intro = models.TextField()
    gender = models.CharField(max_length=1, choices=GENDER, default='')
    birthday = models.DateField(null=True)
    phone = models.CharField(max_length=20, unique=True)
    county = models.CharField(max_length=20)
    rating = models.FloatField(null=True, default=None)


class Case(models.Model):
    STATUS = [
        ('O', 'open'),
        ('C', 'close'),
        ('D', 'delete'),
    ]
    #caseId = models.IntegerField(unique=True)
    employerId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    text = models.TextField()
    location = models.CharField(max_length=100)
    pay = models.IntegerField()
    status = models.CharField(max_length=1, choices=STATUS, default='O')
    publishTime = models.DateTimeField(default=tz.localtime(tz.now()))
    modifiedTime = models.DateTimeField(default=tz.localtime(tz.now()))


class Application(models.Model):
    ACCEPTED = [
        ('A', 'accept'),
        ('R', 'reject'),
        ('T', 'TBC'),
    ]
    caseId = models.ForeignKey(Case, on_delete=models.DO_NOTHING)
    employeeId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    message = models.TextField()
    accepted = models.BooleanField(max_length=1, choices=ACCEPTED, default='T')
    employerRating = models.FloatField(null=True, default=None)
    employeeRating = models.FloatField(null=True, default=None)