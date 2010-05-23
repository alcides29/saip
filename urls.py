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
	(r'^proyectos/mod&id=(?P<object_id>\d+)/$', update_object, {'form_class':ModProyectosForm, 'template_name':'admin/proyectos/abm_proyecto.html', 'post_save_redirect':'/proyectos', 'login_required':True}),
	(r'^proyectos/del&id=(?P<object_id>\d+)/$', delete_object, {'model':Proyecto, 'template_name':'admin/proyectos/proyecto_confirm_delete.html', 'post_delete_redirect':'/proyectos', 'login_required':True}),
	(r'^proyectos/miembros&id=(?P<object_id>\d+)/$', admin_usuarios_proyecto),
	(r'^proyectos/miembros&id=(?P<object_id>\d+)/nuevo/$', add_usuario_proyecto),
    (r'^proyectos/miembros&id=(?P<proyecto_id>\d+)/cambiar&id=(?P<user_id>\d+)/$', cambiar_rol_usuario_proyecto),
    (r'^proyectos/miembros&id=(?P<proyecto_id>\d+)/del&id=(?P<user_id>\d+)/$', eliminar_miembro_proyecto),
    
    #artefactos
    (r'^proyectos/artefactos/(?P<proyecto_id>\d+)/$', admin_artefactos),
    (r'^proyectos/artefactos/(?P<proyecto_id>\d+)/crear/$', crear_artefacto),
    (r'^proyectos/artefactos/(?P<proyecto_id>\d+)/mod/(?P<art_id>\d+)/$', modificar_artefacto),
    (r'^proyectos/artefactos/(?P<proyecto_id>\d+)/del/(?P<art_id>\d+)/$', borrar_artefacto),
    
    #historial
    (r'^proyectos/artefactos/(?P<proyecto_id>\d+)/historial/(?P<art_id>\d+)/$', ver_historial),
    (r'^proyectos/artefactos/(?P<proyecto_id>\d+)/historial/(?P<art_id>\d+)/volver/(?P<reg_id>\d+)/$', restaurar_artefacto),
    
    #roles
    (r'^roles/$', admin_roles),
    (r'^roles/crear/$', crear_rol),
    (r'^roles/mod&id=(?P<rol_id>\d+)/$', mod_rol),
    (r'^roles/permisos&id=(?P<rol_id>\d+)/$', admin_permisos),
    (r'^roles/del&id=(?P<rol_id>\d+)/$', borrar_rol),
    
    # Tipo de artefacto
    (r'^tipo_artefacto/$', admin_tipo_artefacto),
    (r'^tipo_artefacto/crear/$', create_object, {'form_class': TipoArtefactoForm, 'template_name':'admin/tipo_artefacto/abm_tipo_artefacto.html', 'post_save_redirect':'/tipo_artefacto', 'login_required':True}),
    (r'^tipo_artefacto/mod&id=(?P<object_id>\d+)/$', update_object, {'form_class':TipoArtefactoForm, 'template_name':'admin/tipo_artefacto/abm_tipo_artefacto.html', 'post_save_redirect':'/tipo_artefacto', 'login_required':True}),
    (r'^tipo_artefacto/del&id=(?P<tipo_id>\d+)/$', borrar_tipo_artefacto),

           
    
)
