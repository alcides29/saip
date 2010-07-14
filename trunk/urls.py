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
    (r'^changepass/$', cambiar_password),   
    (r'^lista/(?P<tipo>\w+)/$', lista),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
       {'document_root': os.path.abspath('site_media')}),
    
    # usuarios
    (r'^usuarios/$', admin_usuarios),
    (r'^usuarios/crear/$', add_user),
    (r'^usuarios/mod&id=(?P<usuario_id>\d+)/$', mod_user),
    (r'^usuarios/rol&id=(?P<usuario_id>\d+)/$', asignar_roles_sistema),
    (r'^usuarios/del&id=(?P<usuario_id>\d+)/$', borrar_usuario),
    
    # proyectos
	(r'^proyectos/$', admin_proyectos),
    (r'^proyectos/crear/$', crear_proyecto),
    (r'^proyectos/mod&id=(?P<proyecto_id>\d+)/$', mod_proyecto),
	(r'^proyectos/del&id=(?P<proyecto_id>\d+)/$', del_proyecto),
	(r'^proyectos/miembros&id=(?P<object_id>\d+)/$', admin_usuarios_proyecto),
	(r'^proyectos/miembros&id=(?P<object_id>\d+)/nuevo/$', add_usuario_proyecto),
    (r'^proyectos/miembros&id=(?P<proyecto_id>\d+)/cambiar&id=(?P<user_id>\d+)/$', cambiar_rol_usuario_proyecto),
    (r'^proyectos/miembros&id=(?P<proyecto_id>\d+)/del&id=(?P<user_id>\d+)/$', eliminar_miembro_proyecto),
    
    # gestion
    (r'^proyectos/lineabase&id=(?P<proyecto_id>\d+)/$', linea_base),
    (r'^proyectos/lineabase&id=(?P<proyecto_id>\d+)/revisar/$', linea_revisar),
    (r'^proyectos/lineabase&id=(?P<proyecto_id>\d+)/revisar&id=(?P<art_id>\d+)/$', linea_revisar_artefacto),
    (r'^proyectos/lineabase&id=(?P<proyecto_id>\d+)/relacionar/$', linea_relacionar),
    (r'^proyectos/lineabase&id=(?P<proyecto_id>\d+)/rel&id=(?P<art_id>\d+)&fase=(?P<fase>\d+)/$', linea_relacionar_artefacto),
    (r'^proyectos/lineabase&id=(?P<proyecto_id>\d+)/anteriores/$', linea_anteriores),
    
    # desarrollo
    (r'^proyectos/admin&id=(?P<proyecto_id>\d+)/$', administrar_proyecto),
    (r'^proyectos/tipoArtefacto&id=(?P<proyecto_id>\d+)/$', admin_tipo_artefacto_fase),
    (r'^proyectos/add_tipoArtefacto_fase&id=(?P<proyecto_id>\d+)/$', add_tipo_artefacto), #tipo de artefacto por proyecto
    (r'^proyectos/mod_tipoArtefacto_fase&id=(?P<proyecto_id>\d+)/(?P<tipo_art_id>\d+)/$', mod_tipo_artefacto_fase),
    (r'^proyectos/quitar_tipoArtefacto_fase&id=(?P<proyecto_id>\d+)/(?P<tipo_art_id>\d+)/$', quitar_tipo_artefacto_fase),
    
    # artefactos
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/$', admin_artefactos),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/crear/$', crear_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/mod&id=(?P<art_id>\d+)/$', modificar_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/del&id=(?P<art_id>\d+)/$', borrar_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/res/$', admin_artefactos_eliminados),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/res&id=(?P<art_id>\d+)/$', restaurar_artefacto_eliminado),
    
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/fasesAnt/$', fases_anteriores),    
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/revisar&id=(?P<art_id>\d+)/$', revisar_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/rel&id=(?P<art_id>\d+)&fase=(?P<fase>\d+)/$', definir_dependencias),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/verrel&id=(?P<art_id>\d+)&fase=(?P<fase>\d+)/$', ver_dependencias),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/imp&id=(?P<art_id>\d+)/$',calcular_impacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/adj&id=(?P<art_id>\d+)/$',admin_adjuntos),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/adjdel&id=(?P<art_id>\d+)/$',adjuntos_eliminados),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/adj&id=(?P<art_id>\d+)/nuevo/$',add_adjunto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/veradj&id=(?P<art_id>\d+)/$', ver_adjuntos),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/adj&id=(?P<art_id>\d+)/get&id=(?P<arch_id>\d+)/$',retornar_archivo),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/adj&id=(?P<art_id>\d+)/quitar&id=(?P<arch_id>\d+)/$',quitar_archivo),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/adj&id=(?P<art_id>\d+)/res&id=(?P<arch_id>\d+)/$',restaurar_archivo),
    
    # historial
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/historial&id=(?P<art_id>\d+)/$', ver_historial),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/historial&id=(?P<art_id>\d+)/historel&id=(?P<reg_id>\d+)&fase=(?P<fase>\d+)/$', historial_relaciones),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/historial&id=(?P<art_id>\d+)/volver&id=(?P<reg_id>\d+)/$', restaurar_artefacto),
    (r'^proyectos/artefactos&id=(?P<proyecto_id>\d+)/historial&id=(?P<art_id>\d+)/histoadj&id=(?P<reg_id>\d+)/$', historial_adjuntos),
    
    # roles
    (r'^roles/$', admin_roles),
    (r'^roles/sist/$',admin_roles_sist),
    (r'^roles/proy/$',admin_roles_proy),
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
