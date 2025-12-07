from django.contrib.auth.models import User
from .models import Profile

def user_profile_global(request):
    """
    Este procesador inyecta 'user_global' y 'profile_global' en TODAS las plantillas HTML.
    Resuelve el problema de que la foto desaparezca al cambiar de página.
    """
    context = {}
    
    # Verificamos si hay un usuario logueado en la sesión manual
    if 'user_id' in request.session:
        try:
            user = User.objects.get(id=request.session['user_id'])
            context['user_global'] = user
            
            try:
                context['profile_global'] = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                context['profile_global'] = None
                
        except User.DoesNotExist:
            pass
            
    return context