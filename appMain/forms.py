from django import forms
from django.db.models import fields
from .models import Resume
from .models import apti_question
from .models import tech_question
from .models import soft_question


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ('pdf',)


class apti_questionForm(forms.ModelForm):
    class Meta:
        model = apti_question
        fields = "__all__"


class tech_questionForm(forms.ModelForm):
    class Meta:
        model = tech_question
        fields = "__all__"


class soft_questionForm(forms.ModelForm):
    class Meta:
        model = soft_question
        fields = "__all__"
