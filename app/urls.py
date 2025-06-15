from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('garage/', views.garage, name='garage'),
    path('map/', views.map, name='map'),
    path('<int:moto_id>/details/', views.motodetails, name='motodetails'),
    path('motoadd/', views.motoadd, name='motoadd'),
    # Authentication URLs
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
]