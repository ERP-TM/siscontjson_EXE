from fastapi import APIRouter, HTTPException
from db.db_connection import create_db_managerAlchemy
from db.db_manager import ConexionParams
from collections import OrderedDict
from db import db_activos_fijos as activos_fijos
from fastapi.responses import JSONResponse, StreamingResponse
from io import StringIO, BytesIO
from pydantic import BaseModel

from fastapi import Query

import logging

class FunctionParams(BaseModel):
    siglas: str

router = APIRouter()

@router.post("/activos_fijos",
    summary="Submayor de los Medios Básicos",
    description="Muestra listado del Submayor de los Medios Básicos",
    tags=["Activos Fijos"],
)
async def get_af_apertura(params: ConexionParams, export: bool = Query(False)):    
    try:        
        with create_db_managerAlchemy(params) as db:           
            data= activos_fijos.getSAFApertura(db, params.database)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener SAFApertura: {e}",
        )
        

@router.post("/activos_fijos_csv", 
    summary="Submayor de los Medios Básicos",
    description="Muestra listado del Submayor de los Medios Básicos",
    tags=["Activos Fijos"],
    )
async def get_activos_fijos_csv(params: ConexionParams):
    try:
        
        with create_db_managerAlchemy(params) as db:
            # Obtener datos como lista de dicts
            df = activos_fijos.getSAFAperturaCSV(db, params.database, params.siglas)
                  
            # Usar BytesIO para mejor performance
            stream = BytesIO()
            df.to_csv(stream, index=False, encoding='utf-8-sig')
            stream.seek(0)  # Volver al inicio del stream

            return StreamingResponse(
                stream,
                media_type="text/csv",
                headers={
                   "Content-Disposition": "attachment; filename=datos.csv",                    
                }
            )            
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPPAGODOCUMENTO: {str(e)}",
        )


@router.post("/categorias",
    summary="Categorias de los Activos Fijos",
    description="Muestra de las Categorias de los Activos Fijos",
    tags=["Activos Fijos"],
)
async def get_af_categoria(params: ConexionParams):   
    print("Categorias") 
    try:
        with create_db_managerAlchemy(params) as db:            
            data= activos_fijos.getCategoryAF(db, params.database)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener SAFGruposAFT o SAFSubgruposAFT: {e}",
        )
        

@router.post("/libro_finanzas",
    summary="Libros de Finanzas",
    description="Muestra los libros de finanzas",
    tags=["Activos Fijos"],
)
async def get_af_libros_finanzas(params: ConexionParams, export: bool = Query(False)):    
    try:
        with create_db_managerAlchemy(params) as db:
            data= activos_fijos.getFinanceBook(db, params.database)            
            return JSONResponse(content=data)
    except Exception as e:
         raise HTTPException(
            status_code=500,
            detail=f"Error al obtener SAFGruposAFT o SAFSubgruposAFT: {e}",
        )
        
        
@router.post("/location",
    summary="Las posibles localizaciones de los activos fijos.",
    description="Muestra el relacionador del Area/Subarea con Nivel de Responsabilidad.",
    tags=["Activos Fijos"],
)
async def getLocation(params: ConexionParams, export: bool = Query(False)):    
    try:
        with create_db_managerAlchemy(params) as db:
            data=activos_fijos.getLocation(db, params.database)
            return JSONResponse(content=data)
    except:
         raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SAFNivelRespAreaSubarea",
        )
    
 
@router.post("/department",
    summary="Departamentos",
    description="Muestra los Departamentos",
    tags=["Activos Fijos"],
)
async def get_department(params: ConexionParams, export: bool = Query(False)):    
    try:
        with create_db_managerAlchemy(params) as db:
            data=activos_fijos.getDepartment(db, params.database)
            return JSONResponse(content=data)
    except Exception as e:
         logging.error(f"Error al obtener SAFGruposAFT o SAFSubgruposAFT: {e}")
         raise Exception(f"Error al obtener datos de SAFGruposAFT o SAFSubgruposAFT: {str(e)}")
 

