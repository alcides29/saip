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

# Administracion de tipo de artefactos
@login_required
def admin_tipo_artefacto(request):
    user = User.objects.get(username=request.user.username)
    lista = TipoArtefacto.objects.all()
    return render_to_response('proyecto/artefacto/tipo_artefacto.html', {'lista': lista, 'user':user})
'''
def tipo_artefacto(request):
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = TipoArtefactoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/terminar')
    else:
        form = ProyectosForm()
    return render_to_response('proyecto/artefacto/abm_tipo_artefacto.html',{'form':form, 'user':user})
'''

@login_required
def terminar(peticion):
	return render_to_response('operacion_exitosa.html');

def logout_pagina(request):
    logout(request)
    return render_to_response('logout.html')

def login_redirect(request):
	return HttpResponseRedirect('/login')
