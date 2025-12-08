import requests
import json
from itertools import chain
from operator import attrgetter
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.db.models import Sum, Max 
from .models import MotoImage, Profile, Motorcycle, MaintenanceLog, MaintenanceReminder, TripLog
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

def index(request):
    """Dashboard principal con Actividad Mixta (Mantenimiento + Viajes)"""
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        motorcycles = Motorcycle.objects.filter(owner=user, is_active=True)
        
        # Selección de moto
        main_moto = None
        selected_moto_id = request.session.get('selected_moto_id')
        if selected_moto_id:
            main_moto = motorcycles.filter(id=selected_moto_id).first()
        if not main_moto:
            main_moto = motorcycles.first()
            if main_moto:
                request.session['selected_moto_id'] = main_moto.id

        recent_activity = [] 
        maintenance_reminders = []

        if main_moto:
            # 1. Obtener Mantenimientos
            m_logs = MaintenanceLog.objects.filter(motorcycle=main_moto)
            
            # 2. Obtener Viajes
            t_logs = TripLog.objects.filter(motorcycle=main_moto)
            
            # 3. Combinar y Ordenar
            activity_list = sorted(
                chain(m_logs, t_logs),
                key=attrgetter('date'),
                reverse=True
            )
            
            recent_activity = activity_list[:6]
            maintenance_reminders = MaintenanceReminder.objects.filter(motorcycle=main_moto, is_active=True)

        context = {
            'user': user,
            'profile': profile,
            'motorcycles': motorcycles,
            'main_moto': main_moto,
            'recent_activity': recent_activity, 
            'maintenance_reminders': maintenance_reminders,
        }
        return render(request, 'index.html', context)

    return redirect('login')

def switch_moto(request, moto_id):
    if 'user_id' not in request.session: return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    moto = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
    request.session['selected_moto_id'] = moto.id
    return redirect('index')

def profile(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        profile, created = Profile.objects.get_or_create(user=user)
        return render(request, 'profile.html', {'user': user, 'profile': profile})
    return redirect('login')

# --- FUNCION AUXILIAR PARA ID INTELIGENTE ---
def construir_moto_id(make, model):
    """
    Evita duplicar la marca si ya está en el modelo.
    Ej: Make='Hero', Model='Hero Hunk' -> Retorna 'Hero Hunk' (no 'Hero Hero Hunk')
    """
    make = str(make).strip()
    model = str(model).strip()
    if model.lower().startswith(make.lower()):
        return model
    return f"{make} {model}"

# --- SEMÁFORO INTELIGENTE ---
def get_moto_health_color(motorcycle):
    """
    Evalúa la salud global consultando TODA la moto en una sola petición.
    """
    # 1. Construir historial usando AGREGACIÓN (DB side)
    history_qs = MaintenanceLog.objects.filter(motorcycle=motorcycle).values('service_type').annotate(max_km=Max('mileage_at_service'))
    historial_usuario = {h['service_type']: h['max_km'] for h in history_qs}

    # 2. Consultar a la IA (Endpoint Full)
    # FIX: Usamos la función auxiliar para no duplicar marca
    moto_id_completo = construir_moto_id(motorcycle.make, motorcycle.model)
    
    payload = {
        "modelo_id": moto_id_completo,
        "km_actual": motorcycle.mileage,
        "historial_usuario": historial_usuario
    }

    try:
        response = requests.post(
            f'{FLASK_API_URL}/predict_full',
            json=payload,
            auth=API_AUTH,
            timeout=2.0 
        )

        if response.status_code == 200:
            data = response.json()
            diagnostico_global = data.get('diagnostico_global', [])
            
            criticos = 0
            advertencias = 0
            
            # --- DEDUPLICACIÓN INTELIGENTE ---
            items_procesados = {}

            for item in diagnostico_global:
                uid = item.get('componente_id') or item.get('componente')
                intervalo = item.get('datos_tecnicos', {}).get('intervalo_fabricante', 0)

                if uid in items_procesados:
                    prev_intervalo = items_procesados[uid].get('datos_tecnicos', {}).get('intervalo_fabricante', 0)
                    if intervalo > prev_intervalo:
                        items_procesados[uid] = item
                else:
                    items_procesados[uid] = item
            
            for item in items_procesados.values():
                estado = item['analisis_ia']['diagnostico']
                if estado == 'fallo_critico':
                    criticos += 1
                elif estado == 'muy_desgastado':
                    advertencias += 1
            
            if criticos > 0: return 'red'
            if advertencias >= 1: return 'yellow'
            return 'green'
            
    except Exception:
        return 'gray'
    
    return 'gray'

def garage(request):
    if 'user_id' not in request.session: return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    current_filter = request.GET.get('filter', 'active')
    motorcycles_qs = Motorcycle.objects.filter(owner=user).order_by('-is_active', '-id')
    
    motorcycles_data = []
    for moto in motorcycles_qs:
        motorcycles_data.append({
            'obj': moto,
            'health_color': get_moto_health_color(moto) if moto.is_active else 'gray'
        })

    context = {
        'motorcycles_data': motorcycles_data,
        'current_filter': current_filter 
    }
    return render(request, 'garage.html', context)

def map(request):
    if 'user_id' not in request.session: return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    
    selected_id = request.session.get('selected_moto_id')
    motorcycles = Motorcycle.objects.filter(owner=user, is_active=True)
    
    if selected_id:
        main_moto = motorcycles.filter(id=selected_id).first()
    else:
        main_moto = motorcycles.first()

    if request.method == 'POST':
        if not main_moto: return redirect('motoadd')
        TripLog.objects.create(
            motorcycle=main_moto,
            title=request.POST.get('title'),
            date=request.POST.get('date'),
            distance_km=int(request.POST.get('distance')),
            terrain=request.POST.get('terrain'),
            notes=request.POST.get('notes')
        )
        if request.POST.get('update_odometer') == 'on':
            main_moto.mileage += int(request.POST.get('distance'))
            main_moto.save()
        return redirect('map')

    trip_logs = []
    total_km_trips = 0
    if main_moto:
        trip_logs = TripLog.objects.filter(motorcycle=main_moto)
        total_data = trip_logs.aggregate(Sum('distance_km'))
        total_km_trips = total_data['distance_km__sum'] or 0

    context = {
        'user': user,
        'main_moto': main_moto,
        'motorcycles': motorcycles,
        'trips': trip_logs,
        'total_km_trips': total_km_trips
    }
    return render(request, 'map.html', context)

def toggle_moto_status(request, moto_id):
    if 'user_id' not in request.session: return redirect('login')
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])
        moto = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
        moto.is_active = not moto.is_active
        moto.save()
    return redirect('motodetails', moto_id=moto_id)

def motodetails(request, moto_id):
    if 'user_id' not in request.session: return redirect('login')
        
    user = User.objects.get(id=request.session['user_id'])
    motorcycle = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
    
    # 1. Obtener logs para la tabla visual
    logs = MaintenanceLog.objects.filter(motorcycle=motorcycle).order_by('-date')
    
    # 2. Construir Historial Matemático usando AGREGACIÓN
    history_qs = MaintenanceLog.objects.filter(motorcycle=motorcycle).values('service_type').annotate(max_km=Max('mileage_at_service'))
    historial_usuario = {h['service_type']: h['max_km'] for h in history_qs}

    predicciones_display = []
    error_api = None
    
    # 3. Llamada Única a la IA (FIX: No duplicar marca)
    moto_id_completo = construir_moto_id(motorcycle.make, motorcycle.model)
    
    payload = {
        "modelo_id": moto_id_completo,
        "km_actual": motorcycle.mileage,
        "historial_usuario": historial_usuario
    }
    
    try:
        response = requests.post(
            f'{FLASK_API_URL}/predict_full',
            json=payload,
            auth=API_AUTH,
            timeout=2.0
        )
        
        if response.status_code == 200:
            data = response.json()
            diagnostico_global = data.get('diagnostico_global', [])
            
            # --- DEDUPLICACIÓN INTELIGENTE (Visual) ---
            items_procesados = {}

            for item in diagnostico_global:
                uid = item.get('componente_id') or item.get('componente')
                intervalo = item.get('datos_tecnicos', {}).get('intervalo_fabricante', 0)

                if uid in items_procesados:
                    prev_intervalo = items_procesados[uid].get('datos_tecnicos', {}).get('intervalo_fabricante', 0)
                    if intervalo > prev_intervalo:
                        items_procesados[uid] = item
                else:
                    items_procesados[uid] = item
            
            # 4. Mapear respuesta filtrada
            for item in items_procesados.values():
                comp_nombre = item['componente']
                estado_ia = item['analisis_ia']['diagnostico']
                confianza = item['analisis_ia']['confianza']
                
                datos_tec = item['datos_tecnicos']
                km_pieza = datos_tec['km_pieza_actual']
                origen_codigo = datos_tec['origen'] 
                pct_uso = datos_tec['porcentaje_uso']
                
                # --- TRADUCCIÓN AMIGABLE DEL ORIGEN ---
                origen_txt = "Estado Desconocido"
                
                if "servicio_inicial" in origen_codigo:
                    # Ej: "servicio_inicial_500km" -> "Despegue (500 km)"
                    km_meta = origen_codigo.split('_')[-1]
                    origen_txt = f"Despegue ({km_meta})"
                elif "teorico_recurrente" in origen_codigo:
                    origen_txt = "Ciclo Normal"
                elif "historial_real" in origen_codigo:
                    origen_txt = f"Hace {km_pieza} km"
                else:
                    origen_txt = "Cálculo Teórico"
                
                # Barra visual
                urgencia_visual = pct_uso / 100.0
                if estado_ia == 'fallo_critico': 
                    urgencia_visual = 1.0
                elif estado_ia == 'muy_desgastado' and urgencia_visual < 0.8:
                    urgencia_visual = 0.8
                
                predicciones_display.append({
                    "componente": comp_nombre,
                    "prediccion_ia": { 
                        "estado_probable": estado_ia, 
                        "confianza": float(confianza) 
                    },
                    "calculo": { 
                        "urgencia": urgencia_visual, 
                        "origen_dato": origen_txt 
                    }
                })
        else:
            error_api = f"Error Servidor: {response.status_code}"

    except Exception:
        error_api = "Sin conexión IA"

    context = {
        'motorcycle': motorcycle,
        'predicciones': predicciones_display,
        'error_api': error_api,
        'maintenance_logs': logs
    }
    return render(request, 'motodetails.html', context)

def upload_moto_image(request, moto_id):
    if 'user_id' not in request.session: return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    moto = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
    if request.method == 'POST':
        images = request.FILES.getlist('gallery_images')
        for img in images:
            MotoImage.objects.create(motorcycle=moto, image=img)
    return redirect('motodetails', moto_id=moto_id)

def motoadd(request):
    if 'user_id' not in request.session: return redirect('login')
    if request.method == 'POST':
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        km = request.POST.get('mileage')
        nickname = request.POST.get('nickname')
        plate = request.POST.get('plate')
        
        owner_id = request.session.get('user_id')
        if not all([make, model, year, km, nickname]):
            return render(request, 'motoadd.html', {'error': 'Campos obligatorios'})
        
        photo = request.FILES.get('photo')
        owner = User.objects.get(id=owner_id)
        
        motorcycle = Motorcycle(
            make=make,
            model=model,
            year=year,
            mileage=km,
            nickname=nickname,
            plate_number=plate,
            owner=owner,
            photo=photo if photo else 'default_motorcycle_photo.jpg',
            is_active=True
        )
        motorcycle.save()
        return redirect('garage')
    return render(request, 'motoadd.html', {})

# --- FORMULARIO DINÁMICO (V3 + MLOps) ---
def maintenance_add(request, moto_id):
    if 'user_id' not in request.session: return redirect('login')
    
    user = User.objects.get(id=request.session['user_id'])
    motorcycle = get_object_or_404(Motorcycle, owner=user, pk=moto_id)
    
    # LOGICA POST (GUARDAR)
    if request.method == 'POST':
        service_type = request.POST.get('service-type', '').strip()
        date = request.POST.get('date')
        mileage_at_service = request.POST.get('mileage-at-service')
        cost = request.POST.get('cost') or None
        notes = request.POST.get('notes')
        condicion_reportada = request.POST.get('condicion_reportada') 
        
        if not all([service_type, date, mileage_at_service]): 
            messages.error(request, 'Faltan campos obligatorios.')
            return redirect('maintenance_add', moto_id=moto_id)
        
        try:
            MaintenanceLog.objects.create(
                motorcycle=motorcycle, 
                service_type=service_type, 
                date=date, 
                mileage_at_service=int(mileage_at_service), 
                cost=cost, 
                notes=notes
            )
            
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
            
            # Notificar al usuario
            messages.success(request, 'Mantenimiento registrado correctamente.')

            # REPORTE A LA IA (MLOps)
            if condicion_reportada:
                try:
                    # FIX: Usar ID inteligente también aquí
                    moto_id_completo = construir_moto_id(motorcycle.make, motorcycle.model)
                    payload_reporte = {
                        "usuario_id_hash": f"user_{user.id}", 
                        "modelo_id": moto_id_completo, 
                        "componente_id": service_type, 
                        "accion_realizada": "REEMPLAZAR", 
                        "km_realizado_usuario": int(mileage_at_service), 
                        "condicion_reportada": condicion_reportada
                    }
                    requests.post(f'{FLASK_API_URL}/reportar_mantenimiento', data=json.dumps(payload_reporte), headers={'Content-Type': 'application/json'}, auth=API_AUTH, timeout=4)
                except Exception: pass
            
            return redirect('motodetails', moto_id=moto_id)
        except Exception: 
            messages.error(request, 'Ocurrió un error al guardar.')
            return redirect('maintenance_add', moto_id=moto_id)

    # LOGICA GET (MOSTRAR FORMULARIO)
    opciones_mantenimiento = []
    try:
        # FIX: Usar ID inteligente para obtener opciones
        moto_id_completo = construir_moto_id(motorcycle.make, motorcycle.model)
        response = requests.get(
            f'{FLASK_API_URL}/get_maintenance_options',
            params={'modelo_id': moto_id_completo},
            timeout=1.5 
        )
        if response.status_code == 200:
            opciones_mantenimiento = response.json()
    except Exception:
        pass

    if not opciones_mantenimiento:
        opciones_mantenimiento = [
            {"id": "aceite_motor", "label": "Aceite de Motor"},
            {"id": "bujias", "label": "Bujías"},
            {"id": "filtro_aire", "label": "Filtro de Aire"},
            {"id": "kit_arrastre", "label": "Kit de Arrastre"},
            {"id": "frenos", "label": "Frenos General"},
            {"id": "otro", "label": "Otro / Reparación"}
        ]

    context = {
        'motorcycle': motorcycle,
        'service_options': opciones_mantenimiento
    }
    return render(request, 'maintenanceadd.html', context)

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
        profile_picture = request.FILES.get('profile_picture') 
        if password != confirm: return render(request, 'register.html', {'error': 'Las contraseñas no coinciden'})
        username = email.split('@')[0]
        if User.objects.filter(username=username).exists(): username = f"{username}_{User.objects.count()}"
        if User.objects.filter(email=email).exists(): return render(request, 'register.html', {'error': 'Email registrado'})
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()
        if profile_picture:
            Profile.objects.create(user=user, profile_picture=profile_picture)
        else:
            Profile.objects.create(user=user)
        request.session['user_id'] = user.id
        return redirect('motoadd')
    return render(request, 'register.html')

def logout(request):
    if 'user_id' in request.session: del request.session['user_id']
    return redirect('login')

def update_mileage(request, moto_id):
    """Actualización rápida de odómetro + Sincronización IA"""
    if 'user_id' not in request.session: return redirect('login')
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])
        motorcycle = get_object_or_404(Motorcycle, pk=moto_id, owner=user)
        new_km = request.POST.get('new_mileage')
        if new_km:
            try:
                new_km_int = int(new_km)
                if new_km_int > motorcycle.mileage:
                    motorcycle.mileage = new_km_int
                    motorcycle.save()
                    try:
                        # FIX: Usar ID inteligente
                        moto_id_completo = construir_moto_id(motorcycle.make, motorcycle.model)
                        payload = {
                            "usuario_id_hash": f"user_{user.id}",
                            "modelo_id": moto_id_completo,
                            "km_actual": new_km_int
                        }
                        requests.post(f'{FLASK_API_URL}/actualizar_kilometraje', json=payload, auth=API_AUTH, timeout=2)
                    except Exception: pass
            except ValueError: pass
    return redirect('motodetails', moto_id=moto_id)

def edit_profile(request):
    if 'user_id' not in request.session: return redirect('login')
    user = User.objects.get(id=request.session['user_id'])
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
        user.first_name = request.POST.get('first-name')
        user.last_name = request.POST.get('last-name')
        user.email = request.POST.get('email')
        user.save()
        profile.bio = request.POST.get('bio')
        profile.location = request.POST.get('location')
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        profile.save()
        return redirect('profile')
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