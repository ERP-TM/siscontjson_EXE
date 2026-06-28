import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse


from db import db_costo as costo
from db.db_connection import create_db_managerAlchemy
from db.db_manager import ConexionParams

router = APIRouter()


@router.post(
    "/centro_costo",
    summary="Lista los Centros de Costo",
    description="Muestra listado de los Centros de Costo",
    tags=["COSTO"],
)

async def get_centro_costo_endpoint(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = costo.get_centro_costo(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCCCENTROCOSTO:"
                   f" {str(e)}",
        )
