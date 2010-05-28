from saip.app.models import *

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

def obtener_relaciones_izq(art):
    relaciones = RelArtefacto.objects.filter(hijo = art)
    if relaciones:
        ret =[]
        for item in relaciones:
            aux = obtener_relaciones_izq(item.padre)
            if aux:
                ret.extend(aux)
        return ret
    else: 
        return [art]

def obtener_relaciones_der(art):
    relaciones = RelArtefacto.objects.filter(padre = art)
    if relaciones:
        ret =[]
        for item in relaciones:
            aux = obtener_relaciones_der(item.hijo)
            if aux:
                ret.extend(aux)
        return ret
    else: 
        return [art]
