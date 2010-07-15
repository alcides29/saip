from geraldo import Report, landscape, ReportBand, ObjectValue, SystemField,\
        BAND_WIDTH, Label

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER


class ReporteArtefacto(Report):
    title = 'Lista de Artefactos'

    page_size = landscape(A5)
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_begin(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='', top=0.1*cm,
                left=8*cm),
        ]

    class band_detail(ReportBand):
        height = 0.5*cm
        elements=(
            ObjectValue(attribute_name='id', top=0, left=0.5*cm),
            ObjectValue(attribute_name='nombre', top=0, left=2*cm),
            ObjectValue(attribute_name='proyecto', top=0, left=4*cm),
            ObjectValue(attribute_name='complejidad', top=0, left=6*cm),
            ObjectValue(attribute_name='descripcion_corta', top=0, left=7*cm),
            ObjectValue(attribute_name='descripcion_larga', top=0, left=11*cm),
            )
       
    class band_page_header(ReportBand):
        height = 1.2*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="ID", top=0.8*cm, left=0.5*cm),
            Label(text=u"Nombre", top=0.8*cm, left=2*cm),
            Label(text=u"Proyecto", top=0.8*cm, left=4*cm),
            Label(text=u"Complej.", top=0.8*cm, left=5.5*cm),
            Label(text=u"Descrip_corta", top=0.8*cm, left=7*cm),
            Label(text=u"Descrip_larga", top=0.8*cm, left=11*cm),
            SystemField(expression=u'Page %(page_number)d of %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='SAIP Reports', top=0.1*cm),
            SystemField(expression=u'Printed in %(now:%Y, %b %d)s at %(now:%H:%M)s', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'top': True}
        
class ReporteProyecto(Report):
    title = 'Lista de Proyectos'

    page_size = landscape(A5)
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_begin(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='', top=0.1*cm,
                left=8*cm),
        ]

    class band_detail(ReportBand):
        height = 0.5*cm
        elements=(
            ObjectValue(attribute_name='id', top=0, left=0.5*cm),
            ObjectValue(attribute_name='nombre', top=0, left=2.5*cm),
            ObjectValue(attribute_name='usuario_lider', top=0, left=4.5*cm),
            ObjectValue(attribute_name='descripcion', top=0, left=6*cm),
            ObjectValue(attribute_name='fecha_inicio', top=0, left=12*cm),
            ObjectValue(attribute_name='fecha_fin', top=0, left=15*cm),
            )
       
    class band_page_header(ReportBand):
        height = 1.2*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="ID", top=0.8*cm, left=0.5*cm),
            Label(text=u"Nombre", top=0.8*cm, left=2.5*cm),
            Label(text=u"Lider", top=0.8*cm, left=4.5*cm),
            Label(text=u"Descripcion", top=0.8*cm, left=6*cm),
            Label(text=u"Inicio", top=0.8*cm, left=12*cm),
            Label(text=u"Fin", top=0.8*cm, left=15*cm),
            SystemField(expression=u'Page %(page_number)d of %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='SAIP Reports', top=0.1*cm),
            SystemField(expression=u'%(now:%Y, %b %d)s  %(now:%H:%M)s', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'top': True}

class ReporteUsuario(Report):
    title = 'Lista de Usuarios'

    page_size = landscape(A5)
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_begin(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='', top=0.1*cm,
                left=8*cm),
        ]

    class band_detail(ReportBand):
        height = 0.5*cm
        elements=(
            ObjectValue(attribute_name='id', top=0, left=0.5*cm),
            ObjectValue(attribute_name='username', top=0, left=2.5*cm),
            ObjectValue(attribute_name='first_name', top=0, left=4.5*cm),
            ObjectValue(attribute_name='last_name', top=0, left=6.5*cm),
            ObjectValue(attribute_name='email', top=0, left=8.5*cm),
            )
       
    class band_page_header(ReportBand):
        height = 1.2*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="ID", top=0.8*cm, left=0.5*cm),
            Label(text=u"usuario", top=0.8*cm, left=2.5*cm),
            Label(text=u"Nombre", top=0.8*cm, left=4.5*cm),
            Label(text=u"Apellido", top=0.8*cm, left=6.5*cm),
            Label(text=u"Email", top=0.8*cm, left=8.5*cm),
            SystemField(expression=u'Page %(page_number)d of %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'bottom': True}

class ReporteRol(Report):
    title = 'Lista de Roles'

    page_size = landscape(A5)
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_begin(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='', top=0.1*cm,
                left=8*cm),
        ]

    class band_detail(ReportBand):
        height = 1*cm
        elements=(
            ObjectValue(attribute_name='id', top=0, left=0.5*cm),
            ObjectValue(attribute_name='nombre', top=0, left=1.5*cm),
            ObjectValue(attribute_name='categoria', top=0, left=5*cm),
            ObjectValue(attribute_name='descripcion', top=0, left=6.5*cm),
            ObjectValue(attribute_name='fecHor_creacion', top=0, left=12*cm),
            ObjectValue(attribute_name='usuario_creador', top=0, left=16.5*cm),
            )
       
    class band_page_header(ReportBand):
        height = 1.2*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="ID", top=0.8*cm, left=0.5*cm),
            Label(text=u"Nombre", top=0.8*cm, left=1.5*cm),
            Label(text=u"Categoria", top=0.8*cm, left=4.5*cm),
            Label(text=u"Descripcion", top=0.8*cm, left=6.5*cm),
            Label(text=u"Fecha/Creacion", top=0.8*cm, left=12*cm),
            Label(text=u"Usuario/Creador", top=0.8*cm, left=16.5*cm),
            SystemField(expression=u'Page %(page_number)d of %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'bottom': True}
        
class ReporteHistorial(Report):
    title = 'Historial'

    page_size = landscape(A5)
    margin_left = 1*cm
    margin_top = 1*cm
    margin_right = 1*cm
    margin_bottom = 1*cm
    
    class band_begin(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='', top=0.1*cm,
                left=8*cm),
        ]

    class band_detail(ReportBand):
        height = 0.5*cm
        elements=(
            ObjectValue(attribute_name='id', top=0, left=0.5*cm),
            ObjectValue(attribute_name='version', top=0, left=1.5*cm),
            ObjectValue(attribute_name='complejidad', top=0, left=3.5*cm),
            ObjectValue(attribute_name='descripcion_corta', top=0, left=5*cm),
            ObjectValue(attribute_name='descripcion_larga', top=0, left=9*cm),
            ObjectValue(attribute_name='fecha_modificacion', top=0, left=14*cm),
            )
       
    class band_page_header(ReportBand):
        height = 1.2*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="ID", top=0.8*cm, left=0.5*cm),
            Label(text=u"Version", top=0.8*cm, left=1.5*cm),
            Label(text=u"Complej.", top=0.8*cm, left=3*cm),
            Label(text=u"Descrip_corta", top=0.8*cm, left=5*cm),
            Label(text=u"Descrip_larga", top=0.8*cm, left=9*cm),
            Label(text=u"Fecha/Modificacion", top=0.8*cm, left=14*cm),
            SystemField(expression=u'Page %(page_number)d of %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='SAIP Reports', top=0.1*cm),
            SystemField(expression=u'Printed in %(now:%Y, %b %d)s at %(now:%H:%M)s', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
            ]
        borders = {'top': True}