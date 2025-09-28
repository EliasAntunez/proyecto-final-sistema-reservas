from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Cliente

# Formulario personalizado para registro de clientes
class RegistroClienteForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña (mínimo 8 caracteres) *',
            'autocomplete': 'new-password'  # Evita autocompletar
        }),
        min_length=8
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña *',
            'autocomplete': 'new-password'  # Evita autocompletar
        })
    )
    
    class Meta:
        model = Cliente
        fields = ['username', 'nombre', 'apellido', 'email', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario (único) *',
                'autocomplete': 'off'  # Evita autocompletar
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre *',
                'autocomplete': 'off'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido *',
                'autocomplete': 'off'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico *',
                'autocomplete': 'off'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono (opcional)',
                'autocomplete': 'off'
            }),
        }
    
    # Validar que las contraseñas coincidan
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2
    
    # Validar que el email sea único
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email
    
    # Validar que el username sea único
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Cliente.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username

    # Guardar el cliente con la contraseña hasheada
    def save(self, commit=True):
        cliente = super().save(commit=False)
        cliente.set_password(self.cleaned_data['password1'])
        if commit:
            cliente.save()
        return cliente

# Formulario personalizado para login
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario *',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña *',
            'autocomplete': 'off'  # Evita autocompletar
        })
    )


# Vista para registro de clientes
def registro(request):
    if request.user.is_authenticated:
        return redirect('home')

    # si el método es POST, procesar el formulario
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        
        # si el formulario es válido, crear el cliente y redirigir
        if form.is_valid():
            cliente = form.save()
            login(request, cliente)
            messages.success(request, f'¡Bienvenido {cliente.nombre}! Tu cuenta ha sido creada exitosamente.')
            return redirect('home')
        
        # si el formulario no es válido, mostrar errores
        else:
            messages.error(request, 'Por favor corrige los errores indicados.')
    
    # si el método es GET, mostrar el formulario vacío
    else:
        form = RegistroClienteForm()
    
    # Renderizar la plantilla de registro con el formulario
    return render(request, 'registro.html', {'form': form})


# Vista para login único (clientes, empleados, administradores)
def iniciar_sesion(request):
    
    #si el usuario ya está autenticado, redirigir a home
    if request.user.is_authenticated:
        return redirect('home')
    
    # si el método es POST, procesar el formulario
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        # si el formulario es válido, autenticar y redirigir
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            usuario = authenticate(username=username, password=password)
            
            # si la autenticación es exitosa, iniciar sesión
            if usuario is not None:
                login(request, usuario)
                
                # Mensaje personalizado según el tipo de usuario
                if usuario.es_administrador():
                    messages.success(request, f'¡Bienvenido, Administrador {usuario.nombre}!')
                elif usuario.es_empleado():
                    messages.success(request, f'¡Bienvenido, Empleado {usuario.nombre}!')
                else:
                    messages.success(request, f'¡Bienvenido, {usuario.nombre}!')
                
                # Redirigir a la página principal
                return redirect('home')
            
            # si la autenticación falla, mostrar error
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        
        # si el formulario no es válido, mostrar errores
        else:
            messages.error(request, 'Por favor verifica los datos ingresados.')

    # si el método es GET, mostrar el formulario vacío
    else:
        form = LoginForm()
    
    # Renderizar la plantilla de login con el formulario
    return render(request, 'login.html', {'form': form})



# Vista home que redirige según el tipo de usuario
@login_required
def home(request):
    if request.user.es_administrador():
        return render(request, 'home_administrador.html')
    elif request.user.es_empleado():
        return render(request, 'home_empleado.html')
    else:  # es cliente
        return render(request, 'home_cliente.html')

# Vista para cerrar sesión
def cerrar_sesion(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión correctamente!')
    return redirect('iniciar_sesion')