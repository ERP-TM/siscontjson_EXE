# ui/pages/modules/base_view.py

import asyncio
import json
import csv
import io

from collections import OrderedDict
from nicegui.functions import javascript
from nicegui import ui, app
from utils.download_manager import save_to_download_cache

from collections import OrderedDict
from io import StringIO, BytesIO
from fastapi.responses import JSONResponse, StreamingResponse

from services.cp_client import get_current_conexion_params


# --- Funciones de Utilidad ---


def _generate_json_string(data_list: list, doctype: str) -> str:
    """
    Genera el contenido JSON como un string con la estructura de exportación
    Reemplaza la función idéntica en ambas vistas.
    """
    content = OrderedDict()
    content["doctype"] = doctype
    content["data"] = data_list
    return json.dumps(content, indent=4, ensure_ascii=False)


# --- Lógica de Visualización ---


async def mostrar_tabla_base(nombre_logico: str, obtener_datos_func):
    """
    Función base para mostrar datos de una tabla en un diálogo.
    Acepta 'obtener_datos_func' como una función asíncrona para obtener datos específicos del módulo.
    """
    try:
        # Obtener datos usando la función específica del cliente
        result = await obtener_datos_func(nombre_logico)
        records = result["data"]
        doctype_name = result["doctype"]

        # ui.notify(f"{nombre_logico} consultado correctamente.")

        if not records or not all(isinstance(r, dict) for r in records):
            ui.notify(f"No hay datos para mostrar en {nombre_logico}", type="warning")
            return

        # Lógica de NiceGUI para mostrar tabla (idéntica en ambas vistas)
        columns = [
            {"name": key, "label": key, "field": key, "align": "left"}
            for key in records[0].keys()
        ]

        data_length = len(records)
        pagination = (
            {"rows_per_page": min(10, data_length)}
            if data_length > 10
            else {"rows_per_page": data_length}
        )

        column_count = len(columns)
        card_classes = "w-full h-full max-h-screen "
        card_classes += (
            "min-w-[90vw] max-w-none" if column_count > 8 else "max-w-screen-xl"
        )

        with ui.dialog() as dialog:
            with ui.card().classes(card_classes):
                ui.label(f"Datos de {nombre_logico}").classes("text-lg font-bold")

                async def show_json_dump():
                    json_str = _generate_json_string(records, doctype_name)

                    with ui.dialog() as json_dialog:
                        with ui.card().classes("w-[80vw] max-w-none"):
                            ui.label(f"JSON Raw de {nombre_logico}").classes(
                                "text-lg font-bold"
                            )
                            ui.markdown(f"```json\n{json_str}\n```").classes(
                                "overflow-auto max-h-[70vh] bg-gray-100 p-4 rounded"
                            )
                            ui.button("Cerrar", on_click=json_dialog.close)
                    json_dialog.open()

                ui.button("Ver JSON Raw", on_click=show_json_dump).props(
                    "color=info size=sm outline icon=code"
                )

                ui.table(columns=columns, rows=records, pagination=pagination).classes(
                    "w-full h-full overflow-x-auto"
                )

                ui.button("Cerrar", on_click=dialog.close)
        dialog.open()

    except Exception as e:
        ui.notify(f"Error al consultar {nombre_logico}: {e}", type="negative")
        print(f"Error al consultar {nombre_logico}: {e}")


# --- Lógica de Exportación ---


async def procesar_tabla_individual_base(
    nombre_logico: str, obtener_datos_func, tablas_map
):
    """
    Función base para exportar datos individuales.
    Acepta la función de obtener datos y el diccionario de mapeo de tablas.
    """
    try:
        # ui.notify(f"Preparando descarga de {nombre_logico}...")
        result = await obtener_datos_func(nombre_logico)

        if not result or not result.get("data"):
            ui.notify(
                f"No hay artículos para exportar en {nombre_logico}.", type="warning"
            )
            return

        # 1. Obtener nombre real del archivo del mapa específico
        sqlserver_name = tablas_map.get(nombre_logico, "error_nombre_tabla")
        if sqlserver_name == "error_nombre_tabla":
            ui.notify(
                f"Error: Mapeo no encontrado para '{nombre_logico}'.", type="negative"
            )
            return

        # 2. Preparar los datos (Bytes)
        json_str = _generate_json_string(result["data"], result["doctype"])
        json_bytes = json_str.encode("utf-8")
        file_name = f"{sqlserver_name}.json"

        download_url = save_to_download_cache(json_bytes, file_name)

        ui.run_javascript(f'window.location.href = "{download_url}"')

        # ui.notify(f"Descargando {file_name}...", type="positive")

    except Exception as e:
        ui.notify(f"Error al exportar {nombre_logico}: {e}", type="negative")
        print(f"Error al exportar {nombre_logico}: {e}")


async def procesar_todas_tablas_base(
    tablas_map, obtener_datos_func, nombre_modulo: str = "export"
):
    """
    Función base para exportar todas las tablas como un ZIP descargable.
    Crea un ZIP en memoria con todos los JSON y lo descarga via navegador.
    """
    import zipfile
    import time
    # 1. Mostrar diálogo de progreso
    with ui.dialog() as dialog, ui.card():
        ui.label("Exportando todas las tablas...").classes("text-lg font-semibold")

    progreso_label = ui.label("Iniciando...").classes("text-sm mt-2")
    ui.spinner(size="lg", color="green")

    dialog.open()

    try:
        total_tablas = len(tablas_map)
        exportadas = 0
        errores = []

        # Crear archivo ZIP en memoria
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Itera sobre el mapa de tablas específico
            for idx, nombre_logico in enumerate(tablas_map.keys(), 1):
                try:
                    progreso_label.set_text(
                        f"Exportando {nombre_logico} ({idx}/{total_tablas})..."
                    )

                    # Obtener datos
                    result = await obtener_datos_func(nombre_logico)

                    if not result or not result.get("data"):
                        errores.append(f"{nombre_logico}: Sin datos")
                        continue

                    # Obtener nombre real del archivo del mapa
                    sqlserver_name = tablas_map.get(nombre_logico, "error_nombre_tabla")
                    if sqlserver_name == "error_nombre_tabla":
                        errores.append(f"{nombre_logico}: Error de mapeo")
                        continue

                    # Generar JSON y agregar al ZIP
                    json_str = _generate_json_string(result["data"], result["doctype"])
                    file_name = f"{sqlserver_name}.json"

                    zipf.writestr(file_name, json_str)
                    exportadas += 1

                except Exception as e:
                    errores.append(f"{nombre_logico}: {str(e)}")
                    print(f"Error al exportar {nombre_logico}: {e}")

                await asyncio.sleep(0.01)

        # Preparar descarga del ZIP
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.getvalue()

        # Nombre del ZIP con nombre del módulo y timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Normalizar nombre del módulo (quitar espacios y caracteres especiales)
        nombre_modulo_clean = (
            nombre_modulo.replace(" ", "_").replace("/", "_").replace("\\", "_")
        )
        zip_filename = f"{nombre_modulo_clean}_{timestamp}.zip"

        download_url = save_to_download_cache(zip_bytes, zip_filename)
        ui.run_javascript(f'window.location.href = "{download_url}"')

        dialog.close()

        # Mensaje de éxito al finalizar
        if exportadas == total_tablas:
            ui.notify(
                f"✅ {exportadas} tablas exportadas exitosamente",
                type="positive",
                timeout=5000,            )
        elif exportadas > 0:
            ui.notify(
                f"⚠️ {exportadas} de {total_tablas} tablas exportadas. Algunas tuvieron errores.",
                type="warning",
                timeout=5000,
            )
        else:
            ui.notify(
                "❌ No se pudo exportar ninguna tabla", type="negative", timeout=5000
            )

        if errores:
            print("Errores de exportación:", errores)
            await asyncio.sleep(0.5)

    except Exception as e:
        dialog.close()
        ui.notify(f"❌ Error al exportar: {str(e)}", type="negative")
        print(f"Error general en exportación: {e}")

async def descargar_csv_base(nombre_logico: str, obtener_datos_func, tablas_map):
    """
    Función base para exportar datos individuales a CSV.
    Acepta la función de obtener datos y el diccionario de mapeo de tablas (TABLAS_NOMINA/GENERAL).
    """
    try:
        # ui.notify(f"Preparando descarga de {nombre_logico}...")
        result = await obtener_datos_func(nombre_logico)

        if not result or not result.get("data"):
            ui.notify(
                f"No hay artículos para exportar en {nombre_logico}.", type="warning"
            )
            return

        # 1. Obtener nombre real del archivo del mapa específico
        sqlserver_name = tablas_map.get(nombre_logico, "error_nombre_tabla")
        if sqlserver_name == "error_nombre_tabla":
            ui.notify(
                f"Error: Mapeo no encontrado para '{nombre_logico}'.", type="negative"
            )
            return

        # 2. Preparar los datos para el archivo CSV
        data = result["data"]

        if not data:
            ui.notify(
                f"No hay artículos para exportar en {nombre_logico}.", type="warning"
            )
            return

        # Obtener las cabeceras (suponiendo que los datos son una lista de diccionarios)
        headers = data[0].keys()

        # Crear el archivo CSV en memoria
        csv_bytes = io.StringIO()
        writer = csv.DictWriter(csv_bytes, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

        # Obtener el contenido CSV como bytes
        csv_bytes.seek(0)  # Volver al principio del archivo
        file_name = f"{sqlserver_name}.csv"

        # Guardar en el caché de descargas (deberás implementar esta función)
        csv_data = csv_bytes.getvalue().encode('utf-8')

        download_url = save_to_download_cache(csv_data, file_name)

        ui.run_javascript(f'window.location.href = "{download_url}"')

        ui.notify(f"Descargando {file_name}...", type="positive")

    except Exception as e:
        ui.notify(f"Error al exportar {nombre_logico}: {e}", type="negative")
        print(f"Error al exportar {nombre_logico}: {e}")


# Otros elementos necesarios (como ui y save_to_download_cache) deben ser implementados según tu contexto.

async def descargar_csv(nombre_logico: str, obtener_datos_func, tablas_map):
    """
    Función base para exportar datos individuales a CSV.
    Acepta la función de obtener datos y el diccionario de mapeo de tablas (TABLAS_NOMINA/GENERAL).
    """
    try:
        ui.notify(f"Preparando descarga de {nombre_logico}...")

        # 1. Obtener nombre real del archivo del mapa específico
        sqlserver_name = tablas_map.get(nombre_logico, "error_nombre_tabla")
        if sqlserver_name == "error_nombre_tabla":
            ui.notify(
                f"Error: Mapeo no encontrado para '{nombre_logico}'.", type="negative"
            )
            return

        df = await obtener_datos_func(nombre_logico)

        file_name = f"{sqlserver_name}.csv"

        csv_bytes = BytesIO()
        df.to_csv(csv_bytes, index=False, encoding='utf-8')
        csv_bytes.seek(0)  # Volver al inicio del stream


        # Guardar en el caché de descargas (deberás implementar esta función)
        csv_data = csv_bytes.getvalue().encode('utf-8')

        download_url = save_to_download_cache(csv_data, file_name)

        ui.run_javascript(f'window.location.href = "{download_url}"')

        ui.notify(f"Descargando {file_name}...", type="positive")

    except Exception as e:
        ui.notify(f"Error al exportar {nombre_logico}: {e}", type="negative")
        print(f"Error al exportar {nombre_logico}: {e}")

async def descargar_csv_js(nombre_logico:str, module:str, TABLAS_CSV, **kargs):

    try:
        ui.notify(f"Preparando descarga de {nombre_logico}...")

        conexion_params = get_current_conexion_params()
        payload = conexion_params.model_dump()
        #Adiciono los argunmentos adicionales en el payload
        for k in kargs.keys(): 
            payload[k] = kargs[k]
        payload_json = json.dumps(payload)        

        js = f"""fetch('/api/{module}/{TABLAS_CSV[nombre_logico]}',{{
                method: 'POST',
                headers: {{'Content-Type': 'application/json', 'Accept': 'text/csv'}},
                body: JSON.stringify({payload_json})
                }}).then(response => {{
                        if (!response.ok) {{
                            // Mejor mensaje de error con status
                            throw new Error('Error HTTP ${{response.status}}: ${{response.statusText}}');
                        }}
                        
                        // Verificar que la respuesta sea CSV
                        const contentType = response.headers.get('content-type');
                        if (!contentType || !contentType.includes('csv')) {{
                            throw new Error('La respuesta no es un CSV válido');
                        }}
                        
                        return response.blob();
                    }})
                    .then(blob => {{ 
                        // Verificar que el blob no esté vacío
                        if (blob.size === 0) {{
                            throw new Error('El archivo recibido está vacío');
                        }}
                        
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = '{TABLAS_CSV[nombre_logico]}.csv';
                        a.style.display = 'none';
                        document.body.appendChild(a);
                        a.click();
                        
                        // Limpiar después de un tiempo
                        setTimeout(() => {{
                            document.body.removeChild(a);
                            window.URL.revokeObjectURL(url);
                        }}, 100);
                    }})
                    .catch(e => {{
                        console.error('Error en descarga:', e);
                        alert('Error al descargar CSV: ' + e.message);
                    }});
            """

        ui.run_javascript(js)

        # --- Generación de Interfaz de Usuario ---
        ui.notify(f"Descargando {TABLAS_CSV[nombre_logico]}...", type="positive")

    except Exception as e:
        ui.notify(f"Error al exportar {nombre_logico}: {e}", type="negative")
        print(f"Error al exportar {nombre_logico}: {e}")
# --- Generación de Interfaz de Usuario ---
def _set_active_table(row_element, all_rows):
    """
    Marca una tabla como activa resaltándola con color y desmarca las demás.
    """
    # Desmarcar todas las filas primero
    for row in all_rows:
        row.classes(remove="bg-blue-400 border-l-4 border-primary shadow-md")

    # Marcar la fila seleccionada con azul más intenso
    row_element.classes("bg-blue-400 border-l-4 border-primary shadow-md")


def _clear_active_table(row_element):
    """
    Desmarca una tabla eliminando el resaltado.
    """
    row_element.classes(remove="bg-blue-400 border-l-4 border-primary shadow-md")


def render_module_ui(
    titulo: str,
    subtitulo: str,
    tablas_map={},
    tablas_map_csv={},
    mostrar_func=None,
    exportar_individual_func=None,
    exportar_todas_func=None,
    descargar_csv_func = None,  # Indica que este boton es opcional,
):
    """
    Genera la interfaz de usuario repetitiva (títulos, botón de exportar todo, lista de tablas).
    """
    ui.label(titulo).classes("text-2xl font-bold mb-1")
    ui.label(subtitulo).classes("text-sm mb-4")
    ui.separator()

    # Botón para exportar todas las tablas (solo si hay más de 1)
    if len(tablas_map) > 1:
        ui.button(
            "Exportar todas las tablas a JSON",
            on_click=exportar_todas_func,
        ).props("color=blue size=md icon=cloud_download").classes("mt-4 mb-6")

    # Display table names and buttons
    all_table_rows = []
    with ui.column().classes("mt-6 gap-2 w-full"):
        for nombre_logico in tablas_map.keys():
            # Fila con efecto hover y padding para que se vea mejor
            table_row = ui.row().classes(
                "items-center justify-between w-full px-3 py-2 rounded cursor-pointer transition-all duration-200 hover:bg-blue-200"
            )
            with table_row:
                ui.label(nombre_logico).classes("text-md font-semibold")

                async def _mostrar_con_highlight(n, row_element, rows):
                    _set_active_table(row_element, rows)
                    try:
                        await mostrar_func(n)
                    finally:
                        _clear_active_table(row_element)

                async def _exportar_con_highlight(n, row_element, rows):
                    _set_active_table(row_element, rows)
                    try:
                        await exportar_individual_func(n)
                    finally:
                        _clear_active_table(row_element)

                with ui.row():
                    ui.button(
                        "Visualizar datos",

                        on_click=lambda n=nombre_logico, r=table_row, rows=all_table_rows: _mostrar_con_highlight(
                            n, r, rows
                        ),
                    ).props("color=primary outline size=sm")

                    ui.button(
                        "Exportar a JSON",

                        on_click=lambda n=nombre_logico, r=table_row, rows=all_table_rows: _exportar_con_highlight(
                            n, r, rows
                        ),
                    ).props("color=green outline size=sm icon=cloud_download")

                    # Lista de nombres lógicos que deben mostrar el botón
                    nombres_con_csv = [ "Facturas de"]

                    if nombre_logico in nombres_con_csv:
                        ui.button(
                            "Exportar a CSV",
                            on_click=lambda n=nombre_logico: descargar_csv_func(n),
                        ).props("color=orange outline size=sm icon=download").classes("ml-2")

    with ui.column().classes("mt-6 gap-2 w-full"):
        for nombre_logico in tablas_map_csv.keys():
            with ui.row().classes("items-center justify-between w-full"):
                ui.label(nombre_logico).classes("text-md font-semibold")

                with ui.row():
                    ui.button(
                        "Visualizar datos",
                        # Aquí usamos la función de mostrar del módulo específico
                        on_click=lambda n=nombre_logico: mostrar_func(n),
                    ).props("color=primary outline size=sm")

                    ui.button(
                            "Exportar a CSV",
                            on_click=lambda n=nombre_logico: descargar_csv_func(n),
                        ).props("color=orange outline size=sm icon=download").classes("ml-2")
            all_table_rows.append(table_row)
