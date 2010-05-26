# -*- coding: iso-8859-15 -*-
from django.conf.urls.defaults import *
from django.views.generic.create_update import *
from django.contrib.auth.models import User

import os.path

from saip.app.forms import *
from saip.app.models import *
from saip.app.views import *

urlpatterns = patterns('',
    # Example:
    # (r'^saip/', include('saip.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^$', principal),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/login/$', login_redirect),
    (r'^terminar/$', terminar),
    (r'^logout/$', logout_pagina),    
    (r'^lista/(?P<tipo>\w+)/$', lista),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
       {'document_root': os.path.abspath('site_media')}),
    
    # usuarios
    (r'^usuarios/$', admin_usuarios),
    (r'^usuarios/crear/$', add_user),
    (r'^usuarios/mod&id=(?P<usuario_id>\d+)/$', mod_user),
    (r'^usuarios/pass&id=(?P<usuario_id>\d+)/$', cambiar_password),
    (r'^usuarios/rol&id=(?P<usuario_id>\d+)/$', asignar_roles_sistema),
    (r'^usuarios/del&id=(?P<usuario_id>\d+)/$', borrar_usuario),
    
    # proyectos
	(r'^proyectos/$', admin_proyectos),
    (r'^proyectos/crear/$', crear_proyecto),
    (r'^proyectos/mod&id=(?P<proyecto_id>\d+)/$', mod_proyecto),
	#(r'^proyectos/mod&id=(?P<object_id>\d+)/$', update_object, {'form_class':ModProyectosForm, 'template_name':'admin/proyectos/abm_proyecto.html', 'post_save_redirect':'/proyectos', 'login_required':True}),
	(r'^proyectos/del&id=(?P<proyecto_id>\d+)/$', del_proyecto),
	(r'^proyectos/miembros&id=(?P<object_id>\d+)/$', admin_usuarios_proyecto),
	(r'^proyectos/miembros&id=(?P<object_id>\d+)/nuevo/$', add_usuario_proyecto),
    (r'^proyectos/miembros&id=(?P<proyecto_id>\d+)/cambiar&id=(?P<user_id>\d+)/$', cambiar_rol_usuario_proyecto),
    (r'^proyectos/miembros&id=(?P<proyecto_id>\d+)/del&id=(?P<user_id>\d+)/$', eliminar_miembro_proyecto),
    
    #desarrollo
    (r'^proyectos/admin&id=(?P<proyecto_id>\d+)/$', administrar_proyecto),
    
    #artefactos
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/$', admin_artefactos),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/crear/$', crear_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/mod&id=(?P<art_id>\d+)/$', modificar_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/del&id=(?P<art_id>\d+)/$', borrar_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/res/$', admin_artefactos_eliminados),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/res&id=(?P<art_id>\d+)/$', restaurar_artefacto_eliminado),
    
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/fasesAnt/$', fases_anteriores),
    
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/revisar&id=(?P<art_id>\d+)/$', revisar_artefacto),
    
    #historial
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/historial&id=(?P<art_id>\d+)/$', ver_historial),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/historial&id=(?P<art_id>\d+)/volver&id=(?P<reg_id>\d+)/$', restaurar_artefacto),
    
    #roles
    (r'^roles/$', admin_roles),
    (r'^roles/crear/$', crear_rol),
    (r'^roles/mod&id=(?P<rol_id>\d+)/$', mod_rol),
    (r'^roles/permisos&id=(?P<rol_id>\d+)/$', admin_permisos),
    (r'^roles/del&id=(?P<rol_id>\d+)/$', borrar_rol),
    
    # Tipo de artefacto
    (r'^tipo_artefacto/$', admin_tipo_artefacto),
    (r'^tipo_artefacto/crear/$', crear_tipo_artefacto),
    (r'^tipo_artefacto/mod&id=(?P<tipo_id>\d+)/$', mod_tipo_artefacto),
    (r'^tipo_artefacto/del&id=(?P<tipo_id>\d+)/$', borrar_tipo_artefacto),

           
    
)
