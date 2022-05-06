from django.contrib import admin
from .models import apti_question, tech_question, soft_question,jobdomains

admin.site.register(apti_question)
admin.site.register(tech_question)
admin.site.register(soft_question)
admin.site.register(jobdomains)
