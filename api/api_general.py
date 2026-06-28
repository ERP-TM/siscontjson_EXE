import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from db import db_general as general
from db.db_connection import create_db_managerAlchemy
from db.db_manager import ConexionParams

from fastapi import Query

router = APIRouter()


@router.post(
    "/unidad_medida",
    summary="Lista las unidades de medida",
    description="Muestra listado de las unidades de medida",
    tags=["GENERAL"],
)
async def get_unidad_medida_endpoint(
    params: ConexionParams, export: bool = Query(False)
):
    try:
        with create_db_managerAlchemy(params) as db:
            data = general.get_unidad_medida(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SMGNOMENCLADORUNIDADMEDIDA:"
            f" {str(e)}",
        )


@router.post(
    "/clientes",
    summary="Lista todos los clientes",
    description="Muestra Listado de los clientes",
    tags=["GENERAL"],
)
async def get_clientes_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = general.get_clientes(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de SMCLIENTEPROVEEDOR CLIENTES: "
            f"{str(e)}",
        )


@router.post(
    "/proveedores",
    summary="Lista todos los proveedores",
    description="Muestra Listado de los proveedoresr",
    tags=["GENERAL"],
)
async def get_proveedores_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = general.get_proveedores(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de SMCLIENTEPROVEEDOR PROVEEDOR: "
            f"{str(e)}",
        )


@router.post(
    "/contactos",
    summary="Lista todos los contactos",
    description="Muestra Listado de los contactos",
    tags=["GENERAL"],
)
async def get_contactos_endpoint(
    params: ConexionParams,
    export: bool = Query(False),
    grouped: bool = Query(False),
):
    try:
        with create_db_managerAlchemy(params) as db:
            # Si export es True forzar la logica de agrupado
            # si no, usamos el valor que tenga 'grouped'
            logica_agrupado = True if export else grouped
            data = general.get_contactos(db, export=False, grouped=logica_agrupado)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de SCOCLIENTECONTACTOS CONTACTOS: "
            f"{str(e)}",
        )


@router.post(
    "/bancos",
    summary="Lista todos los bancos",
    description="Muestra listado de los bancos",
    tags=["GENERAL"],
)
async def get_bancos_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = general.get_banks(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de SCOCIENTEDATOSBANCARIOS: "
            f"{str(e)}",
        )


@router.post(
    "/tipos_bancos",
    summary="Lista todos los tipos de bancos",
    description="Muestra listado de los tipos de bancos",
    tags=["GENERAL"],
)
async def get_tipos_bancos_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = general.get_bank_type(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos fijos de la tabla: "
            f"{str(e)}",
        )


@router.post(
    "/cuentas_bancarias",
    summary="Lista todas las cuentas bancarias",
    description="Muestra listado de las cuentas bancarias",
    tags=["GENERAL"],
)
async def get_cuentas_bancarias_endpoint(
    params: ConexionParams, export: bool = Query(False)
):
    try:
        with create_db_managerAlchemy(params) as db:
            data = general.get_bank_accounts(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de SCOCIENTEDATOSBANCARIOS: "
            f"{str(e)}",
        )


@router.post(
    "/clientes_con_contactos",
    summary="Lista clientes con cantidad de contactos",
    description="Muestra listado de clientes con la cantidad de contactos y detalles",
    tags=["GENERAL"],
)
async def get_clientes_con_contactos_endpoint(
    params: ConexionParams, export: bool = Query(False)
):
    try:
        with create_db_managerAlchemy(params) as db:
            data = general.get_clientes_con_contactos(db, export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de clientes con contactos: "
            f"{str(e)}",
        )


@router.post(
    "/direcciones",
    summary="Lista direcciones clientes proveedores",
    description="Muestra listado de las direcciones",
    tags=["GENERAL"],
)
async def get_direcciones_endpoint(
    params: ConexionParams, export: bool = Query(False), grouped: bool = Query(False)
):
    try:
        with create_db_managerAlchemy(params) as db:
            logica_agrupado = True if export else grouped
            data = general.get_direcciones(db, export=False, grouped=logica_agrupado)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los datos de las direcciones: " f"{str(e)}",
        )
