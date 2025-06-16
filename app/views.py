from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from .models import Profile, Motorcycle, MaintenanceLog, MaintenanceReminder
from django.contrib.auth.decorators import login_required


# Create your views here.


def index(request):
    # Aquí podrías obtener información del usuario si está autenticado
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        profile = Profile.objects.get(user=user)
        # Aquí podrías obtener información adicional del perfil o motocicletas
        motorcycles = Motorcycle.objects.get(owner=user, is_active=True)

        maintenance_logs = MaintenanceLog.objects.filter(motorcycle=motorcycles)
        maintenance_reminders = MaintenanceReminder.objects.filter(motorcycle=motorcycles)
        # Puedes pasar esta información al contexto del renderizado
        context = {
            'user': user,
            'profile': profile,
            'motorcycles': motorcycles,
            'maintenance_logs': maintenance_logs,
            'maintenance_reminders': maintenance_reminders,

        }
        return render(request, 'index.html', context)

    return render(request, 'index.html', {})

def profile(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        profile = Profile.objects.get(user=user)
        # Aquí podrías obtener información adicional del perfil o motocicletas
        motorcycles = Motorcycle.objects.filter(owner=user, is_active=True)

        context = {
            'user': user,
            'profile': profile,
            'motorcycles': motorcycles,
        }
        return render(request, 'profile.html', context)
    return render(request, 'profile.html', {})

def garage(request):
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        motorcycles = Motorcycle.objects.filter(owner=user, is_active=True)
        print(f"User ID: {user.id}, Motorcycles: {motorcycles}")
        return render(request, 'garage.html', {'motorcycles': motorcycles})
    return render(request, 'garage.html', {})

def map(request):
    return render(request, 'map.html', {})

def motodetails(request, moto_id):
    return render(request, 'motodetails.html', {})

def motoadd(request):
    if request.method == 'POST':
        # Aquí iría la lógica para añadir una nueva moto
        make = request.POST.get('make')
        model = request.POST.get('model')
        year = request.POST.get('year')
        km = request.POST.get('mileage')
        nickname = request.POST.get('nickname')
        owner_id = request.session.get('user_id')
        if not make or not model or not year or not km or not nickname or not owner_id:
            return render(request, 'motoadd.html', {'error': 'All fields are required'})
        
        photo = request.FILES.get('photo')
        
        # Verificar si el usuario existe
        try:
            owner = User.objects.get(id=owner_id)
        except User.DoesNotExist:
            return render(request, 'motoadd.html', {'error': 'User does not exist'})
        
        # Crear la nueva moto
        motorcycle = Motorcycle(
            make=make,
            model=model,
            year=year,
            mileage=km,
            nickname=nickname,
            owner=owner,
            photo=photo if photo else 'default_motorcycle_photo.jpg',  # Asignar una foto por defecto si no se proporciona
            is_active=True  # Asumimos que la moto es activa al momento de crearla
        )

        motorcycle.save()   

        return redirect('index')
    return render(request, 'motoadd.html', {})


def maintenance_add(request, moto_id):
        # Aquí iría la lógica para añadir un registro de mantenimiento
    user = User.objects.get(id=request.session['user_id'])

    motorcycle = get_object_or_404(Motorcycle, owner=user, pk=moto_id)

    if request.method == 'POST':
        # --- PASO 1: Recolectar datos del formulario principal ---
        service_type = request.POST.get('service-type')
        date = request.POST.get('date')
        mileage_at_service = request.POST.get('mileage-at-service')
        cost = request.POST.get('cost') or None
        notes = request.POST.get('notes')

        # --- Validación básica ---
        if not all([service_type, date, mileage_at_service]):
            return redirect('maintenance_add', motorcycle_id = moto_id)

        try:
            # --- PASO 2: Crear y guardar el registro de mantenimiento ---
            new_log = MaintenanceLog.objects.create(
                motorcycle=motorcycle,
                service_type=service_type,
                date=date,
                mileage_at_service=int(mileage_at_service),
                cost=cost,
                notes=notes
            )
            
            # Actualizamos el kilometraje de la moto
            if int(mileage_at_service) > motorcycle.mileage:
                motorcycle.mileage = mileage_at_service
                motorcycle.save()

            # --- PASO 3: Procesar el recordatorio opcional (Lógica mejorada) ---
            reminder_type = request.POST.get('reminder-type')

            if reminder_type and reminder_type != 'none':
                reminder_data = {
                    'motorcycle': motorcycle,
                    'service_type': f"Próximo {dict(MaintenanceLog.SERVICE_CHOICES).get(service_type, service_type)}",
                    'reminder_type': reminder_type,
                    'is_active': True,
                }

                if reminder_type == 'distance':
                    next_mileage_increase = request.POST.get('next-service-mileage')
                    # Comprobar que el valor no esté vacío
                    if next_mileage_increase:
                        reminder_data['next_service_at_mileage'] = int(mileage_at_service) + int(next_mileage_increase)
                        MaintenanceReminder.objects.create(**reminder_data)

                elif reminder_type == 'date':
                    next_date = request.POST.get('next-service-date')
                    # Comprobar que el valor no esté vacío
                    if next_date:
                        reminder_data['next_service_date'] = next_date
                        MaintenanceReminder.objects.create(**reminder_data)

            return redirect('index')

        except Exception as e:
            # Capturamos cualquier error y lo mostramos
            return redirect('maintenance_add', motorcycle_id=moto_id)

    # Si el método es GET
    return render(request, 'maintenanceadd.html', {'motorcycle': motorcycle})
               

def login(request):
    if request.method == 'POST':
        # Aquí iría la lógica de autenticación
        username = request.POST.get('email').split('@')[0]  # Asumiendo que el username es el email sin el dominio
        password = request.POST.get('password')

        # Verificar si el usuario existe y la contraseña es correcta
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                # Aquí podrías iniciar sesión al usuario
                request.session['user_id'] = user.id
            else:
                return render(request, 'login.html', {'error': 'Invalid password'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'User does not exist'})

        return redirect('index')
    return render(request, 'login.html', {})

def register(request):
    if request.method == 'POST':
        print(request.POST)
        # Aquí iría la lógica de registro
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        confirm = request.POST.get('confirm-password')
        # Validar que todos los campos requeridos estén presentes
        if password != confirm:
            print("Passwords do not match")
            return render(request, 'register.html')
        
        username = email.split('@')[0]
        # Verificar si el usuario ya existe

        if User.objects.filter(username=username).exists():
            print("User already exists")
            return render(request, 'register.html')
        
        # Aquí podrías crear el usuario en la base de datos
        print("Creating user")
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()

        # Aquí podrías crear un perfil asociado al usuario si es necesario

        profile = Profile.objects.create(user=user)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        else:
            profile.profile_picture = 'default_profile_pic.jpg'

        profile.save()

        return redirect('index')
    return render(request, 'register.html')

def logout(request):
    # Aquí podrías cerrar la sesión del usuario
    if 'user_id' in request.session:
        del request.session['user_id']
    return render(request, 'login.html', {'message': 'Logout successful'})