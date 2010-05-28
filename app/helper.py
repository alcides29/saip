
def validar_fase(proyecto, fase):
    if proyecto.fase.id == 1: 
        if fase == 2 or fase ==3: return false;
        return True
    if proyecto.fase.id == 2:
        if fase == 1 or fase == 2: return True
        return False
    if proyecto.fase.id == 3:
        if fase == 2 or fase == 3: return True
        return False
    return False