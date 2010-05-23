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
    (r'^usuarios/mod/(?P<object_id>\d+)/$', update_object, {'form_class':ModUsuariosForm, 'template_name':'admin/usuarios/abm_usuario.html', 'post_save_redirect': '/usuarios', 'login_required':True}),
	(r'^usuarios/del/(?P<object_id>\d+)/$', delete_object, {'model':User, 'template_name':'admin/usuarios/user_confirm_delete.html', 'post_delete_redirect':'/usuarios', 'login_required':True}),
    
    # proyectos
	(r'^proyectos/$', admin_proyectos),
    (r'^proyectos/crear/$', crear_proyecto),
	(r'^proyectos/mod/(?P<object_id>\d+)/$', update_object, {'form_class':ModProyectosForm, 'template_name':'admin/proyectos/abm_proyecto.html', 'post_save_redirect':'/proyectos', 'login_required':True}),
	(r'^proyectos/del/(?P<object_id>\d+)/$', delete_object, {'model':Proyecto, 'template_name':'admin/proyectos/proyecto_confirm_delete.html', 'post_delete_redirect':'/proyectos', 'login_required':True}),
	(r'^proyectos/miembros/(?P<object_id>\d+)/$', admin_usuarios_proyecto),
	(r'^proyectos/miembros/(?P<object_id>\d+)/nuevo/$', add_usuario_proyecto),
    (r'^proyectos/miembros/(?P<proyecto_id>\d+)/cambiar/(?P<user_id>\d+)/$', cambiar_rol_usuario_proyecto),
    
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
    (r'^roles/crearp/$', crear_rol_proyecto),
    (r'^roles/crears/$', crear_rol_sistema),
    (r'^roles/mod/(?P<object_id>\d+)/$', update_object, {'form_class':ModRolesForm, 'template_name':'admin/roles/abm_rol.html', 'post_save_redirect':'/roles', 'login_required':True}),
    (r'^roles/del/(?P<object_id>\d+)/$', delete_object, {'model':Rol, 'template_name':'admin/roles/rol_confirm_delete.html', 'post_delete_redirect':'/roles', 'login_required':True}),
    
    # Tipo de artefacto
    (r'^tipo_artefacto/$', admin_tipo_artefacto),
    (r'^tipo_artefacto/crear/$', create_object, {'form_class': TipoArtefactoForm, 'template_name':'admin/tipo_artefacto/abm_tipo_artefacto.html', 'post_save_redirect':'/tipo_artefacto', 'login_required':True}),
    (r'^tipo_artefacto/mod/(?P<object_id>\d+)/$', update_object, {'form_class':TipoArtefactoForm, 'template_name':'admin/tipo_artefacto/abm_tipo_artefacto.html', 'post_save_redirect':'/tipo_artefacto', 'login_required':True}),
    (r'^tipo_artefacto/del/(?P<object_id>\d+)/$', delete_object, {'model':TipoArtefacto, 'template_name':'admin/tipo_artefacto/tipo_artefacto_confirm_delete.html', 'post_delete_redirect':'/tipo_artefacto', 'login_required':True}),

           
    
)
