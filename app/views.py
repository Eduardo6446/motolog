from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile, Motorcycle, MaintenanceLog, MaintenanceReminder

# Create your views here.


def index(request):
    # Aquí podrías obtener información del usuario si está autenticado
    if 'user_id' in request.session:
        user = User.objects.get(id=request.session['user_id'])
        profile = Profile.objects.get(user=user)
        # Aquí podrías obtener información adicional del perfil o motocicletas
        motorcycles = Motorcycle.objects.get(owner=user, is_active=True)

        maintenance_logs = MaintenanceLog.objects.filter(motorcycle__owner=user)
        maintenance_reminders = MaintenanceReminder.objects.filter(motorcycle__owner=user)
        # Puedes pasar esta información al contexto del renderizado
        context = {
            'user': user,
            'profile': profile,
            'motorcycles': motorcycles,
            'maintenance_logs': maintenance_logs,
            'maintenance_reminders': maintenance_reminders
        }
        return render(request, 'index.html', context)

    return render(request, 'index.html', {})

def profile(request):
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