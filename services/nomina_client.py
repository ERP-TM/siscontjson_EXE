# services/nomina_client.py
from typing import Any

# Importar la función base y la función de utilidad
from .base_client import obtener_datos_tabla_base, get_current_conexion_params


# Lista de endpoints disponibles (Datos únicos)
TABLAS_NOMINA = {
    "Trabajadores": "trabajadores",
    "Categorías Ocupacionales": "categorias-ocupacionales",
    "Cargos Trabajadores": "cargos-trabajadores",
    "Tipos Trabajadores": "tipos-trabajadores",
    "Retenciones": "tipos-retenciones",
    "Pensionados": "pensionados",
    "Tasas Destajos": "tasas_destajos",
    "Colectivos": "colectivos",
    "Departamentos": "departamentos",
    "Submayor Vacaciones": "submayor_vacaciones",
    "Submayor Salarios No Reclamados": "submayor_salarios_no_reclamados",
    "Pagos Trabajadores": "pagos_trabajadores",
    "Grupo Salarial": "grupo_salarial",
    "Puestos de Trabajos": "puestos_trabajos",
    "Configuracion Contribuciones e Impuestos": "configuracion_contribuciones_impuestos",
    "Asignacion Contribuciones e Impuestos": "asignacion_contribuciones_impuestos",
}

# Mapeando con el nombre de las tablas de sqlserver (Datos únicos)
DOCTYPE_NAME_MAP = {
    "Trabajadores": "Employee",
    "Categorías Ocupacionales": "Occupational Category",
    "Cargos Trabajadores": "Designation",
    "Tipos Trabajadores": "Employment Type",
    "Retenciones": "Withholding Type",
    "Pensionados": "SNOMANTPENS",
    "Tasas Destajos": "Piecework Rate",
    "Colectivos": "Employee Group",
    "Departamentos": "Department",
    "Submayor Vacaciones": "Employee Opening Vacation Subledger",
    "Submayor Salarios No Reclamados": "Opening of the Unclaimed Salary Subledger",
    "Pagos Trabajadores": "sc408 model",
    "Grupo Salarial": "Salary Group",
    "Puestos de Trabajos": "Job Position",
    "Configuracion Contribuciones e Impuestos": "Contributions and Taxes Setting",
    "Asignacion Contribuciones e Impuestos": "Allocation of Contributions and Taxes",
}


# Reemplazar la definición por la importación directa de la base
get_current_conexion_params = get_current_conexion_params


async def obtener_datos_tabla(
    nombre_tabla: str,
    modulo: str | None = None,
    export: bool = False,
    grouped: bool = False,
    mes: int | None = None,  # adicionado para el submayor vacaciones
    anno: int | None = None,  # adicionado para el submayor vacaciones
) -> Any:
    """
    Función de fachada para Nómina que llama a la función base.
    """

    return await obtener_datos_tabla_base(
        nombre_tabla=nombre_tabla,
        tablas_map=TABLAS_NOMINA,
        doctype_map=DOCTYPE_NAME_MAP,
        default_module="nomina",
        modulo=modulo,
        export=export,  # se adiciono como parametro opcional
        grouped=grouped,  # adicionado nuevo parametro opcional para anidados
        mes=mes,  # adicionado para el submayor vacaciones
        anno=anno,  # adicionado para el submayor vacaciones
    )
