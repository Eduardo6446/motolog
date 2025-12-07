import requests
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from .models import Profile, Motorcycle, MaintenanceLog, MaintenanceReminder
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import dotenv
dotenv.load_dotenv()


# Cargar credenciales desde .env
import os

AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'default_user')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'default_password')


# --- CONFIGURACIÓN ---
FLASK_API_URL = 'http://127.0.0.1:5000'
API_AUTH = (AUTH_USERNAME, AUTH_PASSWORD) 

COMPONENTES_DASHBOARD = [
    ('aceite_motor', 'Aceite de Motor'),
    ('bujias', 'Bujías'),
    ('filtro_aire', 'Filtro de Aire'),
    ('kit_arrastre', 'Kit de Arrastre'),
    ('frenos_delanteros', 'Frenos Delanteros')
]

# ... (index, profile, garage, map se quedan igual) ...
def index(request):
    """Dashboard principal"""
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        motorcycles = Motorcycle.objects.filter(owner=user, is_active=True)
        
        # --- LÓGICA DE SELECCIÓN DE MOTO ---
        main_moto = None
        
        # 1. ¿El usuario ya eligió una moto en esta sesión?
        selected_moto_id = request.session.get('selected_moto_id')
        
        if selected_moto_id:
            # Verificamos que esa moto aún exista y sea suya
            main_moto = motorcycles.filter(id=selected_moto_id).first()
        
        # 2. Si no ha elegido (o la moto se borró), tomamos la primera por defecto
        if not main_moto:
            main_moto = motorcycles.first()
            # Guardamos esta elección por defecto en la sesión para consistencia
            if main_moto:
                request.session['selected_moto_id'] = main_moto.id

        maintenance_logs = []
        maintenance_reminders = []

        if main_moto:
            maintenance_logs = MaintenanceLog.objects.filter(motorcycle=main_moto)[:5]
            maintenance_reminders = MaintenanceReminder.objects.filter(motorcycle=main_moto, is_active=True)

        context = {
            'user': user,
            'profile': profile,
            'motorcycles': motorcycles,
            'main_moto': main_moto,
            'maintenance_logs': maintenance_logs,
            'maintenance_reminders': maintenance_reminders,
        }
        return render(request, 'index.html', context)

    return render(request, 'index.html', {})

# --- NUEVA VISTA: CAMBIAR MOTO ---
def switch_moto(request, moto_id):
    """Cambia la moto principal del dashboard guardando el ID en la sesión"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Solo permitimos cambiar si la moto pertenece al usuario
    user = User.objects.get(id=request.session['user_id'])
    moto = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
    
    # Guardamos la elección en la sesión
    request.session['selected_moto_id'] = moto.id
    
    # Regresamos al dashboard (ahora mostrará la moto elegida)
    return redirect('index')

def profile(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        profile, created = Profile.objects.get_or_create(user=user)
        #motorcycles = Motorcycle.objects.filter(owner=user, is_active=True)
        return render(request, 'profile.html', {'user': user, 'profile': profile})
    return redirect('login')

def garage(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        motorcycles = Motorcycle.objects.filter(owner=user, is_active=True)
        return render(request, 'garage.html', {'motorcycles': motorcycles})
    return redirect('login')

def map(request):
    return render(request, 'map.html', {})

# --- VISTA DE DETALLES CORREGIDA (LÓGICA DE DESGASTE REAL) ---
def motodetails(request, moto_id):
    if 'user_id' not in request.session: return redirect('login')
        
    user = User.objects.get(id=request.session['user_id'])
    motorcycle = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
    
    # 1. BUSCAR ÚLTIMO MANTENIMIENTO DE CADA PIEZA
    # Creamos un diccionario: {'aceite_motor': 11000, 'bujias': 8000, ...}
    # Inicializamos todo en 0 (asumiendo que nunca se cambiaron si no hay logs)
    km_ultimo_cambio = {} 
    
    # Obtenemos todos los logs de esta moto ordenados por kilometraje (ascendente)
    logs = MaintenanceLog.objects.filter(motorcycle=motorcycle).order_by('mileage_at_service')
    
    for log in logs:
        # Al recorrer en orden, sobrescribimos, quedándonos con el valor más alto (el último)
        km_ultimo_cambio[log.service_type] = log.mileage_at_service

    predicciones_display = []
    error_api = None
    
    # 2. CONSULTAR A LA IA CON EL "KM DE USO"
    for comp_id, comp_nombre in COMPONENTES_DASHBOARD:
        try:
            # LÓGICA CLAVE: Restamos el KM actual - KM del último cambio
            km_base = km_ultimo_cambio.get(comp_id, 0)
            km_uso_pieza = motorcycle.mileage - km_base
            
            # Protección por si alguien metió mal un dedo y el log es mayor al actual
            if km_uso_pieza < 0: km_uso_pieza = 0

            # Ahora le preguntamos a la IA: "¿Cómo está un aceite con [km_uso_pieza] km?"
            payload = {
                "modelo": motorcycle.model,
                "componente": comp_id,
                "km": km_uso_pieza  # <--- AQUÍ ESTÁ EL CAMBIO
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                f'{FLASK_API_URL}/predict',
                data=json.dumps(payload),
                headers=headers,
                auth=API_AUTH,
                timeout=2 
            )
            
            if response.status_code == 200:
                data = response.json()
                estado_ia = data.get('prediccion_ia', 'desconocido')
                confianza = data.get('confianza', '0%').replace('%', '')
                
                # Mapeo visual
                urgencia_visual = 0.1
                origen_txt = "Desde fábrica"
                
                if km_base > 0:
                    origen_txt = f"Hace {km_uso_pieza} km"
                
                if estado_ia == 'desgaste_normal': urgencia_visual = 0.4
                elif estado_ia == 'muy_desgastado': urgencia_visual = 0.8
                elif estado_ia == 'fallo_critico': urgencia_visual = 1.0
                
                predicciones_display.append({
                    "componente": comp_nombre,
                    "prediccion_ia": {
                        "estado_probable": estado_ia,
                        "confianza": float(confianza)
                    },
                    "calculo": {
                        "urgencia": urgencia_visual,
                        "origen_dato": origen_txt # Mostramos al usuario hace cuánto se cambió
                    }
                })
            
        except Exception as e:
            error_api = "Conexión parcial con IA"
            print(f"Error pieza {comp_id}: {e}")

    if not predicciones_display and not error_api:
        error_api = "No hay datos suficientes para el diagnóstico."

    context = {
        'motorcycle': motorcycle,
        'predicciones': predicciones_display,
        'error_api': error_api
    }
    return render(request, 'motodetails.html', context)

# ... (motoadd, maintenance_add, auth... todo eso sigue igual) ...
def motoadd(request):
    if 'user_id' not in request.session: return redirect('login')
    if request.method == 'POST':
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        km = request.POST.get('mileage')
        nickname = request.POST.get('nickname')
        owner_id = request.session.get('user_id')
        if not all([make, model, year, km, nickname]):
            return render(request, 'motoadd.html', {'error': 'Campos obligatorios'})
        photo = request.FILES.get('photo')
        owner = User.objects.get(id=owner_id)
        motorcycle = Motorcycle(make=make, model=model, year=year, mileage=km, nickname=nickname, owner=owner, photo=photo or 'default_motorcycle_photo.jpg', is_active=True)
        motorcycle.save()
        return redirect('garage')
    return render(request, 'motoadd.html', {})

def maintenance_add(request, moto_id):
    if 'user_id' not in request.session: return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    motorcycle = get_object_or_404(Motorcycle, owner=user, pk=moto_id)
    if request.method == 'POST':
        service_type = request.POST.get('service-type')
        date = request.POST.get('date')
        mileage_at_service = request.POST.get('mileage-at-service')
        cost = request.POST.get('cost') or None
        notes = request.POST.get('notes')
        condicion_reportada = request.POST.get('condicion_reportada') 
        if not all([service_type, date, mileage_at_service]): return redirect('maintenance_add', moto_id=moto_id)
        try:
            MaintenanceLog.objects.create(motorcycle=motorcycle, service_type=service_type, date=date, mileage_at_service=int(mileage_at_service), cost=cost, notes=notes)
            if int(mileage_at_service) > motorcycle.mileage:
                motorcycle.mileage = mileage_at_service
                motorcycle.save()
            reminder_type = request.POST.get('reminder-type')
            if reminder_type and reminder_type != 'none':
                MaintenanceReminder.objects.filter(motorcycle=motorcycle, service_type__icontains=service_type, is_active=True).update(is_active=False)
                reminder_data = {'motorcycle': motorcycle, 'service_type': f"Próximo {service_type}", 'reminder_type': reminder_type, 'is_active': True}
                if reminder_type == 'distance':
                    val = request.POST.get('next-service-mileage')
                    if val: reminder_data['next_service_at_mileage'] = int(mileage_at_service) + int(val)
                elif reminder_type == 'date':
                    val = request.POST.get('next-service-date')
                    if val: reminder_data['next_service_date'] = val
                if 'next_service_at_mileage' in reminder_data or 'next_service_date' in reminder_data:
                    MaintenanceReminder.objects.create(**reminder_data)
            if condicion_reportada:
                try:
                    payload_reporte = {"usuario_id_hash": f"user_{user.id}", "modelo_id": motorcycle.model, "componente_id": service_type, "accion_realizada": "REEMPLAZAR", "km_realizado_usuario": int(mileage_at_service), "condicion_reportada": condicion_reportada}
                    requests.post(f'{FLASK_API_URL}/reportar_mantenimiento', data=json.dumps(payload_reporte), headers={'Content-Type': 'application/json'}, auth=API_AUTH, timeout=5)
                except Exception: pass
            return redirect('motodetails', moto_id=moto_id)
        except Exception: return redirect('maintenance_add', moto_id=moto_id)
    return render(request, 'maintenanceadd.html', {'motorcycle': motorcycle})

def login(request):
    if request.method == 'POST':
        input_login = request.POST.get('email')
        password = request.POST.get('password')
        user = None
        if '@' in input_login:
            try: user = User.objects.get(email=input_login)
            except User.DoesNotExist: pass
        if not user:
            try: user = User.objects.get(username=input_login)
            except User.DoesNotExist: pass
        if user and user.check_password(password):
            request.session['user_id'] = user.id
            return redirect('index')
        else: return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html', {})

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        confirm = request.POST.get('confirm-password')
        
        # --- AQUÍ ESTÁ EL CAMBIO ---
        # Capturamos la foto del formulario
        profile_picture = request.FILES.get('profile_picture') 

        if password != confirm: return render(request, 'register.html', {'error': 'Las contraseñas no coinciden'})
        username = email.split('@')[0]
        if User.objects.filter(username=username).exists(): username = f"{username}_{User.objects.count()}"
        if User.objects.filter(email=email).exists(): return render(request, 'register.html', {'error': 'Email registrado'})
        
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()
        
        # Creamos el perfil, pasando la foto si existe
        if profile_picture:
            Profile.objects.create(user=user, profile_picture=profile_picture)
        else:
            Profile.objects.create(user=user) # Usa default

        request.session['user_id'] = user.id
        return redirect('motoadd')
    return render(request, 'register.html')

def logout(request):
    if 'user_id' in request.session: del request.session['user_id']
    return redirect('login')


def update_mileage(request, moto_id):
    """
    Vista para actualización rápida de kilometraje (Odómetro).
    Sincroniza con la base de datos local y avisa a la IA.
    """
    if 'user_id' not in request.session: 
        return redirect('login')
    
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])
        motorcycle = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
        
        new_km = request.POST.get('new_mileage')
        
        if new_km:
            try:
                new_km_int = int(new_km)
                
                # Validación básica: No puedes bajar el kilometraje (a menos que haya error)
                if new_km_int > motorcycle.mileage:
                    
                    # 1. ACTUALIZAR DJANGO (Lo que ve el usuario)
                    motorcycle.mileage = new_km_int
                    motorcycle.save()
                    
                    # 2. NOTIFICAR A FLASK (MLOps - Fase 2)
                    # Llamamos al endpoint que acabas de crear en la API
                    try:
                        payload = {
                            "usuario_id_hash": f"user_{user.id}",
                            "modelo_id": motorcycle.model,
                            "km_actual": new_km_int
                        }
                        
                        # Sin auth headers complejos porque es una actualización simple
                        requests.post(
                            f'{FLASK_API_URL}/actualizar_kilometraje',
                            json=payload,
                            auth=API_AUTH,
                            timeout=2 # Timeout corto, no queremos hacer esperar al usuario
                        )
                        print(f"✅ Kilometraje {new_km_int} sincronizado con IA.")
                        
                    except Exception as e:
                        print(f"⚠️ Error avisando a IA (No crítico): {e}")
                
            except ValueError:
                pass # Si envían texto en vez de números, ignoramos

    # Siempre redirigimos a los detalles, haya funcionado o no
    return redirect('motodetails', moto_id=moto_id)


def edit_profile(request):
    """Permite al usuario actualizar sus datos personales y foto."""
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    # Nos aseguramos de que el perfil exista
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # 1. Actualizar datos del Usuario (User Model)
        user.first_name = request.POST.get('first-name')
        user.last_name = request.POST.get('last-name')
        user.email = request.POST.get('email')
        user.save()

        # 2. Actualizar datos del Perfil (Profile Model)
        profile.bio = request.POST.get('bio')
        profile.location = request.POST.get('location')
        
        # Si suben una nueva foto, la actualizamos
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        
        # Opcional: Mensaje de éxito (si usas 'messages' en tu base.html)
        # messages.success(request, 'Perfil actualizado correctamente')

        return redirect('profile')

    # GET: Mostrar formulario con datos actuales
    return render(request, 'edit_profile.html', {'user': user, 'profile': profile})


def change_password(request):
    if 'user_id' not in request.session: return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        if not user.check_password(current): return render(request, 'change_password.html', {'error': 'Contraseña actual incorrecta'})
        if new_pass != confirm: return render(request, 'change_password.html', {'error': 'Las contraseñas no coinciden'})
        user.set_password(new_pass)
        user.save()
        return redirect('profile')
    return render(request, 'change_password.html')