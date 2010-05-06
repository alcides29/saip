from django.db import models

# Create your models here.

class Proyecto(models.Model):
    nombre = models.CharField(max_length=50)
    usuario_lider = models.CharField(max_length=50)
    decripcion = models.TextField(null=True, blank=True)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    fecha_fin = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    cronograma = models.FileField(upload_to='/tmp')

class Rol(models.Model):
    CATEGORY_CHOICES = (
 	            ('1', 'Rol de Sistema'),
 	            ('2', 'Rol de Proyecto'),
 	        )    
    nombre = models.CharField(max_length=50)
    categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)
    descripcion = models.TextField(null=True, blank=True)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    usuario_creador = models.CharField(max_length=50, null=True, blank=True)#ojo
    
class Usuario(models.Model):
    ID_usuario = models.CharField(max_length=50)
    contrasena = models.CharField(max_length=8)#ojo
    nombre = models.CharField(max_length=50, null=True, blank=True)
    apellido = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    #relaciones con otras tablas
    proyectos = models.ManyToManyField(Proyecto)
    roles = models.ManyToManyField(Rol)

class Privilegio(models.Model):
    descripcion = models.TextField(null=True, blank=True)

class Vista(models.Model):
    descripcion = models.TextField(null=True, blank=True)
    
class Fase(models.Model):
    nombre = models.CharField(max_length=50)
    
class TipoArtefacto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    #claves foraneas
    fase = models.ForeignKey(Fase)

class Artefacto(models.Model):   	
    STATUS_CHOICES = (
 	            ('1', 'Pendiente'),
 	            ('2', 'Modificado'),
                ('3', 'Revisado'),
 	        )
    nombre = models.CharField(max_length=50)
    estado = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=1)
    version = models.PositiveIntegerField()#ojo
    complejidad = models.PositiveIntegerField(default=1)
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    habilitado = models.BooleanField()
    icono = models.FileField(upload_to='/tmp', null=True, blank=True)
    #relaciones con otras tablas
    relacionados = models.ManyToManyField("self")
    #claves foraneas
    proyectos = models.ForeignKey(Proyecto)
    tipo = models.ForeignKey(TipoArtefacto)
   
class Adjunto(models.Model):
    nombre = models.CharField(max_length=50)
    contenido = models.FileField(upload_to='/tmp')
    descripcion = models.TextField(null=True, blank=True)  
    #claves foraneas
    artefacto = models.ForeignKey(Artefacto)

class LineaBase(models.Model):
    fechaCreacion = models.DateField(auto_now=False, auto_now_add=True, editable=False)
    #relaciones con otras tablas
    proyectos = models.ManyToManyField(Proyecto)
    Fase = models.OneToOneField(Fase, parent_link=False)

class Historial(models.Model):
    fechaCreacion = models.DateField(auto_now =False, auto_now_add=True, editable=False)
    #claves foraneas
    artefacto = models.OneToOneField(Artefacto, parent_link=False)#ojo

class RegitroHistorial(models.Model):
    version = models.PositiveIntegerField()#ojo
    descripcion = models.TextField(null=True, blank=True)
    fecha_modificacion = models.DateField(auto_now=True, auto_now_add=False)#ojo
    #claves foraneas
    historial = models.ForeignKey(Historial)

class Permiso(models.Model):
    #claves foraneas
    rol = models.ForeignKey(Rol)
    privilegio = models.ForeignKey(Privilegio)
    vista = models.ForeignKey(Vista)
   

