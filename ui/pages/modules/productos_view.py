# Importar el módulo base
from .base_view import (
    mostrar_tabla_base,
    procesar_tabla_individual_base,
    procesar_todas_tablas_base,
    descargar_csv_js,
    render_module_ui,
)

# Importar solo lo necesario del cliente específico
from services.productos_client import TABLAS_PRODUCTOS,TABLAS_PRODUCTOS_CSV, obtener_datos_tabla


# 1. Adaptar las funciones base a General
async def mostrar_tabla(nombre_logico: str):
    async def datos_view(nombre):
        return await obtener_datos_tabla(nombre, export=False)
    await mostrar_tabla_base(nombre_logico, obtener_datos_tabla)


async def procesar_tabla_individual(nombre_logico: str):
    async def datos_export(nombre: str):
        return await obtener_datos_tabla(nombre, export=True)
    await procesar_tabla_individual_base(
        nombre_logico, obtener_datos_tabla, TABLAS_PRODUCTOS)


async def procesar_todas_tablas():
    # Pasa obtener_datos_tabla directamente para que la función base maneje la exportación
    async def datos_export(nombre: str):
        return await obtener_datos_tabla(nombre, export=True)
    await procesar_todas_tablas_base(TABLAS_PRODUCTOS, datos_export, "Productos")


async def descargar_csv_js_custom(nombre_logico: str):
    await descargar_csv_js(nombre_logico, "producto", TABLAS_PRODUCTOS_CSV)
#
# async def descargar_csv(nombre_logico: str):
#     await descargar_csv_base(nombre_logico, obtener_datos_tabla, TABLAS_PRODUCTOS)

# 2. Reemplazar la función 'show' con el renderizador base
def show():
    render_module_ui(
        titulo="Productos",
        subtitulo='Consulta y genera los JSON de las tablas del modulo "Productos"',
        tablas_map=TABLAS_PRODUCTOS,
        tablas_map_csv=TABLAS_PRODUCTOS_CSV,
        mostrar_func=mostrar_tabla,
        exportar_individual_func=procesar_tabla_individual,
        exportar_todas_func=procesar_todas_tablas,
        descargar_csv_func=descargar_csv_js_custom,
    )