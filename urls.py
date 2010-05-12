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
    
    # usuarios
	(r'^usuarios/$', admin_usuarios),
    (r'^usuarios/crear/$', create_object, {'form_class':UsuariosForm,'template_name':'admin/usuarios/abm_usuario.html', 'post_save_redirect':'/usuarios', 'login_required':True}),
    (r'^usuarios/mod/(?P<object_id>\d+)/$', update_object, {'form_class':UsuariosForm, 'template_name':'admin/usuarios/abm_usuario.html', 'post_save_redirect':'/usuarios', 'login_required':True}),
	(r'^usuarios/del/(?P<object_id>\d+)/$', delete_object, {'model':User, 'template_name':'admin/usuarios/user_confirm_delete.html', 'post_delete_redirect':'/usuarios', 'login_required':True}),
    
    # proyectos
	(r'^proyectos/$', admin_proyectos),
    (r'^proyectos/crear/$', create_object, {'form_class': ProyectosForm, 'template_name':'admin/proyectos/abm_proyecto.html', 'post_save_redirect':'/proyectos', 'login_required':True}),
	(r'^proyectos/mod/(?P<object_id>\d+)/$', update_object, {'form_class':ProyectosForm, 'template_name':'admin/proyectos/abm_proyecto.html', 'post_save_redirect':'/proyectos', 'login_required':True}),
	(r'^proyectos/del/(?P<object_id>\d+)/$', delete_object, {'model':Proyecto, 'template_name':'admin/proyectos/proyecto_confirm_delete.html', 'post_delete_redirect':'/proyectos', 'login_required':True}),
    
    # Tipo de artefacto
    (r'^tipo_artefacto/$', admin_tipo_artefacto),
    (r'^tipo_artefacto/crear/$', create_object, {'form_class': TipoArtefactoForm, 'template_name':'proyecto/artefacto/abm_tipo_artefacto.html', 'post_save_redirect':'/tipo_artefacto', 'login_required':True}),
    (r'^tipo_artefacto/mod/(?P<object_id>\d+)/$', update_object, {'form_class':TipoArtefactoForm, 'template_name':'proyecto/artefacto/abm_tipo_artefacto.html', 'post_save_redirect':'/tipo_artefacto', 'login_required':True}),
    (r'^tipo_artefacto/del/(?P<object_id>\d+)/$', delete_object, {'model':TipoArtefacto, 'template_name':'proyecto/artefacto/tipo_artefacto_confirm_delete.html', 'post_delete_redirect':'/tipo_artefacto', 'login_required':True}),
    
    
    
    (r'^terminar/$', terminar),
    (r'^logout/$', logout_pagina),
    
    (r'^lista/(?P<tipo>\w+)/$', lista),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
       {'document_root': os.path.abspath('site_media')}),
)
