# -*- coding: iso-8859-15 -*-
from django import forms
from django.contrib.auth.models import User
from saip.app.models import *
import datetime

class UsuariosForm(forms.Form):
	username = forms.CharField(max_length=30, label='Usuario')
	first_name = forms.CharField(max_length=30, label='Nombre')
	last_name = forms.CharField(max_length=30, label='Apellido')
	email = forms.EmailField(max_length=75, label='Correo Electronico')
	password = forms.CharField(max_length=128, label='Contrasena', widget=forms.PasswordInput())
	password2 = forms.CharField(max_length=128, label='Confirmar contrasena', widget=forms.PasswordInput())

	def clean_password2(self):
		#comprobar que las contrasenas dadas sean iguales
		if 'password' in self.cleaned_data:
			password = self.cleaned_data['password']
			password2 = self.cleaned_data['password2']
			if password == password2:
				return password2
		raise forms.ValidationError('Las contrasenas no coinciden')
	
	def clean_username(self):
		#controlar que ya no existe el nombre de usuario
		if 'username' in self.cleaned_data:
			usuarios = User.objects.all()
			nuevo = self.cleaned_data['username']
			for item in usuarios:
				if item.username == nuevo:
					raise forms.ValidationError('Ya existe ese nombre de usuario. Elija otro.')
			return nuevo

class ModUsuariosForm(forms.Form):
	first_name = forms.CharField(max_length=30, label='Nombre')
	last_name = forms.CharField(max_length=30, label='Apellido')
	email = forms.EmailField(max_length=75, label='Correo Electronico')

class CambiarPasswordForm(forms.Form):
	password1 = forms.CharField(widget = forms.PasswordInput, max_length=128, label = 'Escriba su contrasena')
	password2 = forms.CharField(widget = forms.PasswordInput, max_length=128, label = 'Repita la contrasena')
	
	def clean_password2(self):
		if 'password1' in self.cleaned_data:
			password1 = self.cleaned_data['password1']
			password2 = self.cleaned_data['password2']
			if password1 == password2:
				return password2
		raise forms.ValidationError('Las contrasenas no coinciden')

class AsignarRolesForm(forms.Form):
	roles = forms.ModelMultipleChoiceField(queryset = None, widget = forms.CheckboxSelectMultiple, label = 'Roles disponibles')
	
	def __init__(self, cat, *args, **kwargs):
		super(AsignarRolesForm, self).__init__(*args, **kwargs)
		self.fields['roles'].queryset = Rol.objects.filter(categoria = cat)

class ProyectosForm(forms.Form):
    """Formulario para la creacion de proyectos."""
    nombre = forms.CharField(max_length=50, label='Nombre')
    usuario_lider = forms.ModelChoiceField(queryset=User.objects.all(), label='Lider')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')
    fecha_inicio = forms.DateField(required=False, label='Fecha de Inicio')
    fecha_fin = forms.DateField(required=False, label='Fecha de Finalizacion')
    cronograma = forms.FileField(required=False, label='Cronograma')
    
    def clean_nombre(self):
    	if 'nombre' in self.cleaned_data:
    		proyectos = Proyecto.objects.all()
    		nuevo = self.cleaned_data['nombre']
    		for proyecto in proyectos:
    			if proyecto.nombre == nuevo:
    				raise forms.ValidationError('Ya existe ese nombre. Elija otro.')
    		return nuevo
	
class RolesForm(forms.Form):
	nombre = forms.CharField(max_length=50, label='Nombre')
	descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')
	categoria = forms.CharField(max_length=1, widget=forms.Select(choices=CATEGORY_CHOICES), label='Elija una categoria')
	#permisos = forms.ModelMultipleChoiceField(queryset = None, widget=forms.CheckboxSelectMultiple, required = False)
		
	def clean_nombre(self):
		if 'nombre' in self.cleaned_data:
			roles = Rol.objects.all()
			nombre = self.cleaned_data['nombre']
			for item in roles: 
				if nombre == item.nombre:
					raise forms.ValidationError('Ya existe ese nombre de rol. Elija otro.')
			return nombre

class PermisosForm(forms.Form):
	permisos = forms.ModelMultipleChoiceField(queryset = None, widget = forms.CheckboxSelectMultiple, required = False)
	
	def __init__(self, cat, *args, **kwargs):
		super(PermisosForm, self).__init__(*args, **kwargs)
		self.fields['permisos'].queryset = Permiso.objects.filter(categoria = cat)
    
class ModRolesForm(forms.Form):
	descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')

class ItemForm(forms.Form):
	items = forms.ModelMultipleChoiceField(queryset= Rol.objects.filter(categoria=2), widget = forms.CheckboxSelectMultiple, required=False)
	
	def __init__(self, miembro, *args, **kwargs):
		super(ItemForm, self).__init__(*args, **kwargs)
		self.fields['items'].label = miembro.username

class UsuarioProyectoForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset = User.objects.all())
    roles = forms.ModelMultipleChoiceField(queryset = Rol.objects.filter(categoria=2), widget = forms.CheckboxSelectMultiple, required=False)
    proyecto = Proyecto()

    def clean_usuario(self):
        if 'usuario' in self.cleaned_data:
            usuarios_existentes = UsuarioRolProyecto.objects.filter(id = self.proyecto.id)
            for i in usuarios_existentes:
                if(usuarios_existentes.usuario == form.clean_data['usuario']):
                    raise forms.ValidationError('Ya existe este usuario')
            return self.cleaned_data['usuario']
        
class TipoArtefactoForm(forms.Form):
    """Form para Tipo de artefacto."""
    nombre = forms.CharField(max_length=50, label='Nombre')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')
    fase = forms.ModelChoiceField(queryset=Fase.objects.all(), label='Fase')
    
    def clean_nombre(self):
    	if 'nombre' in self.cleaned_data:
			roles = TipoArtefacto.objects.all()
			nombre = self.cleaned_data['nombre']
			for item in roles: 
				if nombre == item.nombre:
					raise forms.ValidationError('Ya existe ese nombre de rol. Elija otro.')
			return nombre

class ArtefactoForm(forms.ModelForm):
    nombre = forms.CharField(max_length=50, label='Nombre')
    complejidad = forms.CharField(max_length=1, widget=forms.Select(choices=COMPLEXITY_CHOICES), label='Complejidad')
    descripcion_corta = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion Corta')
    descripcion_larga = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion Larga')
    icono = forms.FileField(required=False, label='Icono')
    #relacionados = forms.ModelMultipleChoiceField(queryset=Artefacto.objects.all(), required=False, label='Artefactos/relacionados')
    tipo = forms.ModelChoiceField(queryset=TipoArtefacto.objects.all(), label='Tipo')
    class Meta:
        model = Artefacto
        fields = ('nombre', 'complejidad', 'descripcion_corta', 'descripcion_larga', 'icono', 'tipo')

class ModArtefactoForm(forms.ModelForm):
    class Meta:
        model = Artefacto
        fields = ('complejidad', 'descripcion_corta', 'descripcion_larga', 'icono', 'tipo')

    
