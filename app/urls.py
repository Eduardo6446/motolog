from django.urls import path
from . import views
from django.conf import settings             # <--- Importar
from django.conf.urls.static import static   # <--- Importar

urlpatterns = [
    
    # Application URLs
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('garage/', views.garage, name='garage'),
    path('map/', views.map, name='map'),
    path('<int:moto_id>/details/', views.motodetails, name='motodetails'),
    path('motoadd/', views.motoadd, name='motoadd'),
    
    # Authentication URLs
    path('accounts/login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    
    # Maintenance URLs
    path('maintenance/<int:moto_id>/add', views.maintenance_add, name='maintenance_add'),
    path('moto/<int:moto_id>/update_km/', views.update_mileage, name='update_mileage'),
    path('moto/switch/<int:moto_id>/', views.switch_moto, name='switch_moto'),
    

]
# Solo sirve archivos media en modo DEBUG (Desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)