from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- 1. PERFIL DE USUARIO ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default_profile_pic.jpg', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

# --- 2. MOTOCICLETA ---
class Motorcycle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='motorcycles')
    nickname = models.CharField(max_length=100, help_text="Apodo de tu moto (ej. La Furia)")
    make = models.CharField(max_length=100, verbose_name="Marca")  # Ej: Bajaj, Yamaha
    model = models.CharField(max_length=100, verbose_name="Modelo") # Ej: Pulsar NS200 (Importante para la IA)
    year = models.IntegerField(verbose_name="Año")
    mileage = models.IntegerField(default=0, verbose_name="Kilometraje Actual")
    photo = models.ImageField(upload_to='moto_photos/', default='default_motorcycle_photo.jpg', blank=True)
    is_active = models.BooleanField(default=True, help_text="Desmarcar si vendiste o diste de baja la moto")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nickname} ({self.make} {self.model})"

# --- 3. REGISTRO DE MANTENIMIENTO (LOGS) ---
class MaintenanceLog(models.Model):
    # Opciones estandarizadas para ayudar a la IA a clasificar
    SERVICE_CHOICES = [
        ('aceite_motor', 'Cambio de Aceite de Motor'),
        ('filtro_aceite', 'Cambio de Filtro de Aceite'),
        ('filtro_aire', 'Limpieza/Cambio Filtro de Aire'),
        ('bujias', 'Cambio de Bujías'),
        ('kit_arrastre', 'Mantenimiento Kit de Arrastre'),
        ('frenos_delanteros', 'Frenos Delanteros (Pastillas/Líquido)'),
        ('frenos_traseros', 'Frenos Traseros (Zapatas/Pastillas)'),
        ('neumaticos', 'Cambio de Neumáticos'),
        ('bateria', 'Batería'),
        ('ajuste_valvulas', 'Ajuste de Válvulas'),
        ('suspension', 'Mantenimiento de Suspensión'),
        ('otro', 'Otro / Reparación General'),
    ]

    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.CASCADE, related_name='maintenance_logs')
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name="Tipo de Servicio")
    date = models.DateField(default=timezone.now, verbose_name="Fecha del Servicio")
    mileage_at_service = models.IntegerField(verbose_name="Kilometraje al momento del servicio")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Costo")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_service_type_display()} - {self.motorcycle.nickname} ({self.date})"

    class Meta:
        ordering = ['-date'] # Los más recientes primero

# --- 4. RECORDATORIOS DE MANTENIMIENTO ---
class MaintenanceReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('distance', 'Por Kilometraje'),
        ('date', 'Por Fecha'),
    ]

    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.CASCADE, related_name='reminders')
    service_type = models.CharField(max_length=100, verbose_name="Servicio a Realizar") # Texto libre o vinculado a choices
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, default='distance')
    
    # Condiciones del recordatorio
    next_service_at_mileage = models.IntegerField(null=True, blank=True, verbose_name="A los Km")
    next_service_date = models.DateField(null=True, blank=True, verbose_name="En la Fecha")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recordatorio: {self.service_type} para {self.motorcycle.nickname}"