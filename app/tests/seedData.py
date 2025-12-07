import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DJANGO
# -----------------------------------------------------------------------------
# ¡IMPORTANTE! Cambia 'nombre_de_tu_proyecto.settings' por el nombre real 
# de tu carpeta de configuración (donde está settings.py).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import Profile, Motorcycle, MaintenanceLog, MaintenanceReminder 
# Nota: Cambia 'app.models' si tu aplicación se llama diferente (ej: 'core.models')

# -----------------------------------------------------------------------------
# DATOS MAESTROS (Compatibles con tu IA)
# -----------------------------------------------------------------------------

# Estos modelos coinciden con tu base_conocimiento.json para que la IA funcione
MODELOS_IA = [
    {"make": "Bajaj", "model": "Bajaj_Pulsar_NS200", "real_name": "Pulsar NS200"},
    {"make": "Bajaj", "model": "Bajaj_Boxer_150", "real_name": "Boxer 150"},
    {"make": "Hero", "model": "Hero_Hunk_160R_4V", "real_name": "Hunk 160R 4V"},
    {"make": "Genesis", "model": "Genesis_KA_150", "real_name": "KA 150"},
    {"make": "Keeway", "model": "Keeway_RKS_125", "real_name": "RKS 125"},
]

USUARIOS_PRUEBA = [
    {"username": "demo_user", "email": "demo@motolog.com", "first": "Usuario", "last": "Demo"},
    {"username": "juan_perez", "email": "juan@gmail.com", "first": "Juan", "last": "Pérez"},
    {"username": "maria_rod", "email": "maria@hotmail.com", "first": "María", "last": "Rodríguez"},
]

SERVICIOS_COMUNES = [
    'aceite_motor', 'bujias', 'filtro_aire', 'kit_arrastre', 'frenos_delanteros'
]

# -----------------------------------------------------------------------------
# LÓGICA DE GENERACIÓN
# -----------------------------------------------------------------------------

def run_seed():
    print("🌱 Iniciando sembrado de datos...")

    # 1. Crear Usuarios
    for u_data in USUARIOS_PRUEBA:
        if not User.objects.filter(username=u_data['username']).exists():
            print(f"   Creating user: {u_data['username']}")
            user = User.objects.create_user(
                username=u_data['username'],
                email=u_data['email'],
                password='password123', # Contraseña genérica
                first_name=u_data['first'],
                last_name=u_data['last']
            )
            # Crear perfil
            Profile.objects.get_or_create(user=user)
            
            # 2. Crear Motos para este usuario
            crear_motos_para_usuario(user)
        else:
            print(f"   User {u_data['username']} already exists. Skipping.")

    print("\n✅ ¡Datos de prueba generados correctamente!")
    print("   Usuario Demo: demo_user / password123")

def crear_motos_para_usuario(user):
    # Generar entre 1 y 2 motos por usuario
    num_motos = random.randint(1, 2)
    
    for _ in range(num_motos):
        spec = random.choice(MODELOS_IA)
        mileage_actual = random.randint(5000, 25000)
        
        moto = Motorcycle.objects.create(
            owner=user,
            nickname=f"Mi {spec['real_name']}",
            make=spec['make'],
            model=spec['model'], # ID que la IA entiende
            year=random.randint(2018, 2024),
            mileage=mileage_actual,
            is_active=True
        )
        print(f"     -> Moto agregada: {moto.nickname}")

        # 3. Crear Historial de Mantenimiento (Logs)
        # Creamos registros en el pasado para que la gráfica tenga datos
        for _ in range(random.randint(3, 6)):
            tipo_servicio = random.choice(SERVICIOS_COMUNES)
            dias_atras = random.randint(30, 360)
            km_atras = random.randint(1000, 4000)
            
            # El mantenimiento ocurrió hace X tiempo y con menos kilometraje
            fecha_log = timezone.now() - timedelta(days=dias_atras)
            km_log = mileage_actual - km_atras
            if km_log < 0: km_log = 500 # Evitar negativos

            MaintenanceLog.objects.create(
                motorcycle=moto,
                service_type=tipo_servicio,
                date=fecha_log,
                mileage_at_service=km_log,
                cost=random.randint(500, 3000), # Precio en moneda local aprox
                notes="Mantenimiento preventivo registrado automáticamente."
            )
        
        # 4. Crear un Recordatorio Activo (Para que salga en el dashboard)
        if random.choice([True, False]):
            MaintenanceReminder.objects.create(
                motorcycle=moto,
                service_type="Próximo Cambio de Aceite",
                reminder_type="distance",
                next_service_at_mileage=mileage_actual + 500, # Faltan 500km
                is_active=True
            )

if __name__ == '__main__':
    run_seed()