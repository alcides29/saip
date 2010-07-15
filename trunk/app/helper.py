from saip.app.models import *
import datetime

def validar_fase(proyecto, fase):
    print proyecto.fase.id
    print fase
    if proyecto.fase.id == 1: 
        if int(fase) == 2 or int(fase) == 3: return False;
        return True
    if proyecto.fase.id == 2:
        if int(fase) == 1 or int(fase) == 2: return True
        return False
    if proyecto.fase.id == 3:
        if int(fase) == 2 or int(fase) == 3: return True
        return False
    return False

def obtener_relaciones_izq(art, lista_existentes):
    relaciones = RelArtefacto.objects.filter(hijo = art, habilitado = True)
    if art.id in lista_existentes:
        return None
    ret = [art]
    lista_existentes.append(art.id)
    if relaciones:
        for item in relaciones:
            aux = obtener_relaciones_izq(item.padre, lista_existentes)
            if aux:
                ret.extend(aux)
    return ret

def obtener_relaciones_der(art, lista_existentes):
    relaciones = RelArtefacto.objects.filter(padre = art, habilitado = True)
    if art.id in lista_existentes:
        return None
    ret = [art]
    lista_existentes.append(art.id)
    if relaciones:
        for item in relaciones:
            aux = obtener_relaciones_der(item.hijo, lista_existentes)
            if aux:
                ret.extend(aux)
    return ret

def get_permisos_proyecto(user, proyecto):
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.filter(rolpermiso__fase = proyecto.fase))
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    return permisos
	
def get_permisos_proyecto_ant(user, proyecto, fase):
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.filter(rolpermiso__fase = fase))
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    return permisos

def get_permisos_sistema(user):
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for item in roles:
        permisos_obj.extend(item.rol.permisos.all())
    permisos = []
    for item in permisos_obj:
        permisos.append(item.nombre)
    return permisos

def registrar_version(art, relaciones, archivos):
    """Se ingresa la version antigua al registro"""
    reg = RegistroHistorial()
    reg.version = art.version
    reg.estado = art.estado
    reg.complejidad = art.complejidad
    reg.descripcion_corta = art.descripcion_corta
    reg.descripcion_larga = art.descripcion_larga
    reg.habilitado = art.habilitado
    reg.icono = art.icono
    reg.tipo = art.tipo
    reg.fecha_modificacion = datetime.datetime.today()
    historial = Historial.objects.get(artefacto = art)
    reg.historial = historial
    reg.save()
    if (relaciones):
        for item in relaciones:
            nuevo = RegHistoRel()
            nuevo.art_padre = item.padre
            nuevo.art_hijo = item.hijo
            nuevo.registro = reg
            nuevo.save()
    if (archivos):
        for item in archivos:
            adj = RegHistoAdj()
            adj.nombre = item.nombre
            adj.contenido = item.contenido
            adj.tamanho = item.tamanho
            adj.mimetype = item.mimetype
            adj.artefacto = art
            adj.registro = reg
            adj.save()
    """Se cambia el estado del artefacto"""
    art.estado = 2            
    """Se incrementa la version actual"""
    art.version = art.version + 1
    art.save()           

def tiene_padre (hijo, padres):
    for item in padres:
        if (item.fase.id == hijo.fase.id - 1):
            return True
        else:
            relaciones = RelArtefacto.objects.filter(hijo=item, habilitado=True).values_list('padre', flat=True)
            if (relaciones):
                padres = Artefacto.objects.filter(id__in = relaciones)
                return tiene_padre (item, padres)
    return False

def tiene_hijo (padre, hijos):
    for item in hijos:
        if (item.fase.id == padre.fase.id + 1):
            return True
        else:
            relaciones = RelArtefacto.objects.filter(padre=item, habilitado=True).values_list('hijo', flat=True)
            if (relaciones):
                hijos = Artefacto.objects.filter(id__in = relaciones)
                return tiene_hijo (item, hijos)
    return False