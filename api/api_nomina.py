import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from db import db_nomina as nomina
from db.db_connection import create_db_managerAlchemy
from db.db_manager import ConexionParams

from fastapi import Query

router = APIRouter()


@router.post(
    "/trabajadores",
    summary="Lista todos los trabajadores",
    description="Muestra listado de los trabajadores segun campos seleccionados",
    tags=["Nómina"],
)
async def get_trabajadores_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_trabajadores(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPTrabajadores: {str(e)}",
        )


@router.post(
    "/categorias-ocupacionales",
    summary="Lista de categorías ocupacionales",
    description="Muestra las categorías ocupacionales activas",
    tags=["Nómina"],
)
async def get_categorias_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_categorias_ocupacionales(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de categorías: {str(e)}",
        )


@router.post(
    "/cargos-trabajadores",
    summary="Lista los cargos de los trabajadores",
    description="Muestra los cargos de los trabajadores",
    tags=["Nómina"],
)
async def get_cargos_trabajadores_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_cargos_trabajadores(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los cargos de los trabajadores: {str(e)}",
        )


@router.post(
    "/tipos-trabajadores",
    summary="Lista los tipos de trabajadores",
    description="Muestra los tipos de los trabajadores",
    tags=["Nómina"],
)
async def get_tipos_trabajadores_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_tipos_trabajadores(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los tipos de trabajadores: {str(e)}",
        )


@router.post(
    "/tipos-retenciones",
    summary="Lista los tipos de retenciones",
    description="Muestra los tipos de los retenciones",
    tags=["Nómina"],
)
async def get_tipos_retenciones_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_tipos_retenciones(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los tipos de retenciones {str(e)}",
        )


@router.post(
    "/pensionados",
    summary="Lista los pensionados",
    description="Muestra los pensionados",
    tags=["Nómina"],
)
async def get_pensionados_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_pensionados(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los pensionados {str(e)}",
        )


@router.post(
    "/tasas_destajos",
    summary="Lista las tasas de destajos",
    description="Muestra las tasas de destajos",
    tags=["Nómina"],
)
async def get_tasas_destajos_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_tasas_destajos(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de las tasas de destajos {str(e)}",
        )


@router.post(
    "/colectivos",
    summary="Lista los colectivos",
    description="Muestra los colectivos",
    tags=["Nómina"],
)
async def get_colectivos_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_colectivos(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los colectivos {str(e)}",
        )


@router.post(
    "/departamentos",
    summary="Lista los departamentos",
    description="Muestra los departamentos",
    tags=["Nómina"],
)
async def get_departamentos_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_departamentos(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los departamentos {str(e)}",
        )


@router.post(
    "/submayor_vacaciones",
    summary="Lista Submayor de Vacaciones",
    description="Muestra Submayor de Vacaciones",
    tags=["Nómina"],
)
async def get_submayor_vacaciones_endpoint(params: ConexionParams, export: bool = Query(False), mes: int = Query(None), anno: int = Query(None)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_submayor_vacaciones(db, export=False, mes=mes, anno=anno)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos del submayor de vacaciones"
            f" {str(e)}",
        )


@router.post(
    "/submayor_salarios_no_reclamados",
    summary="Lista Submayor de salarios no reclamados",
    description="Muestra Submayor de Salarios No Reclamados",
    tags=["Nómina"],
)
async def get_submayor_salarios_no_reclamados_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_submayor_salarios_no_reclamados(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos del submayor de salarios no "
            f"reclamados"
            f" {str(e)}",
        )


@router.post(
    "/pagos_trabajadores",
    summary="Lista de los pagos de los trabajadores SC408",
    description="Muestra Pagos de los trabajadores SC408",
    tags=["Nómina"],
)
async def get_corte_sc408_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_corte_sc408(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos del pago de los trabajadores"
            f" {str(e)}",
        )


@router.post(
    "/grupo_salarial",
    summary="Lista de los grupos salariales y escala salarial",
    description="Muestra los grupos y escala salarial de los trabajadores",
    tags=["Nómina"],
)
async def get_grupo_salarial_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_grupo_salarial(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los grupos salariales de los trabajadores"
            f" {str(e)}",
        )


@router.post(
    "/puestos_trabajos",
    summary="Lista de los puestos de trabajos",
    description="Muestra los puestos de trabajos, grupo salarial por departamento",
    tags=["Nómina"],
)
async def get_puestos_trabajos_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = nomina.get_puestos_trabajos(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de los puestos de trabajo" f" {str(e)}",
        )


@router.post(
    "/configuracion_contribuciones_impuestos",
    summary="Lista la configuracion de contribuciones e impuestos",
    description="Muestra listado de la configuracion de contribuciones e impuestos",
    tags=["Nómina"],
)
async def get_configuracion_contribuciones_impuestos_endpoint(
    params: ConexionParams,
    export: bool = Query(False),
    grouped: bool = Query(False),
):
    try:
        with create_db_managerAlchemy(params) as db:
            # Si export es True forzar la logica de agrupado
            # si no, usamod el valor que tenga 'grouped'
            logica_agrupado = True if export else grouped
            data = nomina.get_configuracion_contribuciones_impuestos(
                db, export=False, grouped=logica_agrupado)
            return JSONResponse(content=data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de la configuracion de las contribuciones e impuestos"
            f" {str(e)}",
        )


@router.post(
    "/asignacion_contribuciones_impuestos",
    summary="Lista la asignacion de contribuciones e impuestos",
    description="Muestra listado de las asignaciones de contribuciones e impuestos",
    tags=["Nómina"],
)
async def get_asignacion_contribuciones_impuestos_endpoint(
    params: ConexionParams,
    export: bool = Query(False),
    grouped: bool = Query(False),
):
    try:
        with create_db_managerAlchemy(params) as db:
            # Si export es True forzar la logica de agrupado
            # si no, usamod el valor que tenga 'grouped'
            logica_agrupado = True if export else grouped
            data = nomina.get_asignacion_contribuciones_impuestos(
                db, export=False, grouped=logica_agrupado)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de la asignacion de contribuciones e impuestos"
            f" {str(e)}",
        )
