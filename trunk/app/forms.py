# -*- coding: iso-8859-15 -*-
from django import forms
from django.contrib.auth.models import User
from saip.app.models import *
import datetime

class UsuariosForm(forms.ModelForm):
	username = forms.CharField(max_length=30, label='Usuario')
	first_name = forms.CharField(max_length=30, label='Nombre')
	last_name = forms.CharField(max_length=30, label='Apellido')
	email = forms.EmailField(max_length=75, label='Correo Electronico')
	password = forms.CharField(max_length=128, label='Contrasena', widget=forms.PasswordInput())
	password2 = forms.CharField(max_length=128, label='Confirmar contrasena', widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password')

	def clean_password2(self):
		if 'password' in self.cleaned_data:
			password = self.cleaned_data['password']
			password2 = self.cleaned_data['password2']
			if password == password2:
				return password2
		raise forms.ValidationError('Las contrasenas no coinciden')

class ModUsuariosForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password')

class ProyectosForm(forms.ModelForm):
    nombre = forms.CharField(max_length=50, label='Nombre')
    usuario_lider = forms.ModelChoiceField(queryset=User.objects.all(), label='Lider')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')
    fecha_inicio = forms.DateField(required=False, label='Fecha de Inicio')
    fecha_fin = forms.DateField(required=False, label='Fecha de Finalizacion')
    cronograma = forms.FileField(required=False, label='Cronograma')
    class Meta:
		model = Proyecto		
		
class RolesForm(forms.ModelForm):
    nombre = forms.CharField(max_length=50, label='Nombre')
    categoria = forms.CharField(max_length=1, widget=forms.Select(choices=CATEGORY_CHOICES), label='Categoria')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')
    fecHor_creacion = forms.DateTimeField(initial=datetime.datetime.now(), required=False, label='Fecha/Hora de creacion')#ojo
    usuario_creador = forms.ModelChoiceField(queryset=User.objects.all(), label='Creador')
    class Meta:
    	model = Rol

class ItemForm(forms.Form):
    def __init__(self, miembro, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.item = forms.ModelChoiceField(queryset= Rol.objects.filter(categoria = 1), label = miembro.username)

class MiembrosProyectoForm(forms.Form):
    item = forms.ModelChoiceField(queryset= Rol.objects.filter(categoria = 1), label = '')
    usuario = User()

class UsuarioProyectoForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset = User.objects.all())
    rol = forms.ModelChoiceField(queryset = Rol.objects.all())
    proyecto = Proyecto()

    def clean_usuario(self):
        if 'usuario' in self.cleaned_data:
            usuarios_existentes = UsuarioRolProyecto.objects.filter(id = self.proyecto.id)
            for i in usuarios_existentes:
                if(usuarios_existentes.usuario == form.clean_data['usuario']):
                    raise forms.ValidationError('Ya existe este usuario')
            return self.cleaned_data['usuario']
        
class TipoArtefactoForm(forms.ModelForm):
    """Form para Tipo de artefacto."""
    nombre = forms.CharField(max_length=50, label='Nombre')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')
    fase = forms.ModelChoiceField(queryset=Fase.objects.all(), label='Fase')
    class Meta:
    	model = TipoArtefacto

class ArtefactoForm(forms.ModelForm):
    nombre = forms.CharField(max_length=50, label='Nombre')
    estado = forms.CharField(max_length=1, widget=forms.Select(choices=STATUS_CHOICES), label='Estado')
    version = forms.IntegerField() # No deberia estar en el form para editar
    complejidad = forms.IntegerField()
    descripcion_corta = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion Corta')
    descripcion_larga = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion Larga')
    habilitado = forms.BooleanField()
    icono = forms.FileField(required=False, label='Icono de Artefacto')
    relacionados = forms.ModelMultipleChoiceField(queryset=Artefacto.objects.all(), required=False, label='Artefactos relacionados')
    proyectos = forms.ModelChoiceField(queryset=Proyecto.objects.all(), label='Proyectos')
    tipo = forms.ModelChoiceField(queryset=TipoArtefacto.objects.all(), label='Tipo')
    class Meta:
        model = Artefacto
        
