from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

# --- Modelo de Motocicleta (RF-01, RF-05) ---
class Motorcycle(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='motorcycles')
    make = models.CharField(max_length=100, verbose_name="Marca")
    model = models.CharField(max_length=100, verbose_name="Modelo")
    year = models.PositiveIntegerField(verbose_name="Año")
    mileage = models.PositiveIntegerField(verbose_name="Kilometraje")
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apodo")
    photo = models.ImageField(upload_to='motorcycle_photos/', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.make} {self.model} ({self.year}) de {self.owner.username}'

# --- Modelo de Historial de Mantenimiento (RF-02) ---
class MaintenanceLog(models.Model):
    SERVICE_CHOICES = [
        ('oil_change', 'Cambio de Aceite'),
        ('brake_service', 'Servicio de Frenos'),
        ('tire_replacement', 'Cambio de Llantas'),
        ('chain_service', 'Servicio de Cadena'),
        ('general_checkup', 'Revisión General'),
        ('other', 'Otro'),
    ]

    # Relación muchos-a-uno: Una motocicleta puede tener muchos registros de mantenimiento.
    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.CASCADE, related_name='maintenance_logs')
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES, verbose_name="Tipo de Servicio")
    date = models.DateField(verbose_name="Fecha del Servicio")
    mileage_at_service = models.PositiveIntegerField(verbose_name="Kilometraje en el Servicio")
    cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Costo")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Servicio de {self.get_service_type_display()} para {self.motorcycle.model} en {self.date}'

# --- Modelo de Recordatorios (RF-03, RF-04) ---
class MaintenanceReminder(models.Model):
    REMINDER_TYPE_CHOICES = [
        ('distance', 'Por Distancia (km)'),
        ('date', 'Por Fecha'),
    ]

    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.CASCADE, related_name='reminders')
    service_type = models.CharField(max_length=100, verbose_name="Tipo de Servicio a Recordar")
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE_CHOICES, verbose_name="Tipo de Recordatorio")
    
    next_service_at_mileage = models.PositiveIntegerField(null=True, blank=True, verbose_name="Próximo servicio en (km)")
    next_service_date = models.DateField(null=True, blank=True, verbose_name="Fecha del próximo servicio")
    
    is_active = models.BooleanField(default=True, verbose_name="Recordatorio Activo")

    def __str__(self):
        return f'Recordatorio para {self.service_type} de {self.motorcycle.model}'

# --- Modelo de Talleres (RF-06) ---
class Workshop(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre del Taller")
    address = models.CharField(max_length=255, verbose_name="Dirección")
    latitude = models.FloatField(verbose_name="Latitud")
    longitude = models.FloatField(verbose_name="Longitud")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    website = models.URLField(blank=True, null=True, verbose_name="Sitio Web")

    def __str__(self):
        return self.name

# --- Modelo de Consejos y Tips (RF-07) ---
class Tip(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    content = models.TextField(verbose_name="Contenido")
    category = models.CharField(max_length=50, verbose_name="Categoría")
    image = models.ImageField(upload_to='tips_images/', null=True, blank=True, verbose_name="Imagen")
    published_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title
