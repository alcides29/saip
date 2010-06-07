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
    ret = [art]
    if relaciones:
        if art.id in lista_existentes:
            return None
        lista_existentes.append(art.id)
        for item in relaciones:
            aux = obtener_relaciones_izq(item.padre, lista_existentes)
            if aux:
                ret.extend(aux)
    return ret

def obtener_relaciones_der(art, lista_existentes):
    relaciones = RelArtefacto.objects.filter(padre = art, habilitado = True)
    ret = [art]
    if relaciones:
        if art.id in lista_existentes:
            return None
        lista_existentes.append(art.id)
        for item in relaciones:
            aux = obtener_relaciones_der(item.hijo, lista_existentes)
            if aux:
                ret.extend(aux)
    return ret

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
