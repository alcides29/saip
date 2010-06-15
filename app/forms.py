# -*- coding: iso-8859-15 -*-
from django import forms
from django.db.models import Q
from django.contrib.auth.models import User
from saip.app.models import *
from saip.app.helper import *
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
	password1 = forms.CharField(widget = forms.PasswordInput, max_length=128, label = u'Escriba su nueva contraseña')
	password2 = forms.CharField(widget = forms.PasswordInput, max_length=128, label = u'Repita la contraseña')
	
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
    		nuevo = self.cleaned_data['nombre']
	    	proyectos = Proyecto.objects.all()
	    	nuevo = self.cleaned_data['nombre']
	    	for proyecto in proyectos:
	    		if proyecto.nombre == nuevo:
	    			raise forms.ValidationError('Ya existe ese nombre. Elija otro.')
    		return nuevo

class ModProyectosForm(forms.Form):
    """Formulario para la creacion de proyectos."""
    nombre = forms.CharField(max_length=50, label='Nombre')
    usuario_lider = forms.ModelChoiceField(queryset=User.objects.all(), label='Lider')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion')
    fecha_inicio = forms.DateField(required=False, label='Fecha de Inicio')
    fecha_fin = forms.DateField(required=False, label='Fecha de Finalizacion')
    cronograma = forms.FileField(required=False, label='Cronograma')
    
    def __init__(self, proyecto, *args, **kwargs):
		super(ModProyectosForm, self).__init__(*args, **kwargs)
		self.proyecto = proyecto
    
    def clean_nombre(self):
    	if 'nombre' in self.cleaned_data:
    		nuevo = self.cleaned_data['nombre']
    		if nuevo != self.proyecto.nombre:
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
	items = forms.ModelMultipleChoiceField(queryset= Rol.objects.filter(categoria=2).exclude(id=2), widget = forms.CheckboxSelectMultiple, required=False)
	
	def __init__(self, miembro, *args, **kwargs):
		super(ItemForm, self).__init__(*args, **kwargs)
		self.fields['items'].label = miembro.username

class UsuarioProyectoForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset = User.objects.all())
    roles = forms.ModelMultipleChoiceField(queryset = Rol.objects.filter(categoria=2).exclude(id=2), widget = forms.CheckboxSelectMultiple, required=False)
    proyecto = Proyecto()
    
    def __init__(self, proyecto, *args, **kwargs):
        super(UsuarioProyectoForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].queryset = User.objects.filter(~Q(id = proyecto.usuario_lider.id))


    def clean_usuario(self):
        if 'usuario' in self.cleaned_data:
            usuarios_existentes = UsuarioRolProyecto.objects.filter(id = self.proyecto.id)
            for i in usuarios_existentes:
                if(usuarios_existentes.usuario == form.clean_data['usuario']):
                    raise forms.ValidationError('Ya existe este usuario')
            return self.cleaned_data['usuario']
        
class TipoArtefactoForm(forms.Form):
    """Form para Tipo de artefacto."""
    nombre = forms.CharField(max_length=5, label='Abreviatura')
    descripcion = forms.CharField(max_length=100, label='Nombre')
    fase = forms.ModelChoiceField(queryset=Fase.objects.all(), label='Fase')
    
    def clean_nombre(self):
    	if 'nombre' in self.cleaned_data:
			roles = TipoArtefacto.objects.all()
			nombre = self.cleaned_data['nombre']
			for item in roles: 
				if nombre == item.nombre:
					raise forms.ValidationError('Ya existe este nombre.')
			return nombre

class ModTipoArtefactoForm(forms.Form):
    """Form para Tipo de artefacto."""
    nombre = forms.CharField(max_length=5, label='Abreviatura')
    descripcion = forms.CharField(max_length=100, label='Nombre')
    fase = forms.ModelChoiceField(queryset=Fase.objects.all(), label='Fase')
    
    def __init__(self, tipo_art, *args, **kwargs):
        super(ModTipoArtefactoForm, self).__init__(*args, **kwargs)
        self.tipo_arterfacto = tipo_art    
    
    def clean_nombre(self):
    	if 'nombre' in self.cleaned_data:
			roles = TipoArtefacto.objects.all()
			nombre = self.cleaned_data['nombre']
			if nombre == self.tipo_arterfacto.nombre:
				return nombre
			for item in roles: 
				if nombre == item.nombre:
					raise forms.ValidationError('Ya existe este nombre.')
			return nombre
		
class TipoArtefactoFaseForm(forms.Form):
    """Form para asociar un tipo de artefacto a una fase de un proyecto."""
    fase = forms.ModelChoiceField(queryset = Fase.objects.all(), widget=forms.RadioSelect, required=False, empty_label=None)
    
class ArtefactoForm(forms.Form):
    complejidad = forms.CharField(max_length=2, widget=forms.Select(choices=COMPLEXITY_CHOICES), label='Complejidad')
    descripcion_corta = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion Corta')
    descripcion_larga = forms.CharField(widget=forms.Textarea(), required=False, label='Descripcion Larga')
    icono = forms.FileField(required=False, label='Icono/Artefacto')
    tipo = forms.ModelChoiceField(queryset=None, label='Tipo')    
    
    def __init__(self, proyect_fase, proyecto_id, *args, **kwargs):
        super(ArtefactoForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].queryset = TipoArtefactoFaseProyecto.objects.filter(proyecto = proyecto_id, fase = proyect_fase)
        print self.fields['tipo'].queryset
        print proyect_fase
        print proyecto_id
        
class ModArtefactoForm(forms.ModelForm):
    tipo = forms.ModelChoiceField(queryset=TipoArtefacto.objects.all(), required=False)    
    class Meta:
        model = Artefacto
        fields = ('complejidad', 'descripcion_corta', 'descripcion_larga', 'icono')
        
    def __init__(self, proyect_fase, *args, **kwargs):
        super(ModArtefactoForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].queryset = TipoArtefactoFaseProyecto.objects.filter(fase = proyect_fase)
        
class RelacionArtefactoForm(forms.Form):
	artefactos = forms.ModelMultipleChoiceField(queryset = None, widget = forms.CheckboxSelectMultiple, required=False)
	
	def __init__(self, art_fase, art, *args, **kwargs):
		super(RelacionArtefactoForm, self).__init__(*args, **kwargs)
		#r = RelArtefacto.objects.filter(padre = art, habilitado = True)
		lista = []
		rel = obtener_relaciones_der(art, [])
		for item in rel:
			lista.append(item.id)
		print lista
		self.fields['artefactos'].queryset = Artefacto.objects.filter(Q(fase = art_fase), ~Q(id = art.id), ~Q(pk__in=lista), Q(proyecto = art.proyecto)) 
        
class AdjuntoForm(forms.Form):
	archivo = forms.FileField(required = False)

