# views/connection_view.py
from datetime import datetime
from nicegui import app, ui

# from state.store import store
from config import get_settings
from db.db_connection_old import create_db_managerAlchemy, test_connection

# from db.db_manager import AppState, ConexionParams
from db.db_manager import ConexionParams


# def connection_form(request):
def connection_form():
    settings = get_settings()

    with ui.column().classes(
        "w-full h-screen flex items-center justify-center bg-gray-100 p-4"
    ):
        with ui.card().classes("w-full max-w-md p-8 shadow-2xl"):
            ui.label("Conectar a la Base de Datos").classes("text-h5 text-center")

            # ip_input = ui.input("IP del servidor/Instancia SQL").classes("w-full mb-4")
            ip_input = ui.input("IP o Nombre del Servidor").classes("w-full mb-4")
            instance_input = ui.input("Instancia SQL (opcional)").classes("w-full mb-4")
            database_input = ui.input("Base de datos").classes("w-full mb-4")
            password_input = ui.input(
                "Contraseña", password=True, password_toggle_button=True
            ).classes("w-full mb-4")
            error_label = ui.label("").classes("text-red-600 text-sm mb-4")

            async def connect():
                if (
                    not ip_input.value
                    or not password_input.value
                    or not database_input.value
                ):
                    error_label.text = "Todos los campos son requeridos"
                    return

                spinner = ui.spinner(size="lg", color="primary")
                spinner.classes(
                    "fixed top-0 left-0 right-0 bottom-0 m-auto z-50"
                )  # centrar el spinner en pantalla

                try:
                    instance_value = instance_input.value.strip() or None
                    
                    params = ConexionParams(
                        host=ip_input.value,
                        password=password_input.value,
                        database=database_input.value,
                        # Solo pasa instance_name si el usuario escribió algo
                        instance_name=instance_value,
                    )
                    # print('Entra a params')
                    # store.db_params = params  # guardando como instancia de ConexionParams
                    # Probar la conexión usando SQLAlchemy
                    if test_connection(params):
                        # Crear DatabaseManager para la sesión del usuario
                        db_manager = create_db_managerAlchemy(params)

                        app.storage.user["connected"] = True
                        app.storage.user["db_params"] = params.model_dump()
                        # app.storage.user["db_manager"] = db_manager
                        app.storage.user["ip_server"] = ip_input.value
                        app.storage.user["server_ip_display"] = ip_input.value
                        app.storage.user["instance_name"] = instance_value  
                        app.storage.user["last_activity"] = datetime.now().isoformat()

                        ui.notify("Conexión exitosa!", type="positive")
                        ui.navigate.to("/")
                    else:
                        error_label.text = "No se pudo conectar a la base de datos"

                except Exception as e:
                    error_label.text = f"Error de conexión: {str(e)}"
                    # store.reset()
                    # Limpiar estado de sesión del usuario en caso de error
                    app.storage.user["connected"] = False
                    app.storage.user["db_params"] = None
                    # app.storage.user["db_manager"] = None
                    ui.notify("Error al conectar", type="negative")
                finally:
                    spinner.delete()  # Esto oculta el spinner siempre

            ui.button("Conectar", on_click=connect).classes("mt-4 w-full")
