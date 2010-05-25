# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
CATEGORY_CHOICES = (
                 ('1', 'Rol de Sistema'),
                 ('2', 'Rol de Proyecto'),
             )    

COMPLEXITY_CHOICES = (
                      ('1', '1'),
                      ('2', '2'),
                      ('3', '3'),
                      ('4', '4'),
                      ('5', '5'),
                      ('6', '6'),
                      ('7', '7'),
                      ('8', '8'),
                      ('9', '9'),
                      ('10', '10'),
 	        )    

STATUS_CHOICES = (
 	            ('1', 'Pendiente'),
 	            ('2', 'Modificado'),
                ('3', 'Revisado'),
 	        )

class Permiso(models.Model):
    nombre = models.CharField(unique=True, max_length = 50)
    categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)
    
    def __unicode__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(unique=True, max_length=50)
    categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)
    descripcion = models.TextField(null=True, blank=True)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    usuario_creador = models.ForeignKey(User, null=True)
    permisos = models.ManyToManyField(Permiso)
    
    def __unicode__(self):
        return self.nombre

class Fase(models.Model):
    """Esta clase representa la fase del proyecto."""
    nombre = models.CharField(unique=True, max_length=50)
    
    def __unicode__(self):
        return self.nombre

class Proyecto(models.Model):
    """Clase que representa un proyecto."""
    nombre = models.CharField(unique=True, max_length=50)
    usuario_lider = models.ForeignKey(User)
    fase = models.ForeignKey(Fase)
    descripcion = models.TextField(null=True, blank=True)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    fecha_fin = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    cronograma = models.FileField(upload_to='cronogramas', null=True, blank=True)
    
    def __unicode__(self):
        return self.nombre
    
class TipoArtefacto(models.Model):
    """"Esta clase representa a que tipo pertenece un artefacto."""
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    #claves foraneas
    fase = models.ForeignKey(Fase)
    
    def __unicode__(self):
        return self.nombre

class Artefacto(models.Model):
    """Clase que representa a los artefactos."""
    nombre = models.CharField(unique=True, max_length=50)
    usuario = models.ForeignKey(User)
    fecha_creacion = models.DateField(auto_now_add=True, editable = False)
    estado = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=1)    
    version = models.PositiveIntegerField()
    complejidad = models.IntegerField(max_length=1, choices=COMPLEXITY_CHOICES)
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    habilitado = models.BooleanField(default=1)
    icono = models.FileField(upload_to='icono', null=True, blank=True)
    #relaciones con otras tablas
    #relacionados = models.ManyToManyField("self")
    #claves foraneas
    proyecto = models.ForeignKey(Proyecto)
    tipo = models.ForeignKey(TipoArtefacto)
    
    def __unicode__(self):
        return self.nombre

class Historial(models.Model):
    """Clase que representa el historial de los artefactos"""
    usuario = models.ForeignKey(User)
    fecha_creacion = models.DateField(auto_now =False, auto_now_add=True, editable=False)
    #claves foraneas
    artefacto = models.OneToOneField(Artefacto, parent_link=False)
    
    #def __init__ (self, artefacto):
     #   self.usuario = artefacto.usuario
      #  self.fecha_creacion = artefacto.fecha_creacion
       # self.artefacto = artefacto
        
class RegistroHistorial(models.Model):
    """Clase que representa el Registro de versiones de los artefactos"""
    version = models.PositiveIntegerField()
    estado = models.IntegerField()
    complejidad = models.IntegerField()
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    habilitado = models.BooleanField()
    #icono = models.FileField(upload_to='icono', null=True, blank=True)
    tipo = models.ForeignKey(TipoArtefacto)
    fecha_modificacion = models.DateTimeField(auto_now=True, auto_now_add=False, editable=False)
    #claves foraneas
    historial = models.ForeignKey(Historial)
   
    
class Adjunto(models.Model):
    archivo = models.FileField(upload_to='artefactos')
    descripcion = models.TextField(null=True, blank=True)  
    #claves foraneas
    artefacto = models.ForeignKey(Artefacto)
    
class LineaBase(models.Model):
    fecha_creacion = models.DateField(auto_now=False, auto_now_add=True, editable=False)
    #relaciones con otras tablas
    proyectos = models.ForeignKey(Proyecto)
    Fase = models.OneToOneField(Fase, parent_link=False)#ver


class UsuarioRolProyecto(models.Model):   
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol, null=True)
    proyecto = models.ForeignKey(Proyecto)

    class Meta:
        unique_together = [("usuario", "rol", "proyecto")]
        
class UsuarioRolSistema(models.Model):
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol)
    
    class Meta:
        unique_together = [("usuario", "rol")]

