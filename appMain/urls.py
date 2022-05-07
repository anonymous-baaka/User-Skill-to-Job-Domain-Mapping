from django.urls import path
from django.urls.resolvers import URLPattern
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index'),
    path('login.html', views.login, name='login'),
    path('signup.html', views.signup, name='signup'),
    path('dashboard.html', views.uploadResume, name='upload'),
    path('dashboard.html', views.quiz, name='dashboard'),
    path('logout.html', views.logout, name='logout'),
    path('apti.html', views.apti, name='apti'),
    path('apti_result.html', views.apti_result, name='aptiresult'),
    path('tech.html', views.tech, name='tech'),
    path('tech_result.html', views.tech_result, name='techresult'),
    path('soft.html', views.soft, name='soft'),
    path('soft_result.html', views.soft_result, name='softresult'),
    path('result.html', views.result, name='result'),
]
