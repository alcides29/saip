# -*- coding: iso-8859-15 -*-
import hashlib

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth import logout
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory

from saip.app.forms import *
from saip.app.models import *

def principal(request):
    """Muestra la pagina principal."""
    return render_to_response('main_page.html', RequestContext(request))

@login_required
def admin_usuarios_proyecto(request, object_id):
    user = User.objects.get(username=request.user.username)
    p = Proyecto.objects.get(pk = object_id)
    miembros = UsuarioRolProyecto.objects.filter(proyecto = p)
    return render_to_response('admin/proyectos/admin_miembros.html',{'user':user, 'proyecto':Proyecto.objects.get(id=object_id), 'miembros': miembros})
	
@login_required
def cambiar_rol_usuario_proyecto(request, proyecto_id, user_id):
    user = User.objects.get(username=request.user.username)
    p = Proyecto.objects.get(pk = proyecto_id)
    u = User.objects.get(pk = user_id)
    lista = UsuarioRolProyecto.objects.filter(proyecto = p, usuario = u)
    item = lista[0]
    if request.method == 'POST':
        form = ItemForm(item.usuario, request.POST)
        if form.is_valid():
            if (form.cleaned_data['item'] != item.rol):
                item.rol = form.cleaned_data['item']
                item.save()
            return HttpResponseRedirect("/proyectos/miembros/" + str(proyecto_id))
    else:
        form = ItemForm(item.usuario, initial = {'item':item.rol._get_pk_val()})
    return render_to_response("admin/proyectos/cambiar_usuario_rol.html", {'user': user, 'form':form, 'usuario':u, 'proyecto': p})
	
@login_required
def add_usuario_proyecto(request, object_id):
	user = User.objects.get(username=request.user.username)
	if request.method == 'POST':
		form = UsuarioProyectoForm(request.POST)
		if form.is_valid():
			relacion = UsuarioRolProyecto()
			relacion.usuario = form.cleaned_data['usuario']
			relacion.proyecto = Proyecto.objects.get(pk = object_id)
			relacion.rol = form.cleaned_data['rol']
			relacion.save()
			return HttpResponseRedirect("/proyectos/miembros/" + str(object_id))
	else:
		form = UsuarioProyectoForm()
	return render_to_response('admin/proyectos/add_miembro.html', {'form':form, 'user':user,  'proyecto': Proyecto.objects.get(pk=object_id)})

@login_required
def add_user(request):
    """Agrega un nuevo usuario."""
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = UsuariosForm(request.POST)
        if form.is_valid():
            nuevo = User()
            nuevo.username = form.cleaned_data['username']
            nuevo.first_name = form.cleaned_data['first_name']
            nuevo.last_name = form.cleaned_data['last_name']
            nuevo.email = form.cleaned_data['email']
            nuevo.set_password(form.cleaned_data['password'])
            nuevo.is_staff = True
            nuevo.is_active = True
            nuevo.is_superuser = True #no se si esta bien este
            nuevo.last_login = datetime.datetime.now()
            nuevo.date_joined = datetime.datetime.now()
            nuevo.save()
            return HttpResponseRedirect("/usuarios")
    else:
        form = UsuariosForm()
    return render_to_response('admin/usuarios/abm_usuario.html',{'form':form, 'user':user})

def lista(request, tipo):
    """Metodo de prueba para listar items"""
    user = User.objects.get(username=request.user.username)
    if tipo == 'usuarios':
        lista = User.objects.all()
    elif tipo == 'proyectos':
        lista = Proyecto.objects.all()
    elif tipo == 'tipo_artefactos':    
        lista = TipoArtefactos.objects.all()
    else:
		return render_to_response('error.html');
    return render_to_response('lista.html',{'lista':lista, 'user':user, 'tipo':tipo})

@login_required
def admin_usuarios(request):
    """Administracion general de usuarios"""
    user = User.objects.get(username=request.user.username)
    lista = User.objects.all()
    return render_to_response('admin/usuarios/usuarios.html',{'lista':lista, 'user':user})

@login_required
def admin_proyectos(request):
    """Administracion general de proyectos"""
    user = User.objects.get(username=request.user.username)
    lista = Proyecto.objects.all()
    return render_to_response('admin/proyectos/proyectos.html',{'lista':lista, 'user':user})	

@login_required
def admin_roles(request):
    """Administracion general de roles"""
    user = User.objects.get(username=request.user.username)
    lista1 = RolSistema.objects.all()
    lista2 = RolProyecto.objects.all()
    return render_to_response('admin/roles/roles.html',{'lista1':lista1, 'lista2':lista2, 'user':user})

@login_required
def crear_rol(request):
    """Agrega un nuevo rol."""
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = ElegirRolForm(request.POST)
        if form.is_valid():
            res = form.cleaned_data['categoria']
            if res == '1':
                return HttpResponseRedirect("/roles/crears")
            elif res == '2':
                return HttpResponseRedirect("/roles/crearp")
    else:
        form = ElegirRolForm()
    return render_to_response('admin/roles/crear_rol.html',{'form':form, 'user':user})

@login_required
def crear_rol_sistema(request):
    """Agrega un nuevo rol."""
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = RolesForm(request.POST)
        if form.is_valid():
            r = RolSistema()
            r.nombre = form.cleaned_data['nombre']
            r.descripcion = form.cleaned_data['descripcion']
            r.fecHor_creacion = datetime.datetime.now()
            r.usuario_creador = user
            r.save()
            return HttpResponseRedirect('/roles')
    else:
        form = RolesForm()
    return render_to_response('admin/roles/abm_rol.html',{'form':form, 'user':user})

@login_required
def crear_rol_proyecto(request):
    """Agrega un nuevo rol."""
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = RolesForm(request.POST)
        if form.is_valid():
            r = RolProyecto()
            r.nombre = form.cleaned_data['nombre']
            r.descripcion = form.cleaned_data['descripcion']
            r.fecHor_creacion = datetime.datetime.now()
            r.usuario_creador = user
            r.save()
            return HttpResponseRedirect('/roles')
    else:
        form = RolesForm()
    return render_to_response('admin/roles/abm_rol.html',{'form':form, 'user':user})

@login_required
def proyectos(request):
	user = User.objects.get(username=request.user.username)
	if request.method == 'POST':
		form = ProyectosForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/terminar')
	else:
		form = ProyectosForm()
	return render_to_response('admin/proyectos/abm_proyecto.html',{'form':form, 'user':user})

@login_required
def admin_tipo_artefacto(request):
    """Muestra la página de administracion de tipo de artefactos."""
    user = User.objects.get(username=request.user.username)
    lista = TipoArtefacto.objects.all()
    return render_to_response('admin/tipo_artefacto/tipo_artefacto.html',
                              {'lista': lista, 'user':user})

@login_required
def terminar(peticion):
    """Muestra una pagina de confirmacion de exito"""
    return render_to_response('operacion_exitosa.html');

def logout_pagina(request):
    """Pagina de logout"""
    logout(request)
    return render_to_response('logout.html')

#desde aqui artefacto
def admin_artefactos(request):
    """Muestra la página de administracion de artefactos."""
    user = User.objects.get(username=request.user.username)
    lista = Artefacto.objects.all()
    return render_to_response('desarrollo/artefacto/artefactos.html',{'lista':lista})
    
def crear_artefacto(request):
    """Crear un artefacto"""
    user = User.objects.get(username=request.user.username)
    if (request.POST):
        form = ArtefactoForm(request.POST)
        if form.is_valid():
            art = Artefacto()
            art.nombre = form.cleaned_data['nombre']
            art.usuario = user
            art.estado = 1
            art.fecha_creacion = datetime.date.today()
            art.version = 1
            art.complejidad = form.cleaned_data['complejidad']
            art.descripcion_corta = form.cleaned_data['descripcion_corta']
            art.descripcion_larga = form.cleaned_data['descripcion_larga']
            art.habilitado = True
            art.icono = form.cleaned_data['icono']
            #art.relacionados = form.cleaned_data['relacionados']
            art.proyecto = form.cleaned_data['proyecto']
            art.tipo = form.cleaned_data['tipo']            
            art.save()
            return HttpResponseRedirect('/artefactos')
    else:
        form = ArtefactoForm()
    variables = RequestContext(request, {
                                        'form': form,
                                        })                
    return render_to_response('desarrollo/artefacto/crear_artefacto.html', variables)


def modificar_artefacto(request, id_art):
    """Modificar un artefacto"""
    if (request.POST):
        art = Artefacto.objects.get(pk=id_art)
        form = ModArtefactoForm(request.POST)
        if (form.is_valid()):
            #realizar una copia del artefacto antiguo e ir comparando
            art.nombre = form.cleaned_data['nombre']
            art.version = art.version + 1 #comprobar si hubo cambio
            art.complejidad = form.cleaned_data['complejidad']
            art.descripcion_corta = form.cleaned_data['descripcion_corta']
            art.descripcion_larga = form.cleaned_data['descripcion_larga']
            art.estado = 2
            art.habilitado = form.cleaned_data['habilitado']
            art.icono = form.cleaned_data['icono']
            #art.relacionados = form.cleaned_data['relacionados']
            art.proyecto = form.cleaned_data['proyecto']#no tiene que estar
            art.tipo = form.cleaned_data['tipo']
            art.save()
            return HttpResponseRedirect('/artefactos')
    else:
        #nombre_art = request.GET['nombre']
        art = get_object_or_404(Artefacto, id=id_art)
        form = ModArtefactoForm({
                        'nombre': art.nombre,
                        'complejidad': art.complejidad,
                        'descripcion_corta':art.descripcion_corta,
                        'descripcion_larga':art.descripcion_larga,
                        'habilitado':art.habilitado,
                        'icono':art.icono,
                        'proyecto':art.proyecto,#ojo
                        'tipo':art.tipo,
                       })      
    variables = RequestContext(request, {'form':form,
                                         'art':art,
                                         })          
    return render_to_response('desarrollo/artefacto/mod_artefacto.html', variables)

def borrar_artefacto(request, id_art):
    """Dar de baja un artefacto"""
    art = get_object_or_404(Artefacto, id=id_art)
    if (request.POST):
        art.habilitado= False
        art.save()
        return HttpResponseRedirect('/artefactos')
    variables = RequestContext(request, {'art': art,
                                        })
    return render_to_response('desarrollo/artefacto/artefacto_confirm_delete.html', variables)


def login_redirect(request):
    """Redirige de /accounts/login a /login."""
    return HttpResponseRedirect('/login')
