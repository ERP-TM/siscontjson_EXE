# views/connection_view.py
from datetime import datetime
from nicegui import app, ui, run
from config import get_settings
from db.db_connection import create_db_managerAlchemy, test_connection
from utils.discover_all_instances import discover_all_mssql_instances
from db.db_manager import ConexionParams

# ---------------------------------------------------------------------------
# Puertos que el firewall del SERVIDOR debe tener abiertos para que la
# aplicación pueda descubrir y conectarse a SQL Server.
# ---------------------------------------------------------------------------
_FIREWALL_PORTS = [
    ("UDP", 1434,  "SQL Server Browser — descubrimiento automático de instancias"),
    ("TCP", 1431,  "Variante cercana al puerto estándar"),
    ("TCP", 1432,  "Variante cercana al puerto estándar"),
    ("TCP", 1433,  "Instancia por defecto (MSSQLSERVER) — puerto principal"),
    ("TCP", 1434,  "SQL Server Browser vía TCP (raro pero posible)"),
    ("TCP", 1435,  "Variante cercana al puerto estándar"),
    ("TCP", 1436,  "Variante cercana al puerto estándar"),
    ("TCP", 1437,  "Variante cercana al puerto estándar"),
    ("TCP", 1438,  "Variante cercana al puerto estándar"),
    ("TCP", 1439,  "Variante cercana al puerto estándar"),
    ("TCP", 1440,  "Variante cercana al puerto estándar"),
    ("TCP", 2433,  "Puerto alternativo habitual (redirección del 1433)"),
    ("TCP", 4022,  "SQL Server Service Broker"),
    ("TCP", 5022,  "Always On Availability Groups"),
    ("TCP", 14330, "Variante extendida del puerto estándar"),
]


def _show_firewall_ports_dialog():
    """
    Muestra un diálogo informativo con los puertos que deben estar abiertos
    en el firewall del servidor SQL Server.
    Se invoca automáticamente al cargar la vista de conexión.
    """
    with ui.dialog() as dlg, ui.card().classes("p-6 max-w-lg w-full"):
        with ui.row().classes("items-center mb-4 gap-2"):
            ui.icon("firewall", size="lg", color="orange")
            ui.label("Requisitos de red — Firewall del servidor").classes(
                "text-lg font-bold text-gray-800"
            )

        ui.label(
            "Para que la detección automática de instancias y la conexión "
            "funcionen correctamente, el administrador de red debe abrir los "
            "siguientes puertos en el firewall del servidor SQL Server:"
        ).classes("text-sm text-gray-600 mb-4")

        # Tabla de puertos
        columns = [
            {"name": "proto", "label": "Protocolo", "field": "proto", "align": "center"},
            {"name": "port",  "label": "Puerto",    "field": "port",  "align": "center"},
            {"name": "desc",  "label": "Uso",        "field": "desc",  "align": "left"},
        ]
        rows = [
            {"proto": proto, "port": port, "desc": desc}
            for proto, port, desc in _FIREWALL_PORTS
        ]
        ui.table(columns=columns, rows=rows, row_key="port").classes(
            "w-full mb-4 text-sm"
        )

        ui.markdown(
            "⚠️ **Importante:** si la instancia usa un **puerto dinámico** "
            "(asignado automáticamente), el administrador debe fijar un "
            "**puerto estático** en *SQL Server Configuration Manager* y abrir "
            "ese puerto en el firewall. El rango dinámico 49152-65535 "
            "**no se escanea** porque en redes corporativas el firewall lo "
            "bloquea en su totalidad."
        ).classes("text-xs text-gray-500 mb-4")

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button(
                "Copiar lista de puertos",
                icon="content_copy",
                on_click=lambda: (
                    ui.clipboard.write(
                        "\n".join(
                            f"{proto} {port} — {desc}"
                            for proto, port, desc in _FIREWALL_PORTS
                        )
                    ),
                    ui.notify("Lista copiada al portapapeles", type="positive"),
                ),
            ).props("flat")
            ui.button("Entendido", on_click=dlg.close).props("unelevated color=primary")

    dlg.open()


def connection_form():
    settings = get_settings()

    # Mostrar la ventana de puertos requeridos al cargar la vista
    ui.timer(0.3, _show_firewall_ports_dialog, once=True)

    with ui.column().classes(
        "w-full h-screen flex items-center justify-center bg-gray-100 p-4"
    ):
        with ui.card().classes("w-full max-w-md p-8 shadow-2xl"):
            ui.label("Conectar a la Base de Datos").classes("text-h5 text-center")

            # --- DIALOG DE INSTANCIAS ---
            with ui.dialog() as dialog, ui.card().classes("w-full max-w-lg p-6"):
                ui.label("Instancias SQL Server Detectadas").classes(
                    "text-h6 font-bold mb-2"
                )
                ui.label(
                    "Selecciona una fila para autocompletar el formulario."
                ).classes("text-grey text-sm mb-4")

                columns = [
                    {
                        "name": "instance_name",
                        "label": "Instancia",
                        "field": "instance_name",
                        "align": "left",
                        "required": True,
                    },
                    {
                        "name": "port",
                        "label": "Puerto TCP",
                        "field": "port",
                        "align": "center",
                    },
                    {
                        "name": "version",
                        "label": "Versión SQL",
                        "field": "version",
                        "align": "left",
                    },
                ]

                tabla_instancias = ui.table(
                    columns=columns,
                    rows=[],
                    row_key="instance_name",
                    selection="single",
                ).classes("w-full mb-4")

                with ui.row().classes("w-full justify-end"):
                    ui.button("Cerrar", on_click=dialog.close).props("flat")
            # --- FIN DIALOG ---

            # Inputs del formulario
            with ui.row().classes("w-full items-center mb-4 no-wrap"):
                ip_input = ui.input("IP o Nombre del Servidor").classes("col")
                search_btn = (
                    ui.button(icon="search")
                    .props("flat round")
                    .tooltip(
                        "Buscar instancias en este servidor.\n"
                        "Usa UDP 1434 (Browser) y escaneo de puertos TCP conocidos.\n"
                        "Si no aparece ninguna instancia, verifica los puertos del\n"
                        "firewall con el botón ℹ️ de arriba."
                    )
                )

            # Instancia: SOLO LECTURA — se rellena exclusivamente con la lupa.
            # Si el usuario pudiera escribirla manualmente no sabríamos el puerto
            # y la conexión fallaría silenciosamente.
            with ui.row().classes("w-full items-center mb-4 no-wrap gap-1"):
                instance_input = (
                    ui.input("Instancia SQL")
                    .classes("col")
                    .props("readonly")
                    .tooltip(
                        "Usa la lupa 🔍 para detectar instancias automáticamente.\n"
                        "Este campo se rellena solo al seleccionar una instancia;\n"
                        "no se puede escribir a mano para garantizar que el puerto\n"
                        "quede registrado correctamente."
                    )
                )
                # Icono informativo junto al input
                ui.icon("info_outline", color="grey", size="sm").tooltip(
                    "Solo lectura: se rellena con la lupa de búsqueda."
                )

            database_input = ui.input("Base de datos").classes("w-full mb-4")
            password_input = ui.input(
                "Contraseña", password=True, password_toggle_button=True
            ).classes("w-full mb-4")

            # Botón para volver a mostrar la info de puertos del firewall
            with ui.row().classes("w-full justify-end mb-2"):
                ui.button(
                    "Ver puertos requeridos",
                    icon="help_outline",
                    on_click=_show_firewall_ports_dialog,
                ).props("flat dense size=sm").classes("text-grey-7")

            error_label = ui.label("").classes("text-red-600 text-sm mb-4")

            # Etiqueta de progreso visible durante la búsqueda
            progress_label = ui.label("").classes("text-blue-600 text-sm mb-2")
            progress_label.set_visibility(False)

            # Puerto capturado al seleccionar instancia en el modal
            _selected_port: dict = {"value": None}

            # --- EVENTO SELECCIÓN EN TABLA ---
            def al_seleccionar_instancia(e):
                seleccionadas = e.args.get("rows", [])
                if not seleccionadas:
                    return
                fila = seleccionadas[0]
                nombre = fila["instance_name"]

                instance_input.value = nombre
                _selected_port["value"] = fila["port"]
                ui.notify(
                    f"Instancia: {nombre} — Puerto: {fila['port']}",
                    type="positive",
                )
                dialog.close()

            tabla_instancias.on("selection", al_seleccionar_instancia)

            # --- BÚSQUEDA DE INSTANCIAS ---
            async def buscar_instancias_click():
                host_ip = ip_input.value.strip()
                if not host_ip:
                    ui.notify("Escribe primero la IP o nombre del servidor.", type="warning")
                    return

                # Limpiar estado previo
                _selected_port["value"] = None
                instance_input.value = ""
                tabla_instancias.rows.clear()
                error_label.text = ""

                spinner = ui.spinner(size="md", color="primary")
                progress_label.set_visibility(True)
                progress_label.text = "🔍 Nivel 1 — Consultando SQL Server Browser (UDP 1434)…"
                search_btn.props("disable")

                try:
                    resultados = await run.io_bound(
                        discover_all_mssql_instances,
                        host_ip,
                        6.0,   # timeout por intento
                        None,  # búsqueda anónima (sin credenciales)
                        None,
                    )

                    progress_label.set_visibility(False)

                    if resultados:
                        tabla_instancias.add_rows(*resultados)
                        dialog.open()
                    else:
                        ui.notify("No se encontraron instancias abiertas.", type="warning")

                except RuntimeError:
                    progress_label.set_visibility(False)
                    with ui.dialog() as error_dialog, ui.card().classes("p-6 max-w-md"):
                        with ui.row().classes("items-center mb-3 gap-2"):
                            ui.icon("warning", color="red", size="md")
                            ui.label("No se encontraron instancias SQL Server").classes(
                                "text-base font-bold text-red-700"
                            )
                        ui.markdown(
                            """
Se intentaron los tres métodos de detección sin éxito:

1. **UDP 1434** (SQL Server Browser) — sin respuesta
2. **TCP 1433** (puerto estándar) — sin respuesta
3. **Escaneo de puertos conocidos** (1433, 2433, 4022, 5022…) — sin respuesta

**El rango dinámico 49152-65535 no se escanea** — si la instancia usa
un puerto en ese rango, el administrador debe fijar un puerto estático.

**Acciones recomendadas para el administrador:**
- Verificar que el servicio **SQL Server** esté iniciado.
- Habilitar el protocolo **TCP/IP** en *SQL Server Configuration Manager*.
- Iniciar el servicio **SQL Server Browser**.
- Abrir en el firewall los puertos requeridos (botón *"Ver puertos requeridos"*).
- Si usa puerto dinámico: asignar un **puerto estático** y abrirlo en el firewall.
                            """
                        ).classes("text-sm text-gray-700 mb-4")
                        with ui.row().classes("w-full justify-end gap-2"):
                            ui.button(
                                "Ver puertos requeridos",
                                icon="help_outline",
                                on_click=lambda: (error_dialog.close(), _show_firewall_ports_dialog()),
                            ).props("flat")
                            ui.button("Cerrar", on_click=error_dialog.close).props(
                                "unelevated color=primary"
                            )
                    error_dialog.open()

                except Exception as ex:
                    progress_label.set_visibility(False)
                    ui.notify(f"Error inesperado: {str(ex)}", type="negative")

                finally:
                    spinner.delete()
                    search_btn.props(remove="disable")

            search_btn.on("click", buscar_instancias_click)

            # --- CONEXIÓN ---
            async def connect():
                if (
                    not ip_input.value
                    or not password_input.value
                    or not database_input.value
                ):
                    error_label.text = "Todos los campos son requeridos"
                    return

                # Validar que se haya seleccionado una instancia con la lupa
                if not instance_input.value or _selected_port["value"] is None:
                    error_label.text = (
                        "Usa la lupa 🔍 para seleccionar una instancia antes de conectar."
                    )
                    return

                spinner = ui.spinner(size="lg", color="primary")
                spinner.classes("fixed top-0 left-0 right-0 bottom-0 m-auto z-50")

                try:
                    params = ConexionParams(
                        host=ip_input.value,
                        password=password_input.value,
                        database=database_input.value,
                        instance_name=instance_input.value,
                        port=_selected_port["value"],
                    )

                    if test_connection(params):
                        create_db_managerAlchemy(params)
                        app.storage.user["connected"] = True
                        app.storage.user["db_params"] = params.model_dump()
                        app.storage.user["ip_server"] = ip_input.value
                        app.storage.user["server_ip_display"] = ip_input.value
                        app.storage.user["instance_name"] = instance_input.value
                        app.storage.user["last_activity"] = datetime.now().isoformat()
                        ui.notify("Conexión exitosa!", type="positive")
                        ui.navigate.to("/")
                    else:
                        error_label.text = "No se pudo conectar a la base de datos"

                except Exception as e:
                    error_label.text = f"Error de conexión: {str(e)}"
                    app.storage.user["connected"] = False
                    app.storage.user["db_params"] = None
                    ui.notify("Error al conectar", type="negative")

                finally:
                    spinner.delete()

            ui.button("Conectar", on_click=connect).classes("mt-4 w-full")