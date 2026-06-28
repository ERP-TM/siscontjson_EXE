from nicegui import app, ui

from config import MODULES


def create_sidebar(selected_module: str, on_module_select):
    """Crea la barra lateral con los módulos disponibles."""
    # Estado para tracking de módulos expandidos
    expanded_modules = {}

    with ui.column().classes("w-64 bg-slate-50 border-r border-slate-200 h-full"):
        ui.label("Módulos").classes(
            "text-lg font-bold p-4 text-slate-700 border-b border-slate-200"
        )

        for module_name, module_data in MODULES.items():
            # Determinar si es un módulo con sub-módulos o uno simple
            if isinstance(module_data, dict):
                icon_name = module_data["icon"]
                children = module_data.get("children", {})
                has_children = True
            else:
                icon_name = module_data
                children = {}
                has_children = False

            is_selected = module_name == selected_module
            is_child_selected = any(
                child == selected_module for child in children.keys()
            )

            if has_children:
                # Usar ui.expansion para módulos con hijos
                with ui.expansion(
                    module_name,
                    icon=icon_name,
                    value=is_child_selected,  # Expandido si un hijo está seleccionado
                ).classes("w-full text-slate-600") as expansion:
                    # Quitar padding por defecto del expansion
                    expansion.props("dense header-class='py-2.5 px-4'")

                    # Crear sub-módulos dentro del expansion
                    for child_name, child_icon in children.items():
                        is_child_item_selected = child_name == selected_module

                        child_classes = (
                            "w-full flex items-center gap-3 px-4 py-2 "
                            "rounded-md cursor-pointer transition-all "
                            "duration-150 ease-in-out"
                        )
                        if is_child_item_selected:
                            child_classes += " bg-primary/20 text-primary font-medium"
                        else:
                            child_classes += " text-slate-500 hover:bg-slate-200 hover:text-slate-700"

                        with (
                            ui.element("div")
                            .classes(child_classes)
                            .on(
                                "click",
                                lambda _, name=child_name: on_module_select(name),
                            )
                        ):
                            ui.icon(child_icon).classes("text-base")
                            ui.label(child_name).classes("text-sm")
            else:
                # Módulo simple sin hijos
                item_classes = (
                    "w-full flex items-center gap-3 px-4 py-2.5 "
                    "rounded-md cursor-pointer transition-all "
                    "duration-150 ease-in-out"
                )
                if is_selected:
                    item_classes += " bg-primary text-white font-semibold shadow-sm"
                else:
                    item_classes += (
                        " text-slate-600 hover:bg-slate-200 hover:text-slate-800"
                    )

                with (
                    ui.element("div")
                    .classes(item_classes)
                    .on("click", lambda _, name=module_name: on_module_select(name))
                ):
                    ui.icon(icon_name).classes("text-xl")
                    ui.label(module_name).classes("text-sm")
