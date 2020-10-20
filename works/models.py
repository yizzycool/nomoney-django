from django.db import models

# Create your models here.
class User(models.Model):
    userId = models.CharField(max_length=200, unique=True)
    displayName = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    intro = models.TextField()
    gender = models.CharField(max_length=1)
    birthday = models.DateTimeField()
    phone = models.CharField(max_length=20, unique=True)
    pass


class Case(models.Model):
    caseId = models.IntegerField(primary_key=True)
    userId = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    text = models.TextField()
    location = models.CharField(max_length=100)
    pay = models.IntegerField()
    status = models.CharField(max_length=50)
    publishTime = models.DateTimeField()
    pass


class Application(models.Model):
    caseId = models.ForeignKey(Case, on_delete=models.DO_NOTHING)
    userId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    accepted = models.BooleanField()