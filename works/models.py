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
    displayName = models.CharField(max_length=200, blank=True)
    image = models.CharField(max_length=200, blank=True)
    intro = models.TextField(default='', blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='', blank=True)
    birthday = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=20, blank=True)
    rating = models.FloatField(null=True, default=None, blank=True)
    lineId = models.CharField(max_length=100, blank=True)


class Case(models.Model):
    # alias caseId='id'
    STATUS = [
        ('O', 'open'),
        ('C', 'close'),
        ('D', 'delete'),
    ]
    employerId = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    pay = models.IntegerField(blank=True)
    status = models.CharField(max_length=1, choices=STATUS, default='O', blank=True)
    publishTime = models.DateTimeField(default=tz.localtime(tz.now()), blank=True)
    modifiedTime = models.DateTimeField(default=tz.localtime(tz.now()), blank=True)


class Application(models.Model):
    ACCEPTED = [
        ('A', 'accept'),
        ('R', 'reject'),
        ('T', 'TBC'),
    ]
    caseId = models.ForeignKey(Case, on_delete=models.CASCADE)
    employeeId = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(default='', blank=True)
    accepted = models.CharField(max_length=1, choices=ACCEPTED, default='T', blank=True)
    employerRating = models.FloatField(null=True, default=None, blank=True)
    employeeRating = models.FloatField(null=True, default=None, blank=True)


class Hashtag(models.Model):
    tag = models.CharField(max_length = 20, unique=True, default='')
    count = models.IntegerField(default=0)


class MiddleAgent(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=True)
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, null=True)
