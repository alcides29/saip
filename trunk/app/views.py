from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from saip.app.forms import *
#from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

def principal(request):
    return render_to_response('main_page.html', RequestContext(request))

@login_required
def admin_usuarios_proyecto(request, object_id):
	user = User.objects.get(username=request.user.username)
	p = Proyecto.objects.get(pk = object_id)
	miembros = UsuarioRolProyecto.objects.filter(proyecto = p)
	print miembros
	if request.method == 'POST':
		#form = MiembrosProyectoForm(request.POST)
		if form.is_valid():
			pass
	else:
		#form = MiembrosProyectoForm()
		#form.usuario = miembros[0].usuario
		lista = []
		for i in miembros:
			nuevo = MiembrosProyectoForm(initial={'item':'rol2'})
			nuevo.usuario = i.usuario
			lista.append(nuevo)
		oform = ItemForm(miembros[0].usuario, initial={'item': '2'})
	return render_to_response('admin/proyectos/admin_miembros.html',{'otroform':oform, 'lista':lista, 'user':user, 'proyecto':Proyecto.objects.get(id=object_id)})
	'''p = Proyecto.objects.get(pk = object_id)
	miembros = UsuarioRolProyecto.objects.filter(proyecto = p)
	print miembros
	if request.method == 'POST':
		form = MiembrosProyectoForm(request.POST)
		if form.is_valid():
			for i in range(miembros.length):
				if(miembros[i].rol != form.cleaned_data['rol_miembros[i]']):
					miembros[i].rol = form.cleaned_data['rol_miembros[i]']
					miembros[i].save()
			return HttpResponseRedirect("/proyectos")
	else:
		form = MiembrosProyectoForm(miembros)
	return render_to_response('admin/proyectos/admin_miembros.html',{'form':form, 'user':user, 'proyecto':Proyecto.objects.get(id=object_id)})	'''
		
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
			return HttpResponseRedirect("/proyectos/")
	else:
		form = UsuarioProyectoForm()
	return render_to_response('admin/proyectos/add_miembro.html', {'form':form, 'user':user})

"""Agrega un nuevo usuario"""
@login_required
def add_user(request):
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
	return render_to_response('admin/usuario

def lista(request, tipo):
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
	user = User.objects.get(username=request.user.username)
	lista = User.objects.all()
	return render_to_response('admin/usuarios/usuarios.html',{'lista':lista, 'user':user})

@login_required
def admin_proyectos(request):
	user = User.objects.get(username=request.user.username)
	lista = Proyecto.objects.all()
	return render_to_response('admin/proyectos/proyectos.html',{'lista':lista, 'user':user})	

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
	return render_to_response('operacion_exitosa.html');

def logout_pagina(request):
    logout(request)
    return render_to_response('logout.html')

def login_redirect(request):
	return HttpResponseRedirect('/login')