import json

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from db import db_almacen as almacen
from db.db_connection import create_db_managerAlchemy
from db.db_manager import ConexionParams


router = APIRouter()


@router.post(
    "/almacen",
    summary="Lista los almacenes",
    description="Muestra listado de los almacenes",
    tags=["ALMACEN"],
)

async def get_almacenes_endpoint(params: ConexionParams, export: bool = Query(False)):
    try:
        with create_db_managerAlchemy(params) as db:
            data = almacen.get_almacenes(db,export=False)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SIVNOMALM:"
                   f" {str(e)}",
        )
