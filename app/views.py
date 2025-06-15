from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Profile, Motorcycle, MaintenanceLog, MaintenanceReminder

# Create your views here.


def index(request):
    return render(request, 'index.html', {})

def profile(request):
    return render(request, 'profile.html', {})

def garage(request):
    return render(request, 'garage.html', {})

def map(request):
    return render(request, 'map.html', {})

def motodetails(request, moto_id):
    return render(request, 'motodetails.html', {})

def motoadd(request):
    return render(request, 'motoadd.html', {})

def login(request):
    if request.method == 'POST':
        # Aquí iría la lógica de autenticación
        username = request.POST.get('usermame')
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

        return render(request, 'index.html', {'message': 'Login successful'})
    return render(request, 'login.html', {})

def register(request):
    if request.method == 'POST':
        # Aquí iría la lógica de registro
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        repassword = request.POST.get('repassword')
        if password != repassword:
            return render(request, 'register.html', {'error': 'Passwords do not match'})
        
        username = email.split('@')[0]
        # Verificar si el usuario ya existe

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        # Aquí podrías crear el usuario en la base de datos

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
        user.save()

        # Aquí podrías crear un perfil asociado al usuario si es necesario

        profile = Profile.objects.create(user=user)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        else:
            profile.profile_picture = 'default_profile_pic.jpg'

        profile.save()

        return render(request, 'index.html', {'message': 'Registration successful'})
    return render(request, 'register.html', {})

def logout(request):
    # Aquí podrías cerrar la sesión del usuario
    if 'user_id' in request.session:
        del request.session['user_id']
    return render(request, 'index.html', {'message': 'Logout successful'})