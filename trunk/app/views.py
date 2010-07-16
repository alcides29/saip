# -*- coding: iso-8859-15 -*-
import base64

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.contrib.auth import logout
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.forms.formsets import formset_factory
from geraldo.generators import PDFGenerator

from saip.app.forms import *
from saip.app.models import *
from saip.app.helper import *
from saip.app.reports import *

@login_required
def principal(request):
    """Muestra la pagina principal.

    @return: Pagina principal, lista de proyectos y usuario.
    """
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
        if not item.proyecto.id in lista_proyectos:
            lista_proyectos.append(item.proyecto.id)
    print lista_proyectos
    variables['permisos_proyecto'] = lista_proyectos
    #-------------------------------------------------------------------
    lista = Proyecto.objects.all()
    variables['user'] = user
    variables['lista'] = lista
    print variables
    return render_to_response('main_page.html', variables)
    
@login_required
def administrar_proyecto(request, proyecto_id):
    """Administracion de proyecto para el modulo de desarrollo.
    
    @param proyecto_id: Id del proyecto a administrar
    @type proyecto_id: Integer
    @return: admin_proyecto.html, proyecto, usuario y lista de permisos
    @rtype: Lista 
    """
    user = User.objects.get(username=request.user.username)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    permisos = get_permisos_proyecto(user, proyecto)
    permisos_ant_req = []
    permisos_ant_dis = []
    if proyecto.fase.id == 2:
        permisos_ant_req = get_permisos_proyecto_ant(user, proyecto, Fase.objects.get(pk=1))
    elif proyecto.fase.id == 3:
        permisos_ant_req = get_permisos_proyecto_ant(user, proyecto, Fase.objects.get(pk=1))
        permisos_ant_dis = get_permisos_proyecto_ant(user, proyecto, Fase.objects.get(pk=2)) 
    #print permisos_ant
    linea = LineaBase.objects.filter(proyectos=proyecto, fase=3)
    return render_to_response("desarrollo/admin_proyecto.html", {'proyecto':proyecto, 
                                                                 'user':user,
                                                                 'fin':linea,
                                                                 'ver_artefactos': 'Ver artefactos' in permisos,
                                                                 'abm_artefactos': 'ABM artefactos' in permisos,
                                                                 'ver_miembros': 'Ver miembros' in permisos,
                                                                 'abm_miembros': 'ABM miembros' in permisos,
                                                                 'asignar_roles': 'Asignar roles' in permisos,
                                                                 'generarlb':'Generar LB' in permisos,
                                                                 'asignar_tipoArt': 'Asignar tipo-artefacto fase' in permisos,
                                                                 'ver_artefactos_ant_req': 'Ver artefactos' in permisos_ant_req or 'ABM artefactos' in permisos_ant_req,
                                                                 'ver_artefactos_ant_dis': 'Ver artefactos' in permisos_ant_dis or 'ABM artefactos' in permisos_ant_dis})
    
@login_required
def admin_usuarios_proyecto(request, object_id):
    """Metodo para administracion de miembros de un proyecto.
    
    @param object_id: Id del proyecto
    @type object_id: Integer
    
    @return: Usuario, proyecto, lista de miembros y permisos
    @rtype: Lista
    """
    user = User.objects.get(username=request.user.username)
    p = Proyecto.objects.get(pk = object_id)
    permisos = get_permisos_proyecto(user, p)
    miembros = UsuarioRolProyecto.objects.filter(proyecto = p).order_by('id')
    lista = []
    for item in miembros:
        if not item.usuario in lista:
            lista.append(item.usuario)
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            miembros = UsuarioRolProyecto.objects.filter(Q(proyecto = p), Q(usuario__username__icontains = palabra) |
                                                         Q(rol__nombre__icontains = palabra)).order_by('id')
            lista = []
            for item in miembros:
                if not item.usuario in lista:
                    lista.append(item.usuario)
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response('desarrollo/admin_miembros.html',{'lista':lista, 'form': form,
                                                                        'user':user, 'pag': pag, 
                                                                        'proyecto':Proyecto.objects.get(id=object_id),                                                                         
                                                                        'ver_miembros': 'Ver miembros' in permisos,
                                                                        'abm_miembros': 'ABM miembros' in permisos})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('desarrollo/admin_miembros.html',{'lista':lista, 'form': form,
                                                                'user':user, 'pag': pag, 
                                                                'proyecto':Proyecto.objects.get(id=object_id),                                                                 
                                                                'ver_miembros': 'Ver miembros' in permisos,
                                                                'abm_miembros': 'ABM miembros' in permisos})
    
@login_required
def cambiar_rol_usuario_proyecto(request, proyecto_id, user_id):
    """Metodo para cambiar roles a un usuario de proyecto.
    
    @param proyecto_id: Id del proyecto
    @type proyecto_id: Integer
    @param user_id: Id del proyecto
    @type user_id: Integer
    
    @return: Usuario, proyecto y permisos
    @rtype: Lista
    """
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
    """Metodo para agregar un usuario a un proyecto.
    
    @param object_id: Id del proyecto
    @type object_id: Integer
    
    @return: Usuario, proyecto y permisos
    @rtype: Lista
    """
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
        form = UsuarioProyectoForm(p, request.POST)
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
        form = UsuarioProyectoForm(p)
    return render_to_response('desarrollo/add_miembro.html', {'form':form, 
                                                              'user':user,  
                                                              'proyecto': p,
                                                              'abm_miembros': 'ABM miembros' in permisos})

@login_required
def eliminar_miembro_proyecto(request, proyecto_id, user_id):
    """Metodo para eliminar un miembro de un proyecto.
    
    @param proyecto_id: Id del proyecto
    @type proyecto_id: Integer
    @param user_id: Id del proyecto
    @type user_id: Integer
    
    @return: Usuario, proyecto y permisos
    @rtype: Lista
    """
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
    """Agrega un nuevo usuario.
    
    @param proyecto_id: Id del proyecto
    @type proyecto_id: Integer
    @param user_id: Id del proyecto
    @type user_id: Integer
    
    @return: Usuario y permisos
    @rtype: Lista
    """
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
    """Modifica los datos de un usuario.
    
    @param usuario_id: Id del proyecto
    @type usuario_id: Integer
    
    @return: Usuario, form y permisos
    @rtype: Lista
    """
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
            usuario.save()
            return HttpResponseRedirect("/usuarios")
    else:
        form = ModUsuariosForm(initial={'first_name':usuario.first_name, 'last_name': usuario.last_name,'email':usuario.email})
    return render_to_response('admin/usuarios/mod_usuario.html',{'form':form, 
                                                                 'user':user, 
                                                                 'usuario':usuario, 
                                                                 'mod_usuario': 'Modificar usuario' in permisos})

@login_required
def cambiar_password(request):
    """Cambia la contrasena del usuario logueado
    
    @return: Usuario, html y formulario
    @rtype: Lista
    """
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return HttpResponseRedirect("/")
    else:
        form = CambiarPasswordForm()
    return render_to_response("cambiar_password.html", {'form': form, 'user': user})

@login_required
def asignar_roles_sistema(request, usuario_id):
    """Asigna roles de sistema a un usuario.
    
    @param usuario_id: Id del proyecto
    @type usuario_id: Integer
    
    @return: Usuario, html y permisos
    @rtype: Lista
    """
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    usuario = get_object_or_404(User, id=usuario_id)
    lista_roles = UsuarioRolSistema.objects.filter(usuario = usuario)
    
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
    """Borra un usuario, comprobando las dependencias primero
    
    @param usuario_id: Id del proyecto
    @type usuario_id: Integer
    @precondition: Se verifican las dependencias
    
    @return: Usuario, html y permisos
    @rtype: Lista
    """
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
    comprometido = 0
    #comprobar si el usuario esta asociado a algun proyecto como lider
    comprometido = Proyecto.objects.filter(usuario_lider = usuario).count()
    if request.method == 'POST':
        usuario.delete()
        return HttpResponseRedirect("/usuarios")
    else:
        if usuario.id == 1:
            error = "No se puede borrar al superusuario."
            return render_to_response("admin/usuarios/user_confirm_delete.html", {'mensaje': error,'usuario':usuario, 'user': user, 'eliminar_usuario': 'Eliminar usuario' in permisos})
        elif comprometido > 0:
            error = "El usuario est&aacute; asociado a un proyecto como l&iacute;der."
            return render_to_response("admin/usuarios/user_confirm_delete.html", {'mensaje': error,'usuario':usuario, 'user': user, 'eliminar_usuario': 'Eliminar usuario' in permisos})
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
    """Administracion general de usuarios
        
    @return: Usuario, html y permisos
    @rtype: Lista
    """
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = User.objects.all().order_by("id")
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = User.objects.filter(Q(username__icontains = palabra) | Q(first_name__icontains = palabra) | Q(last_name__icontains = palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            try:
                pag = paginator.page(page)
            except (EmptyPage, InvalidPage):
                pag = paginator.page(paginator.num_pages)
            return render_to_response('admin/usuarios/usuarios.html',{'pag': pag,
                                                               'form': form,
                                                               'lista':lista,
                                                               'user':user, 
                                                               'ver_usuarios': 'Ver usuarios' in permisos,
                                                               'crear_usuario': 'Crear usuario' in permisos,
                                                               'mod_usuario': 'Modificar usuario' in permisos,
                                                               'eliminar_usuario': 'Eliminar usuario' in permisos,
                                                               'asignar_roles': 'Asignar rol' in permisos})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('admin/usuarios/usuarios.html',{ 'pag':pag,
                                                               'form': form,
                                                               'lista':lista,
                                                               'user':user, 
                                                               'ver_usuarios': 'Ver usuarios' in permisos,
                                                               'crear_usuario': 'Crear usuario' in permisos,
                                                               'mod_usuario': 'Modificar usuario' in permisos,
                                                               'eliminar_usuario': 'Eliminar usuario' in permisos,
                                                               'asignar_roles': 'Asignar rol' in permisos})

@login_required
def admin_proyectos(request):
    """Administracion general de proyectos
    
    @return: Usuario, html y permisos
    @rtype: Lista
    """
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = Proyecto.objects.all().order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Proyecto.objects.filter(Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(usuario_lider__username__icontains = palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            try:
                pag = paginator.page(page)
            except (EmptyPage, InvalidPage):
                pag = paginator.page(paginator.num_pages)
            return render_to_response('admin/proyectos/proyectos.html',{'lista':lista, 'pag': pag, 'form':form, 
                                                                'user':user,
                                                                'ver_proyectos':'Ver proyectos' in permisos,
                                                                'crear_proyecto': 'Crear proyecto' in permisos,
                                                                'mod_proyecto': 'Modificar proyecto' in permisos,
                                                                'eliminar_proyecto': 'Eliminar proyecto' in permisos})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
        return render_to_response('admin/proyectos/proyectos.html',{'lista':lista, 'pag': pag, 'form':form, 
                                                                'user':user,
                                                                'ver_proyectos':'Ver proyectos' in permisos,
                                                                'crear_proyecto': 'Crear proyecto' in permisos,
                                                                'mod_proyecto': 'Modificar proyecto' in permisos,
                                                                'eliminar_proyecto': 'Eliminar proyecto' in permisos})

@login_required
def admin_roles(request):
    """Administracion general de roles"""
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    return render_to_response('admin/roles/roles.html',{'user':user,
                                                        'ver_roles':'Ver roles' in permisos,
                                                        'crear_rol': 'Crear rol' in permisos,
                                                        'mod_rol': 'Modificar rol' in permisos,
                                                        'eliminar_rol': 'Eliminar rol' in permisos})
@login_required
def admin_roles_sist(request):
    """Administracion general de roles"""
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = Rol.objects.filter(categoria=1).order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Rol.objects.filter(Q(categoria = 1), Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(usuario_creador__username__icontains = palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            try:
                pag = paginator.page(page)
            except (EmptyPage, InvalidPage):
                pag = paginator.page(paginator.num_pages)
            return render_to_response('admin/roles/roles_sistema.html',{'lista':lista, 'form': form,
                                                        'user':user, 'pag': pag,
                                                        'ver_roles':'Ver roles' in permisos,
                                                        'crear_rol': 'Crear rol' in permisos,
                                                        'mod_rol': 'Modificar rol' in permisos,
                                                        'eliminar_rol': 'Eliminar rol' in permisos})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('admin/roles/roles_sistema.html',{'lista':lista, 'form':form,
                                                            'user':user, 'pag': pag,
                                                            'ver_roles':'Ver roles' in permisos,
                                                            'crear_rol': 'Crear rol' in permisos,
                                                            'mod_rol': 'Modificar rol' in permisos,
                                                            'eliminar_rol': 'Eliminar rol' in permisos})
@login_required
def admin_roles_proy(request):
    """Administracion general de roles"""
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = Rol.objects.filter(categoria=2).order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Rol.objects.filter(Q(categoria = 2), Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(usuario_creador__username__icontains = palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            try:
                pag = paginator.page(page)
            except (EmptyPage, InvalidPage):
                pag = paginator.page(paginator.num_pages)
            return render_to_response('admin/roles/roles_sistema.html',{'lista':lista,'form':form,
                                                        'user':user, 'pag': pag,
                                                        'ver_roles':'Ver roles' in permisos,
                                                        'crear_rol': 'Crear rol' in permisos,
                                                        'mod_rol': 'Modificar rol' in permisos,
                                                        'eliminar_rol': 'Eliminar rol' in permisos})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('admin/roles/roles_proyecto.html',{'lista':lista,'form':form,
                                                        'user':user,'pag': pag,
                                                        'ver_roles':'Ver roles' in permisos,
                                                        'crear_rol': 'Crear rol' in permisos,
                                                        'mod_rol': 'Modificar rol' in permisos,
                                                        'eliminar_rol': 'Eliminar rol' in permisos})

@login_required
def crear_rol(request):
    """Agrega un nuevo rol"""
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
        if actual.categoria == 1:
            form = PermisosForm(request.POST)
        else:
            form = PermisosProyectoForm(request.POST)
        if form.is_valid():
            actual.permisos.clear()
            if actual.categoria == 1:
                lista = form.cleaned_data['permisos']
                for item in lista:
                    nuevo = RolPermiso()
                    nuevo.rol = actual
                    nuevo.permiso = item
                    nuevo.save()
            else:
                lista_req = form.cleaned_data['permisos1']
                lista_dis = form.cleaned_data['permisos2']
                lista_impl = form.cleaned_data['permisos3']
                for item in lista_req:
                    nuevo = RolPermiso()
                    nuevo.rol = actual
                    nuevo.permiso = item
                    nuevo.fase = Fase.objects.get(pk=1)
                    nuevo.save()
                for item in lista_dis:
                    nuevo = RolPermiso()
                    nuevo.rol = actual
                    nuevo.permiso = item
                    nuevo.fase = Fase.objects.get(pk=2)
                    nuevo.save()
                for item in lista_impl:
                    nuevo = RolPermiso()
                    nuevo.rol = actual
                    nuevo.permiso = item
                    nuevo.fase = Fase.objects.get(pk=3)
                    nuevo.save()
            if actual.categoria == 1:
                return HttpResponseRedirect("/roles/sist")
            else:
                return HttpResponseRedirect("/roles/proy")
    else:
        #form = PermisosForm(actual.categoria, initial={'permisos': dict})
        if actual.categoria == 1:
            dict = {}
            for item in actual.permisos.all():
                dict[item.id] = True
            form = PermisosForm(initial={'permisos': dict})
        else:
            dict1 = {}
            for item in actual.permisos.filter(rolpermiso__fase = Fase.objects.get(pk=1)):
                dict1[item.id] = True
            dict2 = {}
            for item in actual.permisos.filter(rolpermiso__fase = Fase.objects.get(pk=2)):
                dict2[item.id] = True
            dict3 = {}
            for item in actual.permisos.filter(rolpermiso__fase = Fase.objects.get(pk=3)):
                dict3[item.id] = True
            form = PermisosProyectoForm(initial={'permisos1': dict1, 'permisos2': dict2, 'permisos3': dict3})
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
            if actual.categoria == 1:
                return HttpResponseRedirect("/roles/sist")
            else:
                return HttpResponseRedirect("/roles/proy")
    else:
        if actual.id == 1:
            error = "No se puede modificar el rol de superusuario"
            return render_to_response("admin/roles/abm_rol.html", {'user': user,'mensaje': error, 'rol':actual, 'user':user})
        form = ModRolesForm()
        form.fields['descripcion'].initial = actual.descripcion
    return render_to_response("admin/roles/mod_rol.html", {'user':user, 
                                                           'form':form,
                                                           'rol': actual,
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
            return render_to_response("admin/roles/rol_confirm_delete.html", {'mensaje': error, 'user':user,
                                                                              'rol':actual, 
                                                                              'user':user,
                                                                              'eliminar_rol':'Eliminar rol' in permisos})
        if relacionados > 0:
            error = "El rol se esta utilizando."
            return render_to_response("admin/roles/rol_confirm_delete.html", {'mensaje': error, 'user': user,
                                                                              'rol':actual, 
                                                                              'user':user,
                                                                              'eliminar_rol':'Eliminar rol' in permisos})
    return render_to_response("admin/roles/rol_confirm_delete.html", {'rol':actual, 
                                                                      'user':user, 
                                                                      'eliminar_rol':'Eliminar rol' in permisos})

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
            lista = TipoArtefacto.objects.filter(proyecto = False)
            for item in lista:
                rel = TipoArtefactoFaseProyecto()
                rel.proyecto = p
                rel.fase = item.fase
                rel.tipo_artefacto = item
                rel.cant = 1
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
                relacion = UsuarioRolProyecto.objects.filter(usuario = p.usuario_lider, proyecto = p, rol = Rol.objects.get(pk=2))[0]
                relacion.delete()
                p.usuario_lider = form.cleaned_data['usuario_lider']
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
        return render_to_response("admin/proyectos/proyecto_confirm_delete.html", {'proyecto':p, 'user': user,
                                                                                   'eliminar_proyecto': 'Eliminar proyecto' in permisos})

@login_required
def admin_tipo_artefacto(request):
    """Muestra la pagina de administracion de tipo de artefactos."""
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = TipoArtefacto.objects.filter(proyecto=False)
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = TipoArtefacto.objects.filter(Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(fase__nombre__icontains = palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            try:
                pag = paginator.page(page)
            except (EmptyPage, InvalidPage):
                pag = paginator.page(paginator.num_pages)
            return render_to_response('admin/tipo_artefacto/tipo_artefacto.html',
                              {'lista': lista, 'pag':pag,
                               'user':user, 'form': form,
                               'ver_tipos_artefacto': 'Ver tipos-artefacto' in permisos,
                               'crear_tipo_artefacto': 'Crear tipo-artefacto' in permisos,
                               'mod_tipo_artefacto': 'Modificar tipo-artefacto' in permisos,
                               'eliminar_tipo_artefacto': 'Eliminar tipo-artefacto' in permisos})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('admin/tipo_artefacto/tipo_artefacto.html',
                              {'lista': lista, 'pag':pag,
                               'user':user, 'form': form,
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
            nuevo.proyecto = False
            nuevo.save()
            
            # Agregamos en cada uno de los proyectos
            p = Proyecto.objects.all()
            for item in p:
                tipo_art = TipoArtefactoFaseProyecto()
                tipo_art.proyecto = item
                tipo_art.fase = nuevo.fase
                tipo_art.tipo_artefacto = nuevo
                tipo_art.cant = 1
                tipo_art.save()
            return HttpResponseRedirect("/tipo_artefacto")
    else:
        form = TipoArtefactoForm()
    return render_to_response("admin/tipo_artefacto/crear_tipo_artefacto.html", {'form':form, 
                                                                               'user':user,
                                                                               'crear_tipo_artefacto': 'Crear tipo-artefacto' in permisos})

@login_required
def add_tipo_artefacto(request, proyecto_id):
    """Crea un tipo de artefacto para un proyecto."""
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
    p = Proyecto.objects.get(pk = proyecto_id)
    if request.method == 'POST':
        form = TipoArtefactoForm(request.POST)
        if form.is_valid():
            nuevo = TipoArtefacto()
            nuevo.nombre = form.cleaned_data['nombre']
            nuevo.descripcion = form.cleaned_data['descripcion']
            nuevo.fase = form.cleaned_data['fase']
            nuevo.proyecto = True
            nuevo.save()
            
            # Agregamos al proyecto actual
            tipo_art = TipoArtefactoFaseProyecto()
            tipo_art.proyecto = p
            tipo_art.fase = nuevo.fase
            tipo_art.tipo_artefacto = nuevo
            tipo_art.cant = 1
            tipo_art.save()
            return HttpResponseRedirect("/proyectos/tipoArtefacto&id="+str(proyecto_id))
    else:
        form = TipoArtefactoForm()
    return render_to_response("admin/tipo_artefacto/add_tipo_artefacto.html",
                              {'form':form,
                               'user':user,
                               'proyecto':p,
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
        form = ModTipoArtefactoForm(actual, request.POST)
        if form.is_valid():
            actual.nombre = form.cleaned_data['nombre']
            actual.descripcion = form.cleaned_data['descripcion']
            actual.fase = form.cleaned_data['fase']
            actual.save()
            return HttpResponseRedirect("/tipo_artefacto")
    else:
        form = ModTipoArtefactoForm(actual, initial = {'nombre': actual.nombre,
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
            return render_to_response("admin/tipo_artefacto/tipo_artefacto_confirm_delete.html", {'mensaje':error, 'user': user,
                                                                                                  'tipo':actual, 
                                                                                                  'user':user,
                                                                                                  'eliminar_tipo_artefacto': 'Eliminar tipo-artefacto' in permisos})
    return render_to_response("admin/tipo_artefacto/tipo_artefacto_confirm_delete.html", {'tipo':actual, 
                                                                                          'user':user,
                                                                                          'eliminar_tipo_artefacto': 'Eliminar tipo-artefacto' in permisos})

@login_required
def admin_tipo_artefacto_fase(request, proyecto_id):
    """Lista de tipos de artefacto con fase para el proyecto actual."""
    user = User.objects.get(username = request.user.username)
    p = Proyecto.objects.get(id = proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto_id).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    #-------------------------------------------------------------------
    lista = TipoArtefactoFaseProyecto.objects.filter(proyecto = proyecto_id)
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = TipoArtefactoFaseProyecto.objects.filter(Q(proyecto = proyecto_id), Q(fase__id__icontains = palabra) | 
                     Q(tipo_artefacto__nombre__icontains = palabra) | Q(fase__nombre__icontains = palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response('desarrollo/tipo_artefacto_fase.html',{'lista': lista, 'pag':pag,
                                                                             'user':user, 'form': form,'lista': lista,
                                                                             'proyecto': p,
                                                                             'asignar_tipoArt': 'Asignar tipo-artefacto fase' in permisos})
    else:   
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('desarrollo/tipo_artefacto_fase.html',{'lista': lista, 'pag':pag,
                                                                     'user':user, 'form': form,'lista': lista,
                                                                     'proyecto': p,
                                                                     'asignar_tipoArt': 'Asignar tipo-artefacto fase' in permisos})
    
@login_required
def mod_tipo_artefacto_fase(request, proyecto_id, tipo_art_id):
    """Permite asignar tipos de artefacto a una fase de un proyecto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    tipoA = TipoArtefacto.objects.get(id = tipo_art_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto_id).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    #-------------------------------------------------------------------
    tipo_art = TipoArtefactoFaseProyecto.objects.filter(proyecto = proyecto_id, tipo_artefacto = tipo_art_id)[0]
    if request.method == 'POST':
        form = TipoArtefactoFaseForm(request.POST)
        if form.is_valid():
            tipo_art.fase = form.cleaned_data['fase']
            tipo_art.save()
            return HttpResponseRedirect("/proyectos/tipoArtefacto&id="+str(proyecto_id))
    else:
        form = TipoArtefactoFaseForm(initial={'fase': tipo_art.fase.id})
    
    return render_to_response('desarrollo/mod_tipo_art_fase.html',
                              {'form': form, 'user':user,
                               'tipo_artefacto': tipoA,
                               'proyecto': proyect,
                               'asignar_tipoArt': 'Asignar tipo-artefacto fase' in permisos})

@login_required
def quitar_tipo_artefacto_fase(request, proyecto_id, tipo_art_id):
    """Permite quitar un tipo de artefacto de un proyecto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    tipoA = TipoArtefacto.objects.get(id = tipo_art_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto_id).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    #-------------------------------------------------------------------
    tipo_art = TipoArtefactoFaseProyecto.objects.filter(proyecto = proyecto_id, tipo_artefacto = tipo_art_id)
    lista = TipoArtefactoFaseProyecto.objects.filter(proyecto = proyecto_id)
    if request.method == 'POST':
        tipo_art.delete()
        return HttpResponseRedirect("/proyectos/tipoArtefacto&id="+ str(proyecto_id)+"/")
    else:
        return render_to_response('desarrollo/tipo_art_fase_confirm_del.html',
                              {'tipo':tipoA,
                               'user':user,
                               'proyecto': proyect,
                               'asignar_tipoArt': 'Asignar tipo-artefacto fase' in permisos})
    
        
#desde aqui artefacto
@login_required
def admin_artefactos(request, proyecto_id):
    """Muestra la pagina de administracion de artefactos."""
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    tipoArtefactos = TipoArtefactoFaseProyecto.objects.filter(proyecto = proyecto_id, fase = proyect.fase)
    linea = LineaBase.objects.filter(proyectos=proyect, fase=proyect.fase)
    permisos = get_permisos_proyecto(user, proyect)
    lista = Artefacto.objects.filter(proyecto=proyect, habilitado=True, tipo__in=tipoArtefactos).order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Artefacto.objects.filter(Q(proyecto=proyect), Q(habilitado=True), Q(tipo__in=tipoArtefactos),Q(nombre__icontains = palabra)|Q(descripcion_corta__icontains = palabra)| Q(usuario__username__icontains = palabra)|Q(estado__icontains = palabra) | Q(tipo__tipo_artefacto__nombre__icontains= palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response('desarrollo/artefacto/artefactos.html', {'lista': lista, 'pag':pag,
                                                                                   'user':user, 'form': form,
                                                                                   'proyecto': proyect,
                                                                                   'linea': linea,
                                                                                   'abm_artefactos': 'ABM artefactos' in permisos,
                                                                                   'ver_artefactos': 'Ver artefactos' in permisos,
                                                                                   'revisar_artefactos': 'Revisar artefactos' in permisos})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('desarrollo/artefacto/artefactos.html', {'lista': lista, 'pag':pag,
                                                                        'user':user, 'form': form,
                                                                        'proyecto': proyect,
                                                                        'linea': linea,
                                                                        'abm_artefactos': 'ABM artefactos' in permisos,
                                                                        'ver_artefactos': 'Ver artefactos' in permisos,
                                                                        'revisar_artefactos': 'Revisar artefactos' in permisos})


@login_required
def crear_artefacto(request, proyecto_id):
    """Crear un artefacto"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    if request.method == 'POST':
        form = ArtefactoForm(proyect.fase, proyecto_id, request.POST, request.FILES)
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
            
            #asignamos el nombre
            art.nombre = art.tipo.tipo_artefacto.nombre + str(art.tipo.cant)
            art.tipo.cant = art.tipo.cant + 1
            art.tipo.save()
            art.save()
            
            #Generacion del historial          
            hist = Historial()
            hist.usuario = user
            hist.fecha_creacion = datetime.date.today()
            hist.artefacto = art
            hist.save()            
            return HttpResponseRedirect("/proyectos/artefactos&id=" + str(proyecto_id)+"/")
    else:
        form = ArtefactoForm(proyect.fase, proyect)
                
    variables = RequestContext(request, {'proyecto': proyect,
                                        'form': form,
                                        'abm_artefactos': 'ABM artefactos' in permisos})                
    return render_to_response('desarrollo/artefacto/crear_artefacto.html', variables)

@login_required
def modificar_artefacto(request, proyecto_id, art_id):
    """Modificar un artefacto"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    if request.method == 'POST':
        art = Artefacto.objects.get(pk=art_id)
        form = ModArtefactoForm(proyect.fase, request.POST, request.FILES)
        if (form.is_valid()):
            
            archivos = Adjunto.objects.filter(artefacto=art, habilitado = True)
            relaciones = RelArtefacto.objects.filter(hijo = art, habilitado=True)            
            
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
                registrar_version(art, relaciones, archivos)                    
                
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
        aprobado = False
        if (art.estado == 3):
            aprobado = True
        form = ModArtefactoForm(proyect.fase, initial={
                        'complejidad': art.complejidad,
                        'descripcion_corta':art.descripcion_corta,
                        'descripcion_larga':art.descripcion_larga,
                        'icono':art.icono,
                        'tipo':art.tipo._get_pk_val(),
                       })      
    variables = RequestContext(request, {'form':form,
                                         'proyecto':proyect,
                                         'art':art,
#                                         'aprobado':aprobado,
                                         'abm_artefactos': 'ABM artefactos' in permisos})          
    return render_to_response('desarrollo/artefacto/mod_artefacto.html', variables)

@login_required
def definir_dependencias(request, proyecto_id, art_id, fase):
    """Definir las relaciones de un artefacto."""
    user = User.objects.get(username=request.user.username)
    p = Proyecto.objects.get(pk=proyecto_id)
    permisos = get_permisos_proyecto(user, p)
    art = get_object_or_404(Artefacto, id=art_id)
    fase_actual = Fase.objects.get(pk=fase)
    relaciones = RelArtefacto.objects.filter(hijo = art, habilitado = True)
    aux = RelArtefacto.objects.filter(padre = art, habilitado = True)
    dependientes = []
    for item in aux:
        if item.hijo.fase == fase_actual:
            dependientes.append(item.hijo)
    if request.method == 'POST':
        art = get_object_or_404(Artefacto, id=art_id)
        form = RelacionArtefactoForm(Fase.objects.get(pk=fase), art, request.POST)
        if form.is_valid():            
            cambio = False            
            
            archivos = Adjunto.objects.filter(artefacto=art, habilitado = True)
            relaciones = RelArtefacto.objects.filter(hijo = art, habilitado = True)
            relaciones_nuevas = form.cleaned_data['artefactos']
            
            lista = []
            for item in relaciones:
                if ( item.padre.fase == Fase.objects.get(pk=fase)):
                    lista.append(item.padre)
                      
            #if (lista):            
            for item in lista:
                if (item in relaciones_nuevas) == 0:
                   cambio = True
            for item in relaciones_nuevas:
                if (item in lista) == 0:
                   cambio =True
                        
            if (cambio):
                registrar_version(art, relaciones, archivos)
                                 
            for item in lista:
                auxi = RelArtefacto.objects.filter(padre = item, hijo = art)
                if auxi:
                    nuevo = auxi[0]
                    nuevo.habilitado = False
                    nuevo.save()
                
            for item in relaciones_nuevas:
                aux = RelArtefacto.objects.filter(padre = item, hijo = art)
                if aux:
                    nuevo = aux[0]
                    nuevo.habilitado = True
                    nuevo.save()
                else:
                    r = RelArtefacto()
                    r.padre = item
                    r.hijo = art
                    r.habilitado = True
                    r.save()
                    
            return HttpResponseRedirect("/proyectos/artefactos&id=" + str(p.id) + "/")
    else:
        if not validar_fase(p, fase):
            mensaje = "Se paso un parametro invalido"
            return render_to_response("desarrollo/artefacto/relacion_artefacto.html", {'mensaje': mensaje})
        dic = {}
        for item in relaciones:
            dic[item.padre.id] = True
        form = RelacionArtefactoForm(Fase.objects.get(pk=fase), art, initial = {'artefactos': dic})
        return render_to_response("desarrollo/artefacto/relacion_artefacto.html", {'form': form, 'dependientes': dependientes,
                                                                                   'user':user,
                                                                                   'art':art, 
                                                                                   'proyecto': p,
                                                                                   'abm_artefactos': 'ABM artefactos' in permisos})
        
@login_required
def ver_dependencias(request, proyecto_id, art_id, fase):
    """ver las relaciones de un artefacto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    art = get_object_or_404(Artefacto, id=art_id)
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    relaciones = RelArtefacto.objects.filter(hijo = art, habilitado = True)
    lista = []
    for item in relaciones:
        if ( item.padre.fase == Fase.objects.get(pk=fase)):
            lista.append(item.padre)
    return render_to_response("desarrollo/artefacto/ver_relacion.html", {'user': user,
                                                                         'art':art, 
                                                                         'proyecto':proyect,
                                                                         'lista':lista,
                                                                         'ver_artefactos': permiso})

@login_required
def ver_adjuntos(request, proyecto_id, art_id):
    """ver los archivos adjuntos de un artefacto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    art = get_object_or_404(Artefacto, id=art_id)
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    adjuntos = Adjunto.objects.filter(artefacto = art, habilitado = True)
    
    return render_to_response("desarrollo/artefacto/ver_adjuntos.html", {'art':art, 'user':user,
                                                                         'proyecto':proyect,
                                                                         'lista':adjuntos,
                                                                         'abm_artefactos':permiso})

@login_required
def ver_historial(request, proyecto_id, art_id):
    art = Artefacto.objects.get(pk=art_id)
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    historial = Historial.objects.get(artefacto=art)
    lista = RegistroHistorial.objects.filter(historial=historial).order_by('version')
    linea = LineaBase.objects.filter(proyectos=proyect, fase=3)
    if (linea):
        fin = 0
    else:
        fin = 1
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = RegistroHistorial.objects.filter( Q(historial=historial), Q(version__icontains = palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response('desarrollo/artefacto/historial.html', {'lista': lista, 'pag':pag,
                                                                                'user':user, 'form': form,
                                                                                'historial': historial, 
                                                                                'lista': lista,
                                                                                'art': art,
                                                                                'fin':fin,
                                                                                'proyecto': proyect,
                                                                                'abm_artefactos': permiso})
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('desarrollo/artefacto/historial.html', {'lista': lista, 'pag':pag,
                                                                      'user':user, 'form': form,'historial': historial, 
                                                                      'lista': lista,
                                                                      'art': art,
                                                                      'fin':fin,
                                                                      'proyecto': proyect,
                                                                      'abm_artefactos': permiso})

@login_required
def borrar_artefacto(request, proyecto_id, art_id):
    """Dar de baja un artefacto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    art = get_object_or_404(Artefacto, id=art_id)
    r = RelArtefacto.objects.filter(padre = art)
    if r:
        mensaje = 'Otros artefactos dependen de el que se est&aacute; tratando de eliminar.'
        return render_to_response('error.html', {'user': user, 'mensaje': mensaje})
    if request.method == 'POST':
        art.habilitado = False
        r = RelArtefacto.objects.filter(hijo = art)
        adj = Adjunto.objects.filter(artefacto = art)
        registrar_version(art, r, adj)
        for item in r:
            item.habilitado = False
            item.save()
        art.save()
        return HttpResponseRedirect("/proyectos/artefactos&id=" + str(proyecto_id)+"/")
    variables = RequestContext(request, {'proyecto':proyect, 'art': art, 'abm_artefactos': 'ABM artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/artefacto_confirm_delete.html', variables)

@login_required
def admin_artefactos_eliminados(request, proyecto_id):
    """Muestra la lista de artefactos eliminados de un proyecto."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    fase = Fase.objects.get(pk = proyect.fase.id)
    permisos = get_permisos_proyecto(user, proyect)
    lista = Artefacto.objects.filter(proyecto=proyect, fase=fase, habilitado=False)
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Artefacto.objects.filter(Q(proyecto=proyect), Q(habilitado=True), Q(tipo__in=tipoArtefactos),Q(nombre__icontains = palabra)|Q(descripcion_corta__icontains = palabra)| Q(usuario__username__icontains = palabra)|Q(estado__icontains = palabra) | Q(tipo__tipo_artefacto__nombre__icontains= palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response('desarrollo/artefacto/artefactos_eliminados.html', {'lista': lista, 'pag':pag,
                                                                        'user':user, 'form': form,
                                                                        'proyecto': proyect,
                                                                        'abm_artefactos': 'ABM artefactos' in permisos,
                                                                        })
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('desarrollo/artefacto/artefactos_eliminados.html', {'lista': lista, 'pag':pag,
                                                                        'user':user, 'form': form,
                                                                        'proyecto': proyect,
                                                                        'abm_artefactos': 'ABM artefactos' in permisos,
                                                                        })

@login_required
def admin_adjuntos(request, proyecto_id, art_id):
    """Administracion de archivos de un artefacto dado"""
    user = User.objects.get(username=request.user.username)
    art = get_object_or_404(Artefacto, id = art_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    permisos = get_permisos_proyecto(user, proyecto)
    archivos = Adjunto.objects.filter(artefacto = art, habilitado = True)
    return render_to_response('desarrollo/artefacto/adjunto/adjuntos.html', {'art':art, 'lista': archivos, 
                                                                             'proyecto': proyecto,'user':user,
                                                                             'abm_artefactos': 'ABM artefactos' in permisos})

@login_required
def adjuntos_eliminados(request, proyecto_id, art_id):
    """Administracion de archivos de un artefacto dado"""
    user = User.objects.get(username=request.user.username)
    art = get_object_or_404(Artefacto, id = art_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    permisos = get_permisos_proyecto(user, proyecto)
    archivos = Adjunto.objects.filter(artefacto = art, habilitado = False)
    return render_to_response('desarrollo/artefacto/adjunto/adjuntos_eliminados.html', {'art':art, 'lista': archivos, 
                                                                             'proyecto': proyecto,'user':user,
                                                                             'abm_artefactos': 'ABM artefactos' in permisos})

@login_required
def add_adjunto(request, proyecto_id, art_id):
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    art = get_object_or_404(Artefacto, id=art_id)
    AdjuntoFormSet = formset_factory(AdjuntoForm, extra=2)
    if request.method == 'POST':
        #form = AdjuntoForm(request.POST, request.FILES)
        formset = AdjuntoFormSet(request.POST, request.FILES)
        i=0
        if formset.is_valid():
            #for form in formset.forms:
            archivos = Adjunto.objects.filter(artefacto = art, habilitado=True)
            relaciones = RelArtefacto.objects.filter(hijo = art, habilitado=True)
            archivos_nuevos = request.FILES.values()
            
            cambio = False
            if (archivos or archivos_nuevos):
                cambio = True
                                
            if (cambio):
                registrar_version(art, relaciones, archivos)       
                
            for f in archivos_nuevos: 
                nuevo = Adjunto()
                nuevo.nombre = f.name
                nuevo.tamanho = f.size
                if f.size > 1048576:
                    mensaje = 'Tama&ntilde;o m&aacute;ximo excedido'
                    return render_to_response('error.html', {'user':user, 'mensaje':mensaje})
                nuevo.mimetype = f.content_type
                nuevo.contenido = base64.b64encode(f.read())
                nuevo.artefacto = art
                nuevo.save()
                
            return HttpResponseRedirect("/proyectos/artefactos&id="+ str(proyect.id) + "/adj&id=" + str(art_id) + "/")
        #return render_to_response('error.html', {'form': form})
    else:
        formset = AdjuntoFormSet()
        return render_to_response('desarrollo/artefacto/adjunto/crear_adjunto.html', {'formset':formset,'art':art, 
                                                                                      'user':user, 'proyecto':proyect,
                                                                                      'abm_artefactos': 'ABM artefactos' in permisos})

@login_required
def quitar_archivo(request, proyecto_id, art_id, arch_id):
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    art = get_object_or_404(Artefacto, id=art_id)
    adjunto = get_object_or_404(Adjunto, id=arch_id)
    if request.method == 'POST':
        archivos = Adjunto.objects.filter(artefacto = art, habilitado=True)
        relaciones = RelArtefacto.objects.filter(hijo = art, habilitado=True)
        registrar_version(art, relaciones, archivos)       
        adjunto.habilitado = False
        adjunto.save()
        return HttpResponseRedirect('/proyectos/artefactos&id=' + str(proyecto_id) + '/adj&id=' + str(art_id) + '/')
    else:
        return render_to_response('desarrollo/artefacto/adjunto/quitar_adjunto.html', {'art':art, 'user':user, 'proyecto':proyect,
                                                                                       'abm_artefactos': 'ABM artefactos' in permisos})
@login_required
def retornar_archivo(request, proyecto_id, art_id, arch_id):
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    art = get_object_or_404(Artefacto, id=art_id)
    adjunto = get_object_or_404(Adjunto, id=arch_id)
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    if permiso:
        if request.method == 'GET':
            respuesta = HttpResponse(base64.b64decode(adjunto.contenido), content_type= adjunto.mimetype)
            respuesta['Content-Disposition'] = 'attachment; filename=' + adjunto.nombre
            respuesta['Content-Length'] = adjunto.tamanho
            return respuesta
        mensaje = 'No se pudo traer el archivo'
        return render_to_response('error.html', {'user': user,'mensaje': mensaje})
    else:
        mensaje = 'No tiene los permisos necesarios.'
        return render_to_response('error.html', {'user': user,'mensaje':mensaje})
    return HttpResponseRedirect('proyectos/artefactos&id=' + str(art.id))

@login_required
def restaurar_archivo(request, proyecto_id, art_id, arch_id):
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    art = get_object_or_404(Artefacto, id=art_id)
    adjunto = get_object_or_404(Adjunto, id=arch_id)
    permisos = get_permisos_proyecto(user, proyect)
    if 'ABM artefactos' in permisos:
        if request.method == 'GET':
            archivos = Adjunto.objects.filter(artefacto = art, habilitado=True)
            relaciones = RelArtefacto.objects.filter(hijo = art, habilitado=True)
            registrar_version(art, relaciones, archivos) 
            adjunto.habilitado = True
            adjunto.save()
            #mensaje = 'No se pudo restaurar el archivo'
        #return render_to_response('error.html', {'mensaje': mensaje})
    else:
        mensaje = 'No tiene los permisos necesarios.'
        return render_to_response('error.html', {'user': user,'mensaje':mensaje})
    return HttpResponseRedirect('/proyectos/artefactos&id=' + str(proyecto_id) + '/adj&id=' + str(art_id) + '/')

@login_required
def restaurar_artefacto_eliminado(request, proyecto_id, art_id):
    """Metodo que restaura un artefacto eliminado a su ultima version."""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos = get_permisos_proyecto(user, proyect)
    art = get_object_or_404(Artefacto, id=art_id)
    if request.method == 'POST':
        art.habilitado = True
        art.save()
        return HttpResponseRedirect ('/proyectos/artefactos&id=' + str(proyecto_id) + '/res/')
    variables = RequestContext(request, {'proyecto':proyect, 'art': art, 'abm_artefactos': 'ABM artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/artefacto_confirm_restaurar.html', variables)


@login_required
def historial_relaciones(request, proyecto_id, art_id, reg_id, fase):
    art = Artefacto.objects.get(pk=art_id)
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    #permisos = get_permisos_proyecto(user, proyect)
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    reg = RegistroHistorial.objects.get (pk=reg_id)
    relaciones = RegHistoRel.objects.filter (registro = reg)
    lista = []
    for item in relaciones:
        if (item.art_padre.fase == Fase.objects.get(pk=fase)):
            lista.append(item.art_padre)
    variables = RequestContext(request, {'registro': reg,
                                         'lista': lista,
                                         'art': art,
                                         'proyecto': proyect,
                                         'abm_artefactos': permiso})
    return render_to_response('desarrollo/artefacto/historial_relaciones.html', variables)

@login_required
def historial_adjuntos(request, proyecto_id, art_id, reg_id):
    art = Artefacto.objects.get(pk=art_id)
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    reg = RegistroHistorial.objects.get (pk=reg_id)
    adjuntos = RegHistoAdj.objects.filter (registro = reg)
    
    variables = RequestContext(request, {'registro': reg,
                                         'lista': adjuntos,
                                         'art': art,
                                         'proyecto': proyect,
                                         'abm_artefactos': permiso})
    return render_to_response('desarrollo/artefacto/historial_adjuntos.html', variables)


@login_required
def restaurar_artefacto(request, proyecto_id, art_id, reg_id):
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    art = Artefacto.objects.get(pk = art_id)
    permisos = get_permisos_proyecto(user, proyect)
    if request.method == 'POST':
        art = Artefacto.objects.get(pk = art_id)
        relaciones = RelArtefacto.objects.filter(hijo = art,habilitado=True)
        archivos = Adjunto.objects.filter(artefacto = art,habilitado=True)
        registrar_version(art, relaciones, archivos)
        
        r = RegistroHistorial.objects.get(pk=reg_id)
        art.complejidad = r.complejidad
        art.descripcion_corta = r.descripcion_corta 
        art.descripcion_larga = r.descripcion_larga 
        art.habilitado = r.habilitado
        art.icono = r.icono
        art.tipo = r.tipo
        art.save()
        relaciones_nuevas = RegHistoRel.objects.filter(registro=r)
        archivos_nuevos = RegHistoAdj.objects.filter(registro=r)
        
        for item in relaciones:
            item.habilitado = False
            item.save()
        for item in archivos:
            item.habilitado = False
            item.save()
                
        for item in relaciones_nuevas:
            aux = RelArtefacto.objects.filter(padre = item.art_padre, hijo = item.art_hijo, habilitado = False)
            if aux:
                nuevo = aux[0]
                nuevo.habilitado = True
                nuevo.save()
                
        for item in relaciones_nuevas:
            aux = Adjunto.objects.filter(artefacto = art, habilitado = False)
            if aux:
                nuevo = aux[0]
                nuevo.habilitado = True
                nuevo.save()
                  
               
        return HttpResponseRedirect("/proyectos/artefactos&id="+ str(proyecto_id)+"/")
           
    variables = RequestContext(request,{'proyecto': proyect,
                          'art': art,
                          'abm_artefactos': 'ABM artefactos' in permisos})
    return render_to_response('desarrollo/artefacto/restaurar_version.html', variables)

@login_required
def revisar_artefacto(request, proyecto_id, art_id):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    art = Artefacto.objects.get(pk=art_id)
    permisos = get_permisos_proyecto(user, proyect)
    if request.method == 'POST':
            art.estado = 3        
            art.save()                
            return HttpResponseRedirect("/proyectos/artefactos&id=" + str(proyect.id)+"/")
    
    archivos = Adjunto.objects.filter(artefacto = art, habilitado = True)
    relaciones = RelArtefacto.objects.filter(hijo = art, habilitado = True)
    return render_to_response("desarrollo/artefacto/revisar_artefacto.html", {'proyecto':proyect, 'user':user,
                                                                              'art':art,
                                                                              'archivos':archivos,
                                                                              'relaciones':relaciones,
                                                                              'revisar_artefacto': 'Revisar artefactos' in permisos})


@login_required
def ver_detalle(request, proyecto_id, art_id):
    """Permite ver el detalle de los artefactos."""
    
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    # Validacion de permisos
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    
    art = Artefacto.objects.get(pk=art_id)
    archivos = Adjunto.objects.filter(artefacto = art, habilitado = True)
    rel_atras = RelArtefacto.objects.filter(hijo = art, habilitado = True)
    rel_adelante = RelArtefacto.objects.filter(padre = art, habilitado = True)
    lista = []
    for item in rel_atras: 
        lista.append(item.padre)
    for item in rel_adelante:
        lista.append(item.hijo)
    lista.sort(cmp=None, key=None, reverse=False)
    
    return render_to_response("desarrollo/artefacto/ver_detalle.html",
                              {'proyecto': proyect,
                               'user': user,
                               'art': art,
                               'archivos': archivos,
                               'relaciones': lista,
                               'ver_artefactos': permiso})

@login_required
def calcular_impacto(request, proyecto_id, art_id):
    """Calculo del impacto de un artefacto"""
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    art = get_object_or_404(Artefacto, id=art_id)
    permisos_ant = []
    if art.fase.id == 1:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2)) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    elif art.fase.id == 2:
        permisos_ant = get_permisos_proyecto_ant(user, proyect, art.fase) + get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
    else:
        permisos_ant = get_permisos_proyecto(user, proyect)
    permiso = 'Ver artefactos' in permisos_ant or 'ABM artefactos' in permisos_ant
    relaciones_izq = obtener_relaciones_izq(art, [])
    print relaciones_izq
    relaciones_der = obtener_relaciones_der(art, [])
    print relaciones_der
    impacto = 0
    suma_izq = 0
    suma_der = 0
    if relaciones_izq:
        for item in relaciones_izq:
            impacto = impacto + item.complejidad
            suma_izq = suma_izq + item.complejidad
            print impacto
    if relaciones_der:
        for item in relaciones_der:
            impacto = impacto + item.complejidad
            suma_der = suma_der + item.complejidad
            print impacto
    impacto = impacto - art.complejidad
    del relaciones_izq[0]
    del relaciones_der[0]  
    linea = LineaBase.objects.filter(proyectos=proyect, fase=3)
    return render_to_response("desarrollo/artefacto/complejidad.html", {'art': art, 'user': user, 'impacto': impacto,
                                                                        'izq': relaciones_izq, 'der': relaciones_der,
                                                                        'fin':linea,'suma_der': suma_der, 'suma_izq': suma_izq,
                                                                        'proyecto': proyect,
                                                                        'abm_artefactos': permiso,
                                                                        'ver_artefactos': permiso})
    
@login_required
def fases_anteriores(request, proyecto_id, fase):
    user = User.objects.get(username = request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    fase = Fase.objects.get(pk=fase)
    permisos = get_permisos_proyecto(user, proyect)
    print permisos
    
    linea1 = LineaBase.objects.filter(proyectos=proyect, fase=1)
    linea2 = LineaBase.objects.filter(proyectos=proyect, fase=2)
    linea3 = LineaBase.objects.filter(proyectos=proyect, fase=3)
   
    tipoArtefactos = TipoArtefactoFaseProyecto.objects.filter(fase=fase)
    
    permisos_ant1 = []
    permisos_ant2 = []
    permisos_ant3 = []
    if proyect.fase.id == 2:
        permisos_ant1 = get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=1))
    elif proyect.fase.id == 3:
        permisos_ant1 = get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=1))
        permisos_ant2 = get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2))
    elif(linea3):
        permisos_ant1 = get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=1))
        permisos_ant2 = get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=2))
        permisos_ant3 = get_permisos_proyecto_ant(user, proyect, Fase.objects.get(pk=3))
        
    
    lista = Artefacto.objects.filter(proyecto=proyect, habilitado=True, tipo__in=tipoArtefactos).order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Artefacto.objects.filter(Q(proyecto=proyect), Q(habilitado=True), Q(tipo__in=tipoArtefactos),Q(nombre__icontains = palabra)|Q(descripcion_corta__icontains = palabra)| Q(usuario__username__icontains = palabra)|Q(estado__icontains = palabra) | Q(tipo__tipo_artefacto__nombre__icontains= palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response("desarrollo/artefacto/Fases_anteriores.html", {'lista': lista, 'pag':pag,
                                                                             'form': form,'user': user, 
                                                                             'proyecto':proyect,'fase':fase,
                                                                              'fin':linea3,
                                                                              'abm_artefactos': 'ABM artefactos' in permisos or 'Ver artefactos' in permisos,
                                                                              'ver_artefactos_ant_1':'ABM artefactos'in permisos_ant1 or 'Ver artefactos' in permisos_ant1,
                                                                              'ver_artefactos_ant_2':'ABM artefactos'in permisos_ant2 or 'Ver artefactos' in permisos_ant2,
                                                                              'ver_artefactos_ant_3':'ABM artefactos'in permisos_ant3 or 'Ver artefactos' in permisos_ant3
                                                                              })    
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response("desarrollo/artefacto/Fases_anteriores.html", {'lista': lista, 'pag':pag,
                                                                             'form': form,'user': user, 
                                                                             'proyecto':proyect,'fase':fase,
                                                                              'fin':linea3,
                                                                              'abm_artefactos': 'ABM artefactos' in permisos or 'Ver artefactos' in permisos,
                                                                              'ver_artefactos_ant_1':'ABM artefactos'in permisos_ant1 or 'Ver artefactos' in permisos_ant1,
                                                                              'ver_artefactos_ant_2':'ABM artefactos'in permisos_ant2 or 'Ver artefactos' in permisos_ant2,
                                                                              'ver_artefactos_ant_3':'ABM artefactos'in permisos_ant3 or 'Ver artefactos' in permisos_ant3
                                                                              })    
                      
        
    
    
@login_required
def linea_base (request, proyecto_id):
    user = User.objects.get(username = request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    fase = Fase.objects.get(pk=proyect.fase.id)
    permisos = get_permisos_proyecto(user, proyect)
    if (fase.id > 1):
        fase_ant = Fase.objects.get(pk=proyect.fase.id - 1)
        tipoArtefactos_ant = TipoArtefactoFaseProyecto.objects.filter(fase=fase_ant)
        artefactos_ant = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipoArtefactos_ant, habilitado=True)    
    
    tipoArtefactos = TipoArtefactoFaseProyecto.objects.filter(fase=fase)
    artefactos = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipoArtefactos, habilitado=True)
    
    lista1 = []
    lista2 = []       
    lista3 = [] 
    msg = ""
    
    if (artefactos):        
        for item in artefactos:
            if (item.estado != 3):
                lista1.append(item)
                
            if (fase.id>1):                   
                relaciones = RelArtefacto.objects.filter(hijo=item, habilitado=True).values_list('padre', flat=True)
                if (relaciones):
                    padres = Artefacto.objects.filter(id__in = relaciones)
                    if (not tiene_padre (item, padres)):
                        lista2.append(item) 
                else:
                    lista2.append(item)
        if (fase.id > 1):       
            if (artefactos_ant):        
                for item in artefactos_ant:
                    relaciones = RelArtefacto.objects.filter(padre=item, habilitado=True).values_list('hijo', flat=True)
                    if (relaciones):
                        hijos = Artefacto.objects.filter(id__in = relaciones)
                        if (not tiene_hijo (item, hijos)):
                                lista3.append(item) 
                    else:
                        lista3.append(item)
    
        if (lista1 or lista2 or lista3):
            msg = "No se cumple con las condiciones necesarias"
        else:
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
        msg = "El proyecto no cuenta con artefactos habilitados en esta fase"
    
    fin = False
    if (fase.id == 3):
        linea = LineaBase.objects.filter(proyectos=proyect, fase=fase)        
        if (linea):
            fin = True 
            msg = "Todas las lineas base han sido generadas"
            
    return render_to_response("gestion/linea_base.html", {'lineabase': 'Generar LB' in permisos,
                                                          'abm_artefactos': 'ABM artefactos' in permisos,
                                                          'proyecto': proyect,
                                                          'user': user,
                                                          'fase': fase,
                                                          'lista': lista1,
                                                          'lista1': lista2,
                                                          'lista2': lista3,
                                                          'fin': fin,
                                                          'msg':msg })

@login_required
def linea_revisar(request, proyecto_id):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    fase = Fase.objects.get(pk=proyect.fase.id)
    permisos = get_permisos_proyecto(user, proyect)
    tipoArtefactos = TipoArtefactoFaseProyecto.objects.filter(fase=fase)
    artefactos = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipoArtefactos, habilitado=True)
    lista = []       
    if (artefactos):        
        for item in artefactos:
            if (item.estado != 3):
                lista.append(item) 
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Artefacto.objects.filter(Q(proyecto=proyect), Q(habilitado=True), Q(tipo__in=tipoArtefactos),Q(nombre__icontains = palabra)|Q(descripcion_corta__icontains = palabra)| Q(usuario__username__icontains = palabra)|Q(estado__icontains = palabra) | Q(tipo__tipo_artefacto__nombre__icontains= palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response("gestion/linea_base_revisar.html", {'lista': lista, 'pag':pag,
                                                                        'user':user, 'form': form,
                                                                        'proyecto': proyect,
                                                                        'revisar_artefacto': 'Revisar artefactos' in permisos})
    
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response("gestion/linea_base_revisar.html", {'lista': lista, 'pag':pag,
                                                                        'user':user, 'form': form,
                                                                        'proyecto': proyect,
                                                                        'revisar_artefacto': 'Revisar artefactos' in permisos})
                      

@login_required
def linea_revisar_artefacto(request, proyecto_id, art_id):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    art = Artefacto.objects.get(pk=art_id)
    permisos = get_permisos_proyecto(user, proyect)
    if request.method == 'POST':
            art.estado = 3        
            art.save()                
            return HttpResponseRedirect("/proyectos/lineabase&id=" + str(proyect.id)+"/revisar/")
    
    archivos = Adjunto.objects.filter(artefacto = art, habilitado = True)
    relaciones = RelArtefacto.objects.filter(hijo = art, habilitado = True)
    return render_to_response("gestion/linea_revisar_detalles.html", {'proyecto':proyect, 
                                                                   'user':user,
                                                                   'art':art,
                                                                   'archivos':archivos,
                                                                   'relaciones':relaciones,
                                                                   'revisar_artefacto': 'Revisar artefactos' in permisos})

@login_required
def linea_relacionar(request, proyecto_id):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    fase = Fase.objects.get(pk=proyect.fase.id)
    permisos = get_permisos_proyecto(user,proyect)
    tipoArtefactos = TipoArtefactoFaseProyecto.objects.filter(fase=fase)
    artefactos = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipoArtefactos, habilitado=True)
    lista = []       
    if (artefactos):        
        for item in artefactos:
            if (fase.id>1):                   
                relaciones = RelArtefacto.objects.filter(hijo=item, habilitado=True).values_list('padre', flat=True)
                if (relaciones):
                    padres = Artefacto.objects.filter(id__in = relaciones)
                    if (not tiene_padre (item, padres)):
                        lista.append(item) 
                else:
                    lista.append(item)   
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Artefacto.objects.filter(Q(proyecto=proyect), Q(habilitado=True), Q(tipo__in=tipoArtefactos),Q(nombre__icontains = palabra)|Q(descripcion_corta__icontains = palabra)| Q(usuario__username__icontains = palabra)|Q(estado__icontains = palabra) | Q(tipo__tipo_artefacto__nombre__icontains= palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response("gestion/linea_base_relacionar.html", {'pag':pag,'form': form,
                                                                     'proyecto': proyect,
                                                                     'user': user,
                                                                     'lista': lista,
                                                                     'abm_artefactos':'ABM artefactos' in permisos})
    
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response("gestion/linea_base_relacionar.html", {'pag':pag,'form': form,
                                                                     'proyecto': proyect,
                                                                     'user': user,
                                                                     'lista': lista,
                                                                     'abm_artefactos':'ABM artefactos' in permisos})
                               
    
           
@login_required
def linea_relacionar_artefacto(request, proyecto_id, art_id, fase):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    art = Artefacto.objects.get(pk=art_id)
    permisos = get_permisos_proyecto(user, proyect)
    fase_actual = Fase.objects.get(pk=fase)
    relaciones_padres = RelArtefacto.objects.filter(hijo = art, habilitado = True)
    relaciones_hijos = RelArtefacto.objects.filter(padre = art, habilitado = True)
    
    
    dependientes = []
    for item in relaciones_hijos:
        if item.hijo.fase == fase_actual:
            dependientes.append(item.hijo)
            
    if request.method == 'POST':
        art = get_object_or_404(Artefacto, id=art_id)
        form = RelacionArtefactoForm(Fase.objects.get(pk=fase), art, request.POST)
        if form.is_valid():            
            cambio = False                        
            archivos = Adjunto.objects.filter(artefacto=art, habilitado = True)
            relaciones = RelArtefacto.objects.filter(hijo = art, habilitado = True)
            relaciones_nuevas = form.cleaned_data['artefactos']            
            lista = []
            for item in relaciones:
                if (item.padre.fase == Fase.objects.get(pk=fase)):
                    lista.append(item.padre)            
            for item in lista:
                if (item in relaciones_nuevas) == 0:
                   cambio = True
            for item in relaciones_nuevas:
                if (item in lista) == 0:
                   cambio =True                        
            if (cambio):
                registrar_version(art, relaciones, archivos)                                 
            for item in lista:
                auxi = RelArtefacto.objects.filter(padre = item, hijo = art, habilitado = True)
                if auxi:
                    nuevo = auxi[0]
                    nuevo.habilitado = False
                    nuevo.save()                
            for item in relaciones_nuevas:
                aux = RelArtefacto.objects.filter(padre = item, hijo = art, habilitado = True)
                if aux:
                    nuevo = aux[0]
                    nuevo.habilitado = True
                    nuevo.save()
                else:
                    r = RelArtefacto()
                    r.padre = item
                    r.hijo = art
                    r.habilitado = True
                    r.save()                    
            return HttpResponseRedirect("/proyectos/lineabase&id=" + str(proyect.id)+"/relacionar/")
    else:
        if not validar_fase(proyect, fase):
            mensaje = "Se paso un parametro invalido"
            return render_to_response("gestion/linea_base_relaciones.html", {'mensaje': mensaje})
        dic = {}
        for item in relaciones_padres:
            dic[item.padre.id] = True
        form = RelacionArtefactoForm(Fase.objects.get(pk=fase), art, initial = {'artefactos': dic})
        return render_to_response("gestion/linea_base_relaciones.html", {'form': form, 
                                                                         'dependientes': dependientes,
                                                                        'user':user,
                                                                        'art':art, 
                                                                        'proyecto': proyect,
                                                                        'abm_artefactos': 'ABM artefactos' in permisos})

@login_required
def linea_anteriores(request, proyecto_id):
    """Asigna roles de sistema a un usuario"""
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(id=proyecto_id)
    fase = Fase.objects.get(pk=proyect.fase.id)
    permisos = get_permisos_proyecto(user, proyect)
    if (fase.id > 1):
        fase_ant = Fase.objects.get(pk=proyect.fase.id - 1)
        tipoArtefactos_ant = TipoArtefactoFaseProyecto.objects.filter(fase=fase_ant)
        artefactos_ant = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipoArtefactos_ant, habilitado=True)  
        
    tipoArtefactos = TipoArtefactoFaseProyecto.objects.filter(fase=fase)
    artefactos = Artefacto.objects.filter(proyecto=proyect, tipo__in=tipoArtefactos, habilitado=True)
    lista = []       
    if (artefactos):    
        if (fase.id > 1):       
            if (artefactos_ant):        
                for item in artefactos_ant:
                    relaciones = RelArtefacto.objects.filter(padre=item, habilitado=True).values_list('hijo', flat=True)
                    if (relaciones):
                        hijos = Artefacto.objects.filter(id__in = relaciones)
                        if (not tiene_hijo (item, hijos)):
                                lista.append(item) 
                    else:
                        lista.append(item)   
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Artefacto.objects.filter(Q(proyecto=proyect), Q(habilitado=True), Q(tipo__in=tipoArtefactos),Q(nombre__icontains = palabra)|Q(descripcion_corta__icontains = palabra)| Q(usuario__username__icontains = palabra)|Q(estado__icontains = palabra) | Q(tipo__tipo_artefacto__nombre__icontains= palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            pag = page_excepcion1(request, paginator)
            return render_to_response("gestion/linea_base_anteriores.html", {'pag':pag,'form': form,
                                                                     'proyecto': proyect,
                                                                   'user': user,
                                                                   'lista': lista,
                                                                   'abm_artefactos': 'ABM artefactos' in permisos})  
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response("gestion/linea_base_anteriores.html", {'pag':pag,'form': form,
                                                                     'proyecto': proyect,
                                                                   'user': user,
                                                                   'lista': lista,
                                                                   'abm_artefactos': 'ABM artefactos' in permisos})  
    
    
@login_required
def reporte_artefacto(request, proyecto_id, fase):
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    fase = get_object_or_404(Fase, id=fase)
    tipoArtefactos = TipoArtefactoFaseProyecto.objects.filter(proyecto = proyect, fase = fase)
    artefactos = Artefacto.objects.filter(proyecto=proyect, habilitado=True, tipo__in=tipoArtefactos).order_by('id')
    resp = HttpResponse(mimetype='application/pdf')
    report = ReporteArtefacto(queryset=artefactos)
    report.generate_by(PDFGenerator, filename=resp)
    return resp

@login_required
def reporte_artefactos(request, proyecto_id):
    user = User.objects.get(username=request.user.username)
    proyect = get_object_or_404(Proyecto, id=proyecto_id)
    artefactos = Artefacto.objects.filter(proyecto=proyect, habilitado=True).order_by('id')
    resp = HttpResponse(mimetype='application/pdf')
    report = ReporteArtefacto(queryset=artefactos)
    report.generate_by(PDFGenerator, filename=resp)
    return resp
 
@login_required
def reporte_usuario(request):
    user = User.objects.get(username=request.user.username)
    usuarios = User.objects.order_by('id')
    resp = HttpResponse(mimetype='application/pdf')
    report = ReporteUsuario(queryset=usuarios)
    report.generate_by(PDFGenerator, filename=resp)
    return resp    

@login_required
def reporte_proyecto(request):
    user = User.objects.get(username=request.user.username)
    proyectos = Proyecto.objects.order_by('id')
    resp = HttpResponse(mimetype='application/pdf')
    report = ReporteProyecto(queryset=proyectos)
    report.generate_by(PDFGenerator, filename=resp)
    return resp

@login_required
def reporte_rol(request, cat):
    user = User.objects.get(username=request.user.username)
    roles = Rol.objects.filter(categoria=cat).order_by('id')
    resp = HttpResponse(mimetype='application/pdf')
    report = ReporteRol(queryset=roles)
    report.generate_by(PDFGenerator, filename=resp)
    return resp

@login_required
def reporte_historial(request, proyecto_id, art_id):
    art = Artefacto.objects.get(pk=art_id)
    user = User.objects.get(username=request.user.username)
    proyect = Proyecto.objects.get(pk=proyecto_id)
    historial = Historial.objects.get(artefacto=art)
    versiones = RegistroHistorial.objects.filter(historial=historial).order_by('version')
    resp = HttpResponse(mimetype='application/pdf')
    report = ReporteHistorial(queryset=versiones)
    report.generate_by(PDFGenerator, filename=resp)
    return resp

@login_required
def terminar(peticion):
    """Muestra una pagina de confirmacion de exito"""
    return render_to_response('operacion_exitosa.html');

def login_redirect(request):
    """Redirige de /accounts/login a /login."""
    return HttpResponseRedirect('/login')

def logout_pagina(request):
    """Pagina de logout"""
    try:
        del request.session['nro_items']
    except KeyError:
        pass

    logout(request)
    return HttpResponseRedirect('/login')
