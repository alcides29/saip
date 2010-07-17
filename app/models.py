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
    """
    Representa una accion posible sobre una vista.
    
    """
    nombre = models.CharField(unique=True, max_length = 50)
    categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)
    
    def __unicode__(self):
        return self.nombre

class Rol(models.Model):
    """
    Representa un conjunto de permisos que definen las tareas realizables por el usuario que lo posea.
    
    """
    nombre = models.CharField(unique=True, max_length=50)
    categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)
    descripcion = models.TextField(null=True, blank=True)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    usuario_creador = models.ForeignKey(User, null=True)
    permisos = models.ManyToManyField(Permiso, through='RolPermiso')
    
    def __unicode__(self):
        return self.nombre

class Fase(models.Model):
    """
    Esta clase representa la fase en la que puede encontrarse un proyecto
    
    """
    nombre = models.CharField(unique=True, max_length=50)
    
    def __unicode__(self):
        return self.nombre
    
class RolPermiso(models.Model):
    """ 
    Tabla asociativa entre Permiso y Rol. El campo fase define (si el rol es de proyecto) en que fase del proyecto el permiso
    es valido.
    
    """
    rol = models.ForeignKey(Rol)
    permiso = models.ForeignKey(Permiso)
    fase = models.ForeignKey(Fase, null = True)

class Proyecto(models.Model):
    """
    Clase que representa un proyecto.
    
    """
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
    """
    Esta clase representa el tipo al que pertenece un artefacto.
    
    """
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    #claves foraneas
    fase = models.ForeignKey(Fase)
    proyecto = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.nombre

class TipoArtefactoFaseProyecto(models.Model):
    """
    Tabla que relaciona el tipo de artefacto a una fase por proyecto.
    
    """
    proyecto = models.ForeignKey(Proyecto)
    fase = models.ForeignKey(Fase)
    tipo_artefacto = models.ForeignKey(TipoArtefacto)
    cant = models.IntegerField(max_length = 4)
    
    def __unicode__(self):
        return self.tipo_artefacto.descripcion

    class Meta:
        unique_together = [("tipo_artefacto", "fase", "proyecto")]

class Artefacto(models.Model):
    """
    Clase que representa a los artefactos.
    
    """
    nombre = models.CharField(max_length=50)
    usuario = models.ForeignKey(User)
    fecha_creacion = models.DateField(auto_now_add=True, editable = False)
    estado = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=1)    
    version = models.PositiveIntegerField()
    complejidad = models.IntegerField(max_length=1, choices=COMPLEXITY_CHOICES)
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    habilitado = models.BooleanField(default=True)
    #claves foraneas
    proyecto = models.ForeignKey(Proyecto)
    tipo = models.ForeignKey(TipoArtefactoFaseProyecto)
    fase = models.ForeignKey(Fase)
    
    def __unicode__(self):
        return self.nombre

class RelArtefacto(models.Model):
    """
    Tabla asociativa que representa la relacion entre dos artefactos.
    
    """
    padre = models.ForeignKey(Artefacto, related_name = 'padre')
    hijo = models.ForeignKey(Artefacto, related_name = 'hijo')
    habilitado = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [("padre", "hijo")]

class Historial(models.Model):
    """
    Clase que representa el historial de los artefactos.
    
    """
    usuario = models.ForeignKey(User)
    fecha_creacion = models.DateField(auto_now =False, auto_now_add=True, editable=False)
    #claves foraneas
    artefacto = models.OneToOneField(Artefacto, parent_link=False)
    
class RegistroHistorial(models.Model):
    """
    Clase que representa el registro de una version anterior de un artefacto.
    
    """
    version = models.PositiveIntegerField()
    complejidad = models.IntegerField()
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    habilitado = models.BooleanField()
    tipo = models.ForeignKey(TipoArtefactoFaseProyecto)
    fecha_modificacion = models.DateTimeField(auto_now=True, auto_now_add=False, editable=False)
    #claves foraneas
    historial = models.ForeignKey(Historial)
   
    
class Adjunto(models.Model):
    """
    Almacena el contenido de un archivo adjunto a un artefacto y sus atributos.
    
    """
    nombre = models.CharField(max_length = 100)
    contenido = models.TextField(null=True)
    tamanho = models.IntegerField()
    mimetype = models.CharField(max_length = 255)  
    #claves foraneas
    artefacto = models.ForeignKey(Artefacto)
    habilitado = models.BooleanField(default = True)
    
class LineaBase(models.Model):
    """
    Almacena los datos de la generacion de una linea base.
    
    """
    fecha_creacion = models.DateField(auto_now=False, auto_now_add=True, editable=False)
    #relaciones con otras tablas
    proyectos = models.ForeignKey(Proyecto)
    fase = models.ForeignKey(Fase)


class UsuarioRolProyecto(models.Model):
    """
    Tabla asociativa que representa la relacion entre un usuario, su rol dentro de un proyecto y el proyecto mismo.
    
    """  
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol, null=True)
    proyecto = models.ForeignKey(Proyecto)

    class Meta:
        unique_together = [("usuario", "rol", "proyecto")]
        
class UsuarioRolSistema(models.Model):
    """
    Tabla asociativa que representa la relacion entre un usuario y un rol de sistema que posee.
    
    """
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol)
    
    class Meta:
        unique_together = [("usuario", "rol")]
        
class RegHistoRel(models.Model):
    """
    Clase que almacena las relaciones de una version anterior de un artefacto.
    
    """
    art_padre = models.ForeignKey(Artefacto, related_name = 'art_padre')
    art_hijo = models.ForeignKey(Artefacto, related_name = 'art_hijo')
    registro = models.ForeignKey(RegistroHistorial)
    
    class Meta:
        unique_together = [("art_padre", "art_hijo", "registro")]
        
class RegHistoAdj(models.Model):
    """
    Clase que almacena los archivos adjuntos de una version anterior de un artefacto.
    
    """
    #archivo = models.FileField(upload_to='artefactos')
    nombre = models.CharField(max_length = 100)
    contenido = models.TextField(null=True)
    tamanho = models.IntegerField()
    mimetype = models.CharField(max_length = 255)  
    #claves foraneas
    artefacto = models.ForeignKey(Artefacto)
    #habilitado = models.BooleanField(default = True)
    registro = models.ForeignKey(RegistroHistorial)

