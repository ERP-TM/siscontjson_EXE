import logging
import traceback

from fastapi import APIRouter, HTTPException
from db.db_connection import create_db_managerAlchemy
from db.db_manager import ConexionParams

from db import db_cuentas as cuentas
from fastapi.responses import JSONResponse

from fastapi import Query

router = APIRouter()

@router.post("/cuentas",
    summary="Cuentas Bancarias",
    description="Muestra listado de los Grupos Contables",
    tags=["Cuentas"],
)
async def getAccounts(params: ConexionParams, export: bool = Query(False)):
    """
    Este endpoint retorna los valores de la tabla TIGRUPOCONTABLE
    """ 
    try:
        with create_db_managerAlchemy(params) as db:
            data =cuentas.getAccounts(db, params.database)
            return JSONResponse(content=data)
    except:
         raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de TIGRUPOCONTABLE",
        )
    
    
@router.post("/elementos_gastos",
    summary="Elementos de gastos",
    description="Muestra listado de Elementos de Gastos",
    tags=["Cuentas"],
)
async def getElemGastos(params: ConexionParams, export: bool = Query(False)):    
    """
    Este endpoint retorna los valores de la tabla SCGELEMENTODEGASTO
    """
    try:
        with create_db_managerAlchemy(params) as db:
            data=cuentas.getExpenseElement(db, params.database)
            return JSONResponse(content=data)
    except:
         raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCGELEMENTODEGASTO",
        )


@router.post("/asientos_contables",
    summary="Asientos Contables",
    description="Muestra listado de Asientos contables del mayor de contabilidad",
    tags=["Cuentas"],
    )
async def getAsientoscontables(params: ConexionParams, export: bool = Query(False)):
    """
    Este endpoint retorna los valores de la tabla SCGMAYORCONTABILIDAD
    """
    try:
        with create_db_managerAlchemy(params) as db:
            data = cuentas.getJournalEntry(db, params.database)
            return JSONResponse(content=data)
    except:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener datos de SCGMAYORCONTABILIDAD",
        )