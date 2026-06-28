# ui/components/header.py
from nicegui import ui


def create_header(server_ip: str, instance_name: str = None, on_logout=None):
    with ui.header(elevated=True).classes(
        "bg-primary text-white justify-between items-center px-4 h-16 shadow-md"
    ):
        # Construir el texto del servidor con instancia si existe
        if server_ip and instance_name:
            server_text = f"🖥️ Servidor: {server_ip}\\{instance_name}"
        elif server_ip:
            server_text = f"🖥️ Servidor: {server_ip}"
        else:
            server_text = "🖥️ Servidor: N/A"
        
        ui.label(server_text).classes("font-semibold text-sm")
        
        ui.button("Logout", on_click=on_logout, icon="logout").props(
            "flat color=white text-sm"
        )