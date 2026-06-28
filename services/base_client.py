# services/base_client.py
from typing import Any, Dict

import httpx
from nicegui import app
from db.db_manager import ConexionParams
from config import get_module_api_url
# from state.store import store


def get_current_conexion_params() -> ConexionParams:
    """
    Accede a la configuración de conexión del usuario actual desde app.storage.user.
    """
    db_params = app.storage.user.get("db_params")
    print("db_params en get_current_conexion_params:", db_params)
    # if not store.db_params:
    #     raise ValueError("No hay conexión activa configurada")
    if not db_params:
        raise ValueError("No hay conexión activa configurada")

    # return ConexionParams(
    #     host=store.db_params.host,
    #     password=store.db_params.password,
    #     database=store.db_params.database,
    # )
    # return ConexionParams(
    #     host=db_params.get("host"),
    #     password=db_params.get("password"),
    #     database=db_params.get("database"),
    # )
    # ✅ SOLUCIÓN: Usar ** para pasar TODOS los campos del diccionario
    # Esto incluye automáticamente instance_name si existe
    return ConexionParams(**db_params)


async def obtener_datos_tabla_base(
    nombre_tabla: str,
    tablas_map: Dict[
        str, str
    ],  # Recibe el mapa específico del módulo (TABLAS_NOMINA o TABLAS_GENERAL)
    doctype_map: Dict[str, str],  # Recibe el mapa de doctype específico
    default_module: str,  # Recibe el nombre del módulo por defecto (ej: "nomina")
    modulo: str | None = None,
    export: bool = False,
    grouped: bool = False,  # <-- Agregado para los datos agrupados
    mes: int | None = None, # adicionado para el submayor vacaciones
    anno: int | None = None,
) -> Any:
    """
    Helper que consulta una tabla de la API.
    La lógica de consulta HTTP y manejo de conexión es común para todos los módulos.
    """
    # Determinar el módulo actual desde app.storage.user
    # modulo = modulo or store.selected_module or default_module
    selected_module = app.storage.user.get("selected_module")
    modulo = modulo or selected_module or default_module

    # Obtener el endpoint y la URL base usando los mapas y el módulo
    endpoint = tablas_map[nombre_tabla]
    base_url = get_module_api_url(modulo)
    url = f"{base_url}/{endpoint}"

    # Preparar y enviar la solicitud HTTP (Lógica común)
    conexion_params = get_current_conexion_params()
    payload = conexion_params.model_dump()
    
    # Construir params — mes y anno solo se incluyen si tienen valor
    params: Dict[str, Any] = {"export": export, "grouped": grouped}
    if mes is not None:
        params["mes"] = mes
    if anno is not None:
        params["anno"] = anno

    async with httpx.AsyncClient() as client:
        
        response = await client.post(
            url,
            json=payload,
            params=params
        )
        response.raise_for_status()
        data = response.json()

    # Obtener el nombre correcto para el doctype usando el mapa específico
    doctype_name = doctype_map.get(nombre_tabla, nombre_tabla)

    # Devolver los datos junto con el doctype_name
    return {"data": data, "doctype": doctype_name}
