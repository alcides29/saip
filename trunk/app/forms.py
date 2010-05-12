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
        
"""
Form para Tipo de artefacto
"""
class TipoArtefactoForm(forms.ModelForm):
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
        
