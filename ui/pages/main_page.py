# ui/pages/main_page.py
from nicegui import app, ui

from config import DEFAULT_MODULE
from ui.components import header, sidebar
from ui.pages.modules import (
    cobros_pagos_view,
    contabilidad_general_view,
    general_view,
    inventarios_view,
    nomina_view,
    recursos_humanos_view,
    inicio_view,
    costo_view,
    almacen_view,
    productos_view,
    activos_fijos_view,
    ventas_view,
    compras_view,
    cuentas_view,
)

# Diccionario que mapea los nombres de módulos a sus funciones .show()
MODULES_VIEW = {
    "Inicio": inicio_view.show,
    "General": general_view.show,
    "Contabilidad General": contabilidad_general_view.show,
    "Nómina": nomina_view.show,
    "Recursos Humanos": recursos_humanos_view.show,
    "Cobros y Pagos": cobros_pagos_view.show,
    "Inventarios": inventarios_view.show,
    "Costo": costo_view.show,
    "Almacen": almacen_view.show,
    "Productos": productos_view.show,
    "Cuentas": cuentas_view.show,
    "Activos Fijos": activos_fijos_view.show,
    "Ventas": ventas_view.show,
    "Compras": compras_view.show,
}


# Definimos la función show_module_content como "refrescable"
# Esto significa que podemos llamarla con .refresh() para que NiceGUI la redibuje
# @ui.refreshable
# def show_module_content(module_name: str):
#     """
#     Renderiza el contenido del módulo seleccionado.
#     Usa un diccionario para simplificar el manejo de vistas.
#     """


#     module_func = MODULES_VIEW.get(module_name)
#     if module_func:
#         module_func()
#     else:
#         ui.label(f"Módulo '{module_name}' no encontrado.").classes(
#             "text-red-500 text-lg"
#         )


def render_module_content(container: ui.column, module_name: str):
    """
    Renderiza el contenido del módulo seleccionado en el contenedor.
    Limpia el contenedor antes de renderizar.
    """
    container.clear()
    with container:
        module_func = MODULES_VIEW.get(module_name)
        if module_func:
            module_func()
        else:
            ui.label(f"Módulo '{module_name}' no encontrado.").classes(
                "text-red-500 text-lg"
            )


def show():
    """
    Función principal que construye la interfaz de usuario de la página principal.
    Cada cliente tiene su propio contenedor de contenido aislado.
    """
    # Obtiene el módulo actual del almacenamiento de usuario'
    current_module = app.storage.user.get("current_view", DEFAULT_MODULE)

    # Crea el encabezado de la aplicación
    header.create_header(
        server_ip=app.storage.user.get("server_ip_display", ""),
        instance_name=app.storage.user.get("instance_name"),
        on_logout=handle_logout
    )

    # Contenedor para el contenido del módulo - se guarda como variable local
    # no en app.storage.user para evitar problemas de serialización
    content_container = None
    def refresh_sidebar(module_name: str):
        """Refresca el sidebar con el módulo seleccionado."""
        nonlocal sidebar_container
        if sidebar_container:
            sidebar_container.clear()
            with sidebar_container:
                sidebar.create_sidebar(
                    selected_module=module_name, on_module_select=handle_module_change
                )
    def handle_module_change(module_name: str):
        """Handler interno para cambio de módulo que tiene acceso al contenedor."""
        nonlocal content_container
        # Actualiza el módulo actual en el almacenamiento de usuario
        app.storage.user["current_view"] = module_name
        # Refrescar el sidebar para mostrar la nueva selección
        refresh_sidebar(module_name)
        # Renderizar el nuevo contenido
        if content_container:
            render_module_content(content_container, module_name)

    # Área principal de contenido (barra lateral + contenido del módulo)
    with ui.row().classes("w-full h-[calc(100vh-4rem)]"):
        # Contenedor para la barra lateral (para poder refrescarlo)
        with ui.column().classes("w-64 h-full") as sidebar_container:
            # Crea la barra lateral
            sidebar.create_sidebar(
                selected_module=current_module, on_module_select=handle_module_change
            )

        # # Contenedor para el contenido del módulo
        # with ui.column().classes("flex-grow p-6 bg-slate-100 overflow-auto"):
        #     # Llama la función refrescable para mostrar el contenido del módulo
        #     show_module_content(current_module)

        # Contenedor para el contenido del módulo (único por cliente)
        with ui.column().classes(
            "flex-grow p-6 bg-slate-100 overflow-auto"
        ) as content_container:
            # Renderizar el contenido inicial del módulo
            render_module_content(content_container, current_module)


def handle_logout():
    """
    Maneja el cierre de sesión del usuario.
    """
    # Actualiza el estado de inicio de sesión y limpia el IP del servidor
    app.storage.user.update(
        {
            "connected": False,
            "server_ip_display": "",
            "instance_name": None,
            "current_view": "General",
        }
    )
    # Redirige al usuario a la página de inicio de sesión
    ui.navigate.to("/")

