# -*- coding: iso-8859-15 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth import logout
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response

from django.shortcuts import get_object_or_404

from saip.app.forms import *
from saip.app.models import *
from saip.app.helper import *

@login_required
def principal(request):
    """Muestra la pagina principal."""
    user = User.objects.get(username=request.user.username)
     #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos_sistema = []
    for item in permisos_obj:
        permisos_sistema.append(item.nombre)
    variables ={}
    for item in permisos_sistema:
        if item == 'Ver roles' or item == 'Crear rol' or item == 'Modificar rol' or item == 'Eliminar rol' or item == 'Asignar rol':
            variables['roles'] = True 
        if item == 'Ver proyectos' or item == 'Crear proyecto' or item == 'Modificar proyecto' or item == 'Eliminar proyecto':
            variables['proyectos'] = True
        if item == 'Ver usuarios' or item == 'Crear usuario' or item == 'Modificar usuario' or item == 'Eliminar usuario':
            variables['usuarios'] = True
        if item == 'Ver tipos-artefacto' or item == 'Crear tipo-artefacto' or item == 'Modificar tipo-artefacto' or item == 'Eliminar tipo-artefacto':
            variables['tipos_artefacto'] = True
    roles = UsuarioRolProyecto.objects.filter(usuario = user).only('rol')
    lista_proyectos = []
    for item in roles:
        lista_proyectos.append(item.proyecto.id)
    print lista_proyectos
    variables['permisos_proyecto'] = lista_proyectos
    #-------------------------------------------------------------------
    lista = Proyecto.objects.all()
    #print lista
    variables['user'] = user
    variables['lista'] = lista
    print variables
    return render_to_response('main_page.html', variables)
    #return render_to_response('main_page.html', RequestContext(request))

@login_required
def administrar_proyecto(request, proyecto_id):
    user = User.objects.get(username=request.user.username)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    return render_to_response("desarrollo/admin_proyecto.html", {'proyecto':proyecto, 
                                                                 'user':user,
                                                                 'ver_artefactos': 'Ver artefactos' in permisos,
                                                                 'abm_artefactos': 'ABM artefactos' in permisos,
                                                                 'ver_miembros': 'Ver miembros' in permisos,
                                                                 'abm_miembros': 'ABM miembros' in permisos,
                                                                 'asignar_roles': 'Asignar roles' in permisos,
                                                                 'generarlb':'Generar LB' in permisos})
    
@login_required
def admin_usuarios_proyecto(request, object_id):
    user = User.objects.get(username=request.user.username)
    p = Proyecto.objects.get(pk = object_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = p).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    miembros = UsuarioRolProyecto.objects.filter(proyecto = p).order_by('id')
    lista = []
    for item in miembros:
        if not item.usuario in lista:
            lista.append(item.usuario)
    return render_to_response('desarrollo/admin_miembros.html',{'user':user, 
                                                                'proyecto':Proyecto.objects.get(id=object_id), 
                                                                'miembros': lista,
                                                                'ver_miembros': 'Ver miembros' in permisos,
                                                                'abm_miembros': 'ABM miembros' in permisos})
	
@login_required
def cambiar_rol_usuario_proyecto(request, proyecto_id, user_id):
    user = User.objects.get(username=request.user.username)
    p = Proyecto.objects.get(pk = proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = p).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    u = User.objects.get(pk = user_id)
    lista = UsuarioRolProyecto.objects.filter(proyecto = p, usuario = u)
    if request.method == 'POST':
        form = ItemForm(u, request.POST)
        if form.is_valid():
            for item in lista:
                item.delete()
            lista_nueva = form.cleaned_data['items']
            if lista_nueva:
                for item in lista_nueva:
                    nuevo = UsuarioRolProyecto()
                    nuevo.usuario = u
                    nuevo.proyecto = p
                    nuevo.rol = item
                    nuevo.save()
            else:
                nuevo = UsuarioRolProyecto()
                nuevo.usuario = u
                nuevo.proyecto = p
                nuevo.rol = None
                nuevo.save()
            return HttpResponseRedirect("/proyectos/miembros&id=" + str(proyecto_id))
    else:
        if len(lista) == 1 and not lista[0].rol:
            form = ItemForm(u)
        else:
            dict = {}
            for item in lista:
                dict[item.rol.id] = True
            form = ItemForm(u, initial = {'items':dict})
    return render_to_response("desarrollo/cambiar_usuario_rol.html", {'user': user, 
                                                                      'form':form, 
                                                                      'usuario':u, 
                                                                      'proyecto': p,
                                                                      'abm_miembros':'ABM miembros' in permisos})
	
@login_required
def add_usuario_proyecto(request, object_id):
    user = User.objects.get(username=request.user.username)
    p = get_object_or_404(Proyecto, id = object_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = p).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = UsuarioProyectoForm(request.POST)
        if form.is_valid():
            roles = form.cleaned_data['roles']
            if not roles:
                relacion = UsuarioRolProyecto()
                relacion.usuario = form.cleaned_data['usuario']
                relacion.proyecto = p
                relacion.rol = None
                relacion.save()
            else:
                for item in roles:
                    relacion = UsuarioRolProyecto()
                    relacion.usuario = form.cleaned_data['usuario']
                    relacion.proyecto = Proyecto.objects.get(pk = object_id)
                    relacion.rol = item
                    relacion.save()
            return HttpResponseRedirect("/proyectos/miembros&id=" + str(object_id))
    else:
        form = UsuarioProyectoForm()
    return render_to_response('desarrollo/add_miembro.html', {'form':form, 
                                                              'user':user,  
                                                              'proyecto': p,
                                                              'abm_miembros': 'ABM miembros' in permisos})

@login_required
def eliminar_miembro_proyecto(request, proyecto_id, user_id):
    user = User.objects.get(username=request.user.username)
    usuario = get_object_or_404(User, pk=user_id)
    proy = get_object_or_404(Proyecto, pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proy).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        lista = UsuarioRolProyecto.objects.filter(proyecto = proy, usuario = usuario)
        for item in lista:
            item.delete()
        return HttpResponseRedirect("/proyectos/miembros&id=" + str(proyecto_id))
    else:
        return render_to_response("desarrollo/eliminar_miembro.html", {'usuario':usuario, 
                                                                       'proyecto':proy, 
                                                                       'user':user,
                                                                       'abm_miembros': 'ABM miembros' in permisos})

@login_required
def add_user(request):
    """Agrega un nuevo usuario."""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos----------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    #--------------------------------------------------------------------
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
    return render_to_response('admin/usuarios/crear_usuario.html',{'form':form, 
                                                                 'user':user, 
                                                                 'crear_usuario': 'Crear usuario' in permisos})

@login_required
def mod_user(request, usuario_id):
    """Modifica los datos de un usuario."""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos----------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    #--------------------------------------------------------------------
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        form = ModUsuariosForm(request.POST)
        if form.is_valid():
            usuario.first_name = form.cleaned_data['first_name']
            usuario.last_name = form.cleaned_data['last_name']
            usuario.email = form.cleaned_data['email']
            return HttpResponseRedirect("/usuarios")
    else:
        form = ModUsuariosForm(initial={'first_name':usuario.first_name, 'last_name': usuario.last_name,'email':usuario.email})
    return render_to_response('admin/usuarios/mod_usuario.html',{'form':form, 
                                                                 'user':user, 
                                                                 'usuario':usuario, 
                                                                 'mod_usuario': 'Modificar usuario' in permisos})

@login_required
def cambiar_password(request):
    """Cambia la contrasena del usuario logueado"""
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return HttpResponseRedirect("/usuarios")
    else:
        form = CambiarPasswordForm()
    return render_to_response("cambiar_password.html", {'form': form, 'user': user})

@login_required
def asignar_roles_sistema(request, usuario_id):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos----------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #--------------------------------------------------------------------
    usuario = get_object_or_404(User, id=usuario_id)
    lista_roles = UsuarioRolSistema.objects.filter(usuario = usuario)
    print lista_roles
    if request.method == 'POST':
        form = AsignarRolesForm(1, request.POST)
        if form.is_valid():
            lista_nueva = form.cleaned_data['roles']
            for item in lista_roles:
                item.delete()
            for item in lista_nueva:
                nuevo = UsuarioRolSistema()
                nuevo.usuario = usuario
                nuevo.rol = item
                nuevo.save()
            return HttpResponseRedirect("/usuarios")
    else:
        if usuario.id == 1:
            error = "No se puede editar roles sobre el superusuario."
            return render_to_response("admin/usuarios/asignar_roles.html", {'mensaje': error,
                                                                            'usuario':usuario, 
                                                                            'user': user, 
                                                                            'asignar_roles': 'Asignar rol' in permisos})
        dict = {}
        for item in lista_roles:
            print item.rol
            dict[item.rol.id] = True
        form = AsignarRolesForm(1,initial = {'roles': dict})
    return render_to_response("admin/usuarios/asignar_roles.html", {'form':form, 'usuario':usuario, 'user':user, 'asignar_roles': 'Asignar rol' in permisos})

@login_required
def borrar_usuario(request, usuario_id):
    """Borra un usuario, comprobando las dependencias primero"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos----------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    #--------------------------------------------------------------------
    usuario = get_object_or_404(User, id=usuario_id)
    comprometido = 0
    #comprobar si el usuario esta asociado a algun proyecto como lider
    comprometido = Proyecto.objects.filter(usuario_lider = usuario).count()
    if request.method == 'POST':
        usuario.delete()
        return HttpResponseRedirect("/usuarios")
    else:
        if usuario.id == 1:
            error = "No se puede borrar al superusuario."
            return render_to_response("admin/usuarios/user_confirm_delete.html", {'mensaje': error,'usuario':usuario, 'user': user})
        elif comprometido > 0:
            error = "El usuario esta asociado a un proyecto como lider."
            return render_to_response("admin/usuarios/user_confirm_delete.html", {'mensaje': error,'usuario':usuario, 'user': user})
    return render_to_response("admin/usuarios/user_confirm_delete.html", {'usuario':usuario, 
                                                                          'user':user,
                                                                          'eliminar_usuario': 'Eliminar usuario' in permisos})
            
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
    '''Ya esta la validacion de permisos en este'''
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    lista = User.objects.all()
    return render_to_response('admin/usuarios/usuarios.html',{'lista':lista,
                                                               'user':user, 
                                                               'ver_usuarios': 'Ver usuarios' in permisos,
                                                               'crear_usuario': 'Crear usuario' in permisos,
                                                               'mod_usuario': 'Modificar usuario' in permisos,
                                                               'eliminar_usuario': 'Eliminar usuario' in permisos,
                                                               'asignar_roles': 'Asignar rol' in permisos})

@login_required
def admin_proyectos(request):
    """Administracion general de proyectos"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    lista = Proyecto.objects.all().order_by('id')
    return render_to_response('admin/proyectos/proyectos.html',{'lista':lista, 
                                                                'user':user,
                                                                'ver_proyectos':'Ver proyectos' in permisos,
                                                                'crear_proyecto': 'Crear proyecto' in permisos,
                                                                'mod_proyecto': 'Modificar proyecto' in permisos,
                                                                'eliminar_proyecto': 'Eliminar proyecto' in permisos})	

@login_required
def admin_roles(request):
    """Administracion general de roles"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    lista1 = Rol.objects.filter(categoria=1).order_by('id')
    lista2 = Rol.objects.filter(categoria=2).order_by('id')
    return render_to_response('admin/roles/roles.html',{'lista1':lista1,
                                                        'lista2':lista2,
                                                        'user':user,
                                                        'ver_roles':'Ver roles' in permisos,
                                                        'crear_rol': 'Crear rol' in permisos,
                                                        'mod_rol': 'Modificar rol' in permisos,
                                                        'eliminar_rol': 'Eliminar rol' in permisos})

@login_required
def crear_rol(request):
    """Agrega un nuevo rol."""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = RolesForm(request.POST)
        if form.is_valid():
            r = Rol()
            r.nombre = form.cleaned_data['nombre']
            r.descripcion = form.cleaned_data['descripcion']
            r.fecHor_creacion = datetime.datetime.now()
            r.usuario_creador = user
            r.categoria = form.cleaned_data['categoria']
            r.save()
            return HttpResponseRedirect("/roles")
    else:
        form = RolesForm()
    return render_to_response('admin/roles/crear_rol.html',{'form':form, 
                                                            'user':user,
                                                            'crear_rol': 'Crear rol' in permisos})

@login_required
def admin_permisos(request, rol_id):
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    actual = get_object_or_404(Rol, id=rol_id)
    if request.method == 'POST':
        form = PermisosForm(actual.categoria, request.POST)
        if form.is_valid():
            actual.permisos.clear()
            lista = form.cleaned_data['permisos']
            for item in lista:
                actual.permisos.add(item)
            actual.save()
            return HttpResponseRedirect("/roles")
    else:
        dict = {}
        for item in actual.permisos.all():
            dict[item.id] = True
        form = PermisosForm(actual.categoria, initial={'permisos': dict})
    return render_to_response("admin/roles/admin_permisos.html", {'form': form, 
                                                                  'rol': actual, 
                                                                  'user':user,
                                                                  'mod_rol':'Modificar rol' in permisos})

def mod_rol(request, rol_id):
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    actual = get_object_or_404(Rol, id=rol_id)
    if request.method == 'POST':
        form = ModRolesForm(request.POST)
        if form.is_valid():
            actual.descripcion = form.cleaned_data['descripcion']
            actual.save()
            return HttpResponseRedirect("/roles")
    else:
        if actual.id == 1:
            error = "No se puede modificar el rol de superusuario"
            return render_to_response("admin/roles/abm_rol.html", {'mensaje': error, 'rol':actual, 'user':user})
        form = ModRolesForm()
        form.fields['descripcion'].initial = actual.descripcion
    return render_to_response("admin/roles/mod_rol.html", {'user':user, 
                                                           'form':form,
                                                           'mod_rol':'Modificar rol' in permisos})

@login_required 
def borrar_rol(request, rol_id):
    """Borra un rol con las comprobaciones de consistencia"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------
    actual = get_object_or_404(Rol, id=rol_id)
    #Obtener todas las posibles dependencias
    if actual.categoria == 1:
        relacionados = UsuarioRolSistema.objects.filter(rol = actual).count()
    elif actual.categoria == 2:
        relacionados = UsuarioRolProyecto.objects.filter(rol = actual).count()
    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/roles")
    else:
        if actual.id == 1:
            error = "No se puede borrar el rol de superusuario"
            return render_to_response("admin/roles/rol_confirm_delete.html", {'mensaje': error, 
                                                                              'rol':actual, 
                                                                              'user':user,
                                                                              'eliminar_rol':'Eliminar_rol' in permisos})
        if relacionados > 0:
            error = "El rol se esta utilizando."
            return render_to_response("admin/roles/rol_confirm_delete.html", {'mensaje': error, 
                                                                              'rol':actual, 
                                                                              'user':user,
                                                                              'eliminar_rol':'Eliminar_rol' in permisos})
    return render_to_response("admin/roles/rol_confirm_delete.html", {'rol':actual, 
                                                                      'user':user, 
                                                                      'eliminar_rol':'Eliminar_rol' in permisos})

@login_required
def crear_proyecto(request):
    """Crea un nuevo proyecto."""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ProyectosForm(request.POST, request.FILES)
        if form.is_valid():
            p = Proyecto()
            p.nombre = form.cleaned_data['nombre']
            p.usuario_lider = form.cleaned_data['usuario_lider']
            p.descripcion = form.cleaned_data['descripcion']
            p.fecha_inicio = form.cleaned_data['fecha_inicio']
            p.fecha_fin = form.cleaned_data['fecha_fin']
            p.cronograma = form.cleaned_data['cronograma']
            p.fase = Fase.objects.get(pk=1)
            p.save()
            relacion = UsuarioRolProyecto()
            relacion.usuario = p.usuario_lider
            relacion.rol = Rol.objects.get(id=2)
            relacion.proyecto = p
            relacion.save()
            
            # Asociacion inicial de TipoArtefacto a fase por proyecto
            lista = TipoArtefacto.objects.all()
            for item in lista:
                rel = TipoArtefactoFaseProyecto()
                rel.proyecto = p
                rel.fase = item.fase
                rel.tipo_artefacto = item
                rel.save()
            
            return HttpResponseRedirect('/proyectos')
    else:
        form = ProyectosForm()
    return render_to_response('admin/proyectos/crear_proyecto.html',{'form':form, 
                                                                   'user':user,
                                                                   'crear_proyecto':'Crear proyecto' in permisos})

@login_required
def mod_proyecto(request, proyecto_id):
    user = User.objects.get(username=request.user.username)
    p = get_object_or_404(Proyecto, id = proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ModProyectosForm(p, request.POST, request.FILES)
        if form.is_valid():
            p.nombre = form.cleaned_data['nombre']
            if p.usuario_lider != form.cleaned_data['usuario_lider']:
                relacion = UsuarioRolProyecto.objects.filter(usuario = User.objects.get(pk = p.usuario_lider), proyecto = p, rol = Rol.objects.get(pk=2))[0]
                relacion.delete()
                relacion = UsuarioRolProyecto()
                relacion.usuario = p.usuario_lider
                relacion.rol = Rol.objects.get(id=2)
                relacion.proyecto = p
                relacion.save()
                p.usuario_lider != form.cleaned_data['usuario_lider']
            p.descripcion = form.cleaned_data['descripcion']
            p.fecha_inicio = form.cleaned_data['fecha_inicio']
            p.fecha_fin = form.cleaned_data['fecha_fin']
            p.cronograma = form.cleaned_data['cronograma']
            p.save()
            return HttpResponseRedirect('/proyectos')
    else:
        form = ModProyectosForm(p, initial = {'nombre': p.nombre,
                                        'usuario_lider': p.usuario_lider.id, 
                                        'descripcion': p.descripcion, 
                                        'fecha_inicio': p.fecha_inicio, 
                                        'fecha_fin':p.fecha_fin,
                                        'cronograma': p.cronograma})
    return render_to_response('admin/proyectos/mod_proyecto.html',{'form':form, 
                                                                   'user':user,
                                                                   'proyecto': p,
                                                                   'mod_proyecto':'Modificar proyecto' in permisos})

@login_required
def del_proyecto(request, proyecto_id):
    user = User.objects.get(username=request.user.username)
    p = get_object_or_404(Proyecto, id = proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        p.delete()
        return HttpResponseRedirect("/proyectos")
    else:
        return render_to_response("admin/proyectos/proyecto_confirm_delete.html", {'proyecto':p,
                                                                                   'eliminar_proyecto': 'Eliminar proyecto' in permisos})

@login_required
def admin_tipo_artefacto(request):
    """Muestra la pÃ¡gina de administracion de tipo de artefactos."""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    lista = TipoArtefacto.objects.all()
    return render_to_response('admin/tipo_artefacto/tipo_artefacto.html',
                              {'lista': lista,
                               'user':user, 
                               'ver_tipos_artefacto': 'Ver tipos-artefacto' in permisos,
                               'crear_tipo_artefacto': 'Crear tipo-artefacto' in permisos,
                               'mod_tipo_artefacto': 'Modificar tipo-artefacto' in permisos,
                               'eliminar_tipo_artefacto': 'Eliminar tipo-artefacto' in permisos})

@login_required
def crear_tipo_artefacto(request):
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = TipoArtefactoForm(request.POST)
        if form.is_valid():
            nuevo = TipoArtefacto()
            nuevo.nombre = form.cleaned_data['nombre']
            nuevo.descripcion = form.cleaned_data['descripcion']
            nuevo.fase = form.cleaned_data['fase']
            nuevo.save()
            return HttpResponseRedirect("/tipo_artefacto")
    else:
        form = TipoArtefactoForm()
    return render_to_response("admin/tipo_artefacto/crear_tipo_artefacto.html", {'form':form, 
                                                                               'user':user,
                                                                               'crear_tipo_artefacto': 'Crear tipo-artefacto' in permisos})

@login_required
def mod_tipo_artefacto(request, tipo_id):
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    actual = get_object_or_404(TipoArtefacto, id=tipo_id)
    if request.method == 'POST':
        form = TipoArtefactoForm(request.POST)
        if form.is_valid():
            actual.nombre = form.cleaned_data['nombre']
            actual.descripcion = form.cleaned_data['descripcion']
            actual.fase = form.cleaned_data['fase']
            actual.save()
            return HttpResponseRedirect("/tipo_artefacto")
    else:
        form = TipoArtefactoForm(initial = {'nombre': actual.nombre,
                                            'descripcion': actual.descripcion,
                                            'fase': actual.fase.id})
    return render_to_response("admin/tipo_artefacto/mod_tipo_artefacto.html", {'form':form, 
                                                                               'user':user,
                                                                               'tipo': actual,
                                                                               'mod_tipo_artefacto': 'Modificar tipo-artefacto' in permisos})

@login_required
def borrar_tipo_artefacto(request, tipo_id):
    """Borra un tipo de artefacto comprobando las dependencias"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    actual = get_object_or_404(TipoArtefacto, id=tipo_id)
    #comprobar las posibles dependencias
    relacionados = Artefacto.objects.filter(tipo = actual).count()
    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/tipo_artefacto")
    else:
        if relacionados > 0:
            error = "Este tipo de artefacto se esta utilizando"
            return render_to_response("admin/tipo_artefacto/tipo_artefacto_confirm_delete.html", {'mensaje':error,
                                                                                                  'tipo':actual, 
                                                                                                  'user':user,
                                                                                                  'eliminar_tipo_artefacto': 'Eliminar tipo-artefacto' in permisos})
    return render_to_response("admin/tipo_artefacto/tipo_artefacto_confirm_delete.html", {'tipo':actual, 
                                                                                          'user':user,
                                                                                          'eliminar_tipo_artefacto': 'Eliminar tipo-artefacto' in permisos})
@login_required
def admin_tipo_artefacto_fase(request, proyecto_id):
    """Metodo que permite asignar tipos de artefacto por fase."""
    # Aun falta terminar
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = TipoArtefactoFaseForm()
        # clean data
    else:
        form = TipoArtefactoFaseForm()
        # cargar los valores
        
    lista = TipoArtefactoFaseProyecto.objects.filter(proyecto=proyect)
    variables = RequestContext(request, {'proyecto': proyect,
                                        'lista': lista,
                                        'abm_artefactos': 'ABM artefactos' in permisos,
                                        'ver_artefactos': 'Ver artefactos' in permisos})
    return render_to_response('desarrollo/tipo_artefacto_fase.html', variables)

#desde aqui artefacto
@login_required
def admin_artefactos(request, proyecto_id):
    """Muestra la página de administracion de artefactos."""
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    tipoArtefactos = TipoArtefacto.objects.filter(fase = proyect.fase)
    linea = LineaBase.objects.filter(proyectos=proyect, fase=proyect.fase)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    lista = Artefacto.objects.filter(proyecto=proyect, habilitado=True, tipo__in=tipoArtefactos).order_by('nombre')
    variables = RequestContext(request, {'proyecto': proyect,
                                         'linea': linea,
                                        'lista': lista,
                                        'abm_artefactos': 'ABM artefactos' in permisos,
                                        'ver_artefactos': 'Ver artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/artefactos.html', variables)

@login_required    
def crear_artefacto(request, proyecto_id):
    """Crear un artefacto"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ArtefactoForm(proyect.fase, request.POST)
        if form.is_valid():
            art = Artefacto()
            art.usuario = user#solo en el historial?
            art.estado = 1
            art.fecha_creacion = datetime.date.today()#solo en el historial?
            art.version = 1
            art.complejidad = form.cleaned_data['complejidad']
            art.descripcion_corta = form.cleaned_data['descripcion_corta']#otro widget?
            art.descripcion_larga = form.cleaned_data['descripcion_larga']
            art.habilitado = True
            art.icono = form.cleaned_data['icono']
            art.proyecto = proyect
            art.tipo = form.cleaned_data['tipo']#hay que ver  
            art.fase = proyect.fase  
            lis = Artefacto.objects.filter(proyecto=proyect, tipo=form.cleaned_data['tipo'])
            cont = 1
            for item in lis:
                cont = cont+1
            art.nombre = (form.cleaned_data['tipo']).nombre + str(cont)                   
            art.save()            
            #Generacion del historial          
            hist = Historial()
            hist.usuario = user
            hist.fecha_creacion = datetime.date.today()
            hist.artefacto = art
            hist.save()            
            return HttpResponseRedirect("/proyectos/artefactos&id=" + str(proyecto_id)+"/")
    else:
        form = ArtefactoForm(proyect.fase)        
    variables = RequestContext(request, {'proyecto': proyect,
                                        'form': form,
                                        'abm_artefactos': 'ABM artefactos' in permisos,
                                        'ver_artefactos': 'Ver artefactos' in permisos})                
    return render_to_response('desarrollo/artefacto/crear_artefacto.html', variables)

@login_required
def modificar_artefacto(request, proyecto_id, art_id):
    """Modificar un artefacto"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    if (request.POST):
        art = Artefacto.objects.get(pk=art_id)
        form = ModArtefactoForm(proyect.fase, request.POST)
        if (form.is_valid()):
            cambio = False            
            if (form.cleaned_data['complejidad'] != art.complejidad):
                cambio = True
            elif (form.cleaned_data['descripcion_corta'] != art.descripcion_corta):
                cambio = True
            elif (form.cleaned_data['descripcion_larga'] != art.descripcion_larga):
                cambio = True
            elif (form.cleaned_data['icono'] != art.icono):
                cambio = True
            elif (form.cleaned_data['tipo'] != art.tipo):
                cambio = True            
            if (cambio):
                """ Se ingresa la version antigua al registro"""
                reg = RegistroHistorial()
                reg.version = art.version
                reg.estado = art.estado
                reg.complejidad = art.complejidad
                reg.descripcion_corta = art.descripcion_corta
                reg.descripcion_larga = art.descripcion_larga
                reg.habilitado = art.habilitado
                reg.tipo = art.tipo
                reg.fecha_modificacion = datetime.datetime.today()
                historial = Historial.objects.get(artefacto = art)
                reg.historial = historial
                reg.save()
                """Se incrementa la version actual"""
                art.version = art.version + 1
                art.save()                    
            art.complejidad = form.cleaned_data['complejidad']
            art.descripcion_corta = form.cleaned_data['descripcion_corta']
            art.descripcion_larga = form.cleaned_data['descripcion_larga']            
            art.icono = form.cleaned_data['icono']
            
            if (form.cleaned_data['tipo'] != art.tipo):
                lis = Artefacto.objects.filter(proyecto=proyect, tipo=form.cleaned_data['tipo'])
                cont = 1
                for item in lis:
                    cont = cont+1
                art.nombre = (form.cleaned_data['tipo']).nombre + str(cont)
                art.save()
                
            art.tipo = form.cleaned_data['tipo']           
            art.save()                          
            return HttpResponseRedirect("/proyectos/artefactos&id=" + str(proyecto_id)+"/")
    else:
        art = get_object_or_404(Artefacto, id=art_id)
        form = ModArtefactoForm(proyect.fase, initial={
                        'complejidad': art.complejidad,
                        'descripcion_corta':art.descripcion_corta,
                        'descripcion_larga':art.descripcion_larga,
                        'icono':art.icono,
                        'tipo':art.tipo._get_pk_val(),
                       })      
    variables = RequestContext(request, {'nombre':art.nombre,
                                         'form':form,
                                         'proyecto':proyect,
                                         'art':art,
                                         'abm_artefactos': 'ABM artefactos' in permisos})          
    return render_to_response('desarrollo/artefacto/mod_artefacto.html', variables)

@login_required
def definir_dependencias(request, proyecto_id, art_id, fase):
    """Definir las relaciones de un artefacto."""
    user = User.objects.get(username=request.user.username)
    p = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = p).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    art = get_object_or_404(Artefacto, id=art_id)
    relaciones = RelArtefacto.objects.filter(Q(padre = art) | Q(hijo = art))
    if request.method == 'POST':
        form = RelacionArtefactoForm(Fase.objects.get(pk=fase), art, request.POST)
        if form.is_valid():
            relaciones_nuevas = form.cleaned_data['artefactos']
            for item in relaciones:
                item.delete()
            for item in relaciones_nuevas:
                nuevo = RelArtefacto()
                nuevo.padre = item
                nuevo.hijo = art
                nuevo.save()
                return HttpResponseRedirect("/proyectos/artefactos&id=" + str(p.id) + "/")
    else:
        if not validar_fase(p, fase):
            mensaje = "Se paso un parametro invalido"
            return render_to_response("desarrollo/artefacto/relacion_artefacto.html", {'mensaje': mensaje})
        dic = {}
        for item in relaciones:
            dic[item.padre.id] = True
        form = RelacionArtefactoForm(Fase.objects.get(pk=fase), art, initial = {'artefactos': dic})
        return render_to_response("desarrollo/artefacto/relacion_artefacto.html", {'form': form, 'user':user, 'art':art, 'proyecto': p})
    

@login_required
def borrar_artefacto(request, proyecto_id, art_id):
    """Dar de baja un artefacto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    art = get_object_or_404(Artefacto, id=art_id)
    
    if request.method == 'POST':
        art.habilitado = False
        art.save()
        return HttpResponseRedirect("/proyectos/artefactos&id=" + str(proyecto_id)+"/")
    variables = RequestContext(request, {'proyecto':proyect, 'art': art, 'abm_artefactos': 'ABM artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/artefacto_confirm_delete.html', variables)

@login_required
def admin_artefactos_eliminados(request, proyecto_id):
    """Muestra la lista de artefactos eliminados de un proyecto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    lista = Artefacto.objects.filter(proyecto=proyect, habilitado=False)
    variables = RequestContext(request, {'proyecto': proyect, 'lista': lista, 'abm_artefactos': 'ABM artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/artefactos_eliminados.html', variables)

@login_required
def restaurar_artefacto_eliminado(request, proyecto_id, art_id):
    """Metodo que restaura un artefacto eliminado a su ultima version."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    art = get_object_or_404(Artefacto, id=art_id)
    
    if request.method == 'POST':
        print "segunda ronda" 
        art.habilitado = True
        art.save()
        lista = Artefacto.objects.filter(proyecto=proyect, habilitado=False)
        variables = RequestContext(request, {'proyecto': proyect, 'lista': lista, 'abm_artefactos': 'ABM artefactos' in permisos})
        return render_to_response('desarrollo/artefacto/artefactos_eliminados.html', variables)
    print "primera ronda"
    variables = RequestContext(request, {'proyecto':proyect, 'art': art, 'abm_artefactos': 'ABM artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/artefacto_confirm_restaurar.html', variables)

@login_required
def ver_historial(request, proyecto_id, art_id):
    art = Artefacto.objects.get(pk=art_id)
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    #-------------------------------------------------------------------
    historial = Historial.objects.get(artefacto=art)
    versiones = RegistroHistorial.objects.filter(historial=historial)
    variables = RequestContext(request, {'historial': historial, 
                                         'lista': versiones,
                                         'art': art,
                                         'proyecto': proyect,
                                         'abm_artefactos': 'ABM artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/historial.html', variables)

@login_required
def restaurar_artefacto(request, proyecto_id, art_id, reg_id):
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    print permisos
    if not ('ABM artefactos' in permisos):
        return render_to_response('error.html')
    #-------------------------------------------------------------------
    art = Artefacto.objects.get(pk = art_id)
    reg = RegistroHistorial()
    reg.version = art.version
    reg.estado = art.estado
    reg.complejidad = art.complejidad
    reg.descripcion_corta = art.descripcion_corta
    reg.descripcion_larga = art.descripcion_larga
    reg.habilitado = art.habilitado
    #reg.icono = art.icono
    reg.tipo = art.tipo
    reg.fecha_modificacion = datetime.datetime.today()
    historial = Historial.objects.get(artefacto = art)
    reg.historial = historial
    reg.save()
    #preguntar por la version incrementada!!!!    
    r = RegistroHistorial.objects.get(pk=reg_id)
    art.version = r.version
    art.estado = r.estado #el estado como va ser!!!
    art.complejidad = r.complejidad
    art.descripcion_corta = r.descripcion_corta 
    art.descripcion_larga = r.descripcion_larga 
    art.habilitado = r.habilitado
    #art.icono = r.icono
    art.tipo = r.tipo
    art.save()   
    return HttpResponseRedirect("/proyectos/artefactos&id="+ str(proyecto_id)+"/")

@login_required
def revisar_artefacto(request, proyecto_id, art_id):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    art = Artefacto.objects.get(pk=art_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')    
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())    
    permisos = []    
    for item in permisos_obj:
        permisos.append(item.nombre)        
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = RevisarArtefactoForm(request.POST)        
        if form.is_valid():                        
            art.estado = form.cleaned_data['estado']         
            art.save()                
            return HttpResponseRedirect("/proyectos/artefactos&id=" + str(proyect.id)+"/")
    else:        
        form = RevisarArtefactoForm({'estado':art.estado})
    return render_to_response("desarrollo/artefacto/revisar_artefacto.html", {
                                                                              'form':form, 
                                                                              'proyecto':proyect,                                                                       
                                                                              'art':art,
                                                                              'revisar_artefacto': 'Revisar artefactos' in permisos})
    
@login_required
def calcular_impacto(request, proyecto_id, art_id):
    """Calculo del impacto de un artefacto"""
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    art = get_object_or_404(Artefacto, id=art_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')    
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())    
    permisos = []    
    for item in permisos_obj:
        permisos.append(item.nombre)        
    print permisos
    #-------------------------------------------------------------------
    relaciones_izq = obtener_relaciones_izq(art, [])
    print relaciones_izq
    relaciones_der = obtener_relaciones_der(art, [])
    print relaciones_der
    impacto = 0
    if relaciones_izq:
        for item in relaciones_izq:
            impacto = impacto + item.complejidad
            print impacto
    if relaciones_der:
        for item in relaciones_der:
            impacto = impacto + item.complejidad
            print impacto
    #impacto = impacto + art.complejidad
    return render_to_response("desarrollo/artefacto/complejidad.html", {'art': art, 'user': user, 'impacto': impacto,
                                                                        'izq': relaciones_izq, 'der': relaciones_der,
                                                                        'proyecto': proyect})
    
@login_required
def fases_anteriores(request, proyecto_id):
    user = User.objects.get(username = request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyect).only('rol')    
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())    
    permisos = []    
    for item in permisos_obj:
        permisos.append(item.nombre)        
    print permisos
    #-------------------------------------------------------------------
    linea1 = LineaBase.objects.filter(proyectos=proyect, fase=1)
    linea2 = LineaBase.objects.filter(proyectos=proyect, fase=2)
    tipo1 = TipoArtefacto.objects.filter(fase=1)
    lista1 = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipo1)
    tipo2 = TipoArtefacto.objects.filter(fase=2)
    lista2 = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipo2)
    return render_to_response("desarrollo/artefacto/Fases_anteriores.html", { 'proyecto':proyect,                                                                       
                                                                              'lista1':lista1,
                                                                              'lista2':lista2,
                                                                              'abm_artefactos': 'ABM artefactos' in permisos
                                                                              })    
    
@login_required
def linea_base (request, proyecto_id):
    user = User.objects.get(username = request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    fase = Fase.objects.get(pk=proyect.fase.id)
    #Validacion de los permisos-----------------------------------------
    roles = UsuarioRolProyecto.objects.filter(proyecto=proyect, usuario=user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())        
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)        
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        tipoArtefactos = TipoArtefacto.objects.filter(fase=fase)
        artefactos = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipoArtefactos, habilitado=True)        
        if (artefactos):
            bool = False
            for item in artefactos:
                if (item.estado != 3):
                    bool = True
            if (bool == False):
                linea = LineaBase()
                linea.fecha_creacion = datetime.date.today()
                linea.proyectos = proyect
                linea.fase = fase
                linea.save()
                
                if (fase.id == 1):
                    proyect.fase = Fase.objects.get(pk=2)
                    proyect.save()
                elif(fase.id == 2):
                    proyect.fase = Fase.objects.get(pk=3)
                    proyect.save() 
            else:
                msg = "Existen artefactos pendientes de aprobacion"
                variables = RequestContext(request, {'lineabase': 'Generar LB' in permisos,
                                                     'proyecto': proyect,
                                                     'fase': fase,
                                                     'msg':msg })
                return render_to_response('gestion/linea_base_error.html', variables)
        else:
            msg = "El proyecto no cuenta con artefactos habilitados en esta fase"
            variables = RequestContext(request, {'lineabase': 'Generar LB' in permisos,
                                                'proyecto': proyect,
                                                'fase': fase,
                                                'msg':msg })
            return render_to_response('gestion/linea_base_error.html', variables)
        return HttpResponseRedirect("/proyectos/admin&id=" + str(proyect.id)+"/")
                
    fin = False
    if (fase.id == 3):
        linea = LineaBase.objects.filter(proyectos=proyect, fase=fase)        
        if (linea):
            fin = True          
    print fin       
    variables = RequestContext(request, {'lineabase': 'Generar LB' in permisos,
                                         'proyecto': proyect,
                                         'fase': fase,
                                         'fin':fin                                         
                                         })
    return render_to_response('gestion/linea_base.html', variables)

@login_required
def terminar(peticion):
    """Muestra una pagina de confirmacion de exito"""
    return render_to_response('operacion_exitosa.html');

def login_redirect(request):
    """Redirige de /accounts/login a /login."""
    return HttpResponseRedirect('/login')

def logout_pagina(request):
    """Pagina de logout"""
    logout(request)
    return render_to_response('logout.html')
