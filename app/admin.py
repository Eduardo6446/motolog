from django.contrib import admin
from .models import Profile, Motorcycle, MaintenanceLog, MaintenanceReminder, MotoImage

# Register your models here.
admin.site.register(Profile)
admin.site.register(Motorcycle)
admin.site.register(MaintenanceLog)
admin.site.register(MaintenanceReminder)
admin.site.register(MotoImage)
