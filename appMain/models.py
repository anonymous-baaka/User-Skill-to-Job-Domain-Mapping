from django import forms
from django.db import models
from django.db import models
from django.db.models.fields import AutoField, CharField
from django.forms import widgets

# Create your models here.


class Resume(models.Model):
    # title=models.CharField(max_length=100)
    pdf = models.FileField(upload_to="uploads/resume/")
    title = forms.CharField(widget=forms.HiddenInput(), initial='def')

    def __str__(self) -> str:
        return self.title


class apti_question(models.Model):
    id = models.IntegerField(primary_key=True)
    question = models.CharField(max_length=200)

    option1 = models.CharField(max_length=50)
    option2 = models.CharField(max_length=50)
    option3 = models.CharField(max_length=50)
    option4 = models.CharField(max_length=50)
    forms.RadioSelect

    answer = models.CharField(max_length=10)
    tag = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.question


class tech_question(models.Model):
    id = models.IntegerField(primary_key=True)
    question = models.CharField(max_length=200)

    option1 = models.CharField(max_length=150)
    option2 = models.CharField(max_length=150)
    option3 = models.CharField(max_length=150)
    option4 = models.CharField(max_length=150)
    forms.RadioSelect

    answer = models.CharField(max_length=10)
    tag = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.question


class soft_question(models.Model):
    id = models.IntegerField(primary_key=True)
    question = models.CharField(max_length=200)

    option1 = models.CharField(max_length=150)
    option2 = models.CharField(max_length=150)
    option3 = models.CharField(max_length=150)
    option4 = models.CharField(max_length=150)
    forms.RadioSelect

    answer = models.CharField(max_length=10)
    tag = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.question


class jobdomains(models.Model):
    jobdomainid = models.IntegerField(primary_key=True)
    jobdomainname = models.CharField(max_length=50)
    jobdomainskill=models.CharField(max_length=50)
    def __str__(self) -> str:
        return self.jobdomainname
