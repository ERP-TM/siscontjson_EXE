from nicegui import ui


from .base_view import (
    mostrar_tabla_base,
    procesar_tabla_individual_base,
    procesar_todas_tablas_base,
    render_module_ui,
    descargar_csv,
    descargar_csv_js
)
from services.activos_fijos_client import TABLAS_ACTIVOS, TABLAS_ACTIVOS_CSV, obtener_datos_tabla


    




# 1. Adaptar las funciones base a General
async def mostrar_tabla(nombre_logico: str):
    await mostrar_tabla_base(nombre_logico, obtener_datos_tabla)

async def procesar_tabla_individual(nombre_logico: str):
    await procesar_tabla_individual_base(
        nombre_logico, obtener_datos_tabla, TABLAS_ACTIVOS
    )

async def procesar_todas_tablas():
    await procesar_todas_tablas_base(TABLAS_ACTIVOS, procesar_tabla_individual)


async def descargar_csv_js_custom(nombre_logico: str):
    await mostrar_dialogo(nombre_logico)
    

async def mostrar_dialogo(nombre_logico: str):
    with ui.dialog() as dialog, ui.card():
        ui.label('Ingrese las siglas de la empresa').classes('text-h6')
        
        # Entrada de texto
        entrada_texto = ui.input('Siglas',
                                 placeholder='Escriba aquí...')
        
        # Botones de acción
        with ui.row().classes('justify-end'):
            ui.button('Cancelar', on_click=dialog.close)
            ui.button('Aceptar', on_click=lambda: procesar_texto(entrada_texto.value, nombre_logico, dialog))
    
    dialog.open()

async def procesar_texto(texto, nombre, dialog):
    if texto:
        ui.notify(f'Texto ingresado: {texto}', type='positive')
        await descargar_csv_js(nombre, "activos_fijos", TABLAS_ACTIVOS_CSV, siglas=texto)
    else:
        ui.notify('No se ingresó ningún texto', type='warning')
        await descargar_csv_js(nombre, "activos_fijos", TABLAS_ACTIVOS_CSV)
    
    dialog.close()

# 2. Reemplazar la función 'show' con el renderizador base
def show():
    render_module_ui(
        titulo="Activos Fijos",
        subtitulo='Consulta y genera los JSON de las tablas del modulo "Activos Fijos"',
        tablas_map=TABLAS_ACTIVOS,
        tablas_map_csv=TABLAS_ACTIVOS_CSV,
        mostrar_func=mostrar_tabla,
        exportar_individual_func=procesar_tabla_individual,
        exportar_todas_func=procesar_todas_tablas,
        descargar_csv_func=descargar_csv_js_custom
    )
    

