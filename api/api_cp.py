import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from db import db_cp as cobropago
from db.db_connection import create_db_managerAlchemy
from db.db_manager import ConexionParams

import io
import csv
from nicegui import ui

router = APIRouter()

@router.post(
    "/factura_compra",
    summary="Lista las Facturas de Compra de Cobros y Pagos para el proceso de Apertura",
    description="Lista las Facturas de Compra que faltan por liquidar",
    tags=["CP"],
)

async def get_factura_compra_endpoint(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = cobropago.get_factura_compra(db)
            return JSONResponse(content=data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPPAGODOCUMENTO:"
                   f" {str(e)}",
        )

@router.post("/factura_compra_csv", 
    summary="Lista las Facturas de Compra de Cobros y Pagos para el proceso de Apertura a CSV",
    description="Lista las Facturas de Compra que faltan por liquidar en CSV",
    tags=["CP"],)

async def get_factura_compra_csv(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            # Obtener datos como lista de dicts
            data = cobropago.get_factura_compra(db)
            # Si data es JSON string, parsear así:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                raise HTTPException(status_code=404, detail="No hay datos para exportar")

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())

            # Filas fijas antes del header
            filas_fijas = [
                ['Editar en masa Invoices', '', ''],
                ['Invoice Number', 'Party Type', 'Party', 'Temporary Opening Account', 
                 'Posting Date', 'Due Date', 'Item Name', 'Outstanding Amount', 
                 'Quantity', 'Cost Center'],
                ['invoice_number', 'party_type', 'party', 'temporary_opening_account', 
                 'posting_date', 'due_date', 'item_name', 'outstanding_amount', 'qty', 
                 'cost_center'],
                ['Reference number of the invoice from the previous system', '', '', 'dd-mm-yyyy', 'dd-mm-yyyy'],
                ['El formato CSV es sensible a mayúsculas y minúsculas'],
                ['No edite los encabezados que están preestablecidos en la plantilla'],
                ['------']
            ]

            csv_writer = csv.writer(output)
            csv_writer.writerows(filas_fijas)

            writer.writeheader()
            writer.writerows(data)

            output.seek(0)

            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="factura_compra.csv"'
                },
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPPAGODOCUMENTO: {str(e)}",
        )
    
@router.post(
    "/factura_venta",
    summary="Lista las Facturas de Ventas de Cobros y Pagos para el proceso de Apertura",
    description="Lista las Facturas de Ventas que faltan por liquidar",
    tags=["CP"],
)

async def get_cobro_pago_Ventas_endpoint(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = cobropago.get_factura_ventas(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPCOBRODOCUMENTO:"
                   f" {str(e)}",
        )

@router.post(
    "/factura_ventas_csv",
    summary="Lista las Facturas de Ventas de Cobros y Pagos para el proceso de apertura a CSV",
    description="Muestra listado de las Facturas de Ventas que faltan por liquida en CSV",
    tags=["CP"],
)

async def get_cobro_pago_Ventas_csv(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = cobropago.get_factura_ventas(db)
            # Si data es JSON string, parsear así:
            if isinstance(data, str):
                data = json.loads(data)

            if not data:
                raise HTTPException(status_code=404, detail="No hay datos para exportar")

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())

            # Filas fijas antes del header
            filas_fijas = [
                ['Editar en masa Invoices', '', ''],
                ['Invoice Number', 'Party Type', 'Party', 'Temporary Opening Account', 
                 'Posting Date', 'Due Date', 'Item Name', 'Outstanding Amount', 
                 'Quantity', 'Cost Center'],
                ['invoice_number', 'party_type', 'party', 'temporary_opening_account', 
                 'posting_date', 'due_date', 'item_name', 'outstanding_amount', 'qty', 
                 'cost_center'],
                ['Reference number of the invoice from the previous system', '', '', 'dd-mm-yyyy', 'dd-mm-yyyy'],
                ['El formato CSV es sensible a mayúsculas y minúsculas'],
                ['No edite los encabezados que están preestablecidos en la plantilla'],
                ['------']
            ]

            csv_writer = csv.writer(output)
            csv_writer.writerows(filas_fijas)

            writer.writeheader()
            writer.writerows(data)

            output.seek(0)

            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="factura_ventas.csv"'
                },
            )

            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPCOBRODOCUMENTO:"
                   f" {str(e)}",
        )


@router.post(
    "/pagos_anticipados",
    summary="Lista los documentos de Pagos Anticipados",
    description="Muestra listado de documentos de Pagos Anticipados",
    tags=["CP"],
)

async def get_pagos_anticipados_endpoint(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = cobropago.get_pagos_anticipados(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPPAGO:"
                   f" {str(e)}",
        )

@router.post(
    "/cobros_anticipados",
    summary="Lista los documentos de Cobros Anticipados",
    description="Muestra listado de documentos de Cobros Anticipados",
    tags=["CP"],
)

async def get_cobros_anticipados_endpoint(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = cobropago.get_cobros_anticipados(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPCOBRO:"
                   f" {str(e)}",
        )

@router.post(
    "/doc_crediticios",
    summary="Lista los documentos de Créditos Documentarios",
    description="Muestra listado de documentos de Créditos Documentarios",
    tags=["CP"],
)

async def get_doc_crediticios_endpoint(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = cobropago.get_doc_crediticios(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPPAGO:"
                   f" {str(e)}",
        )

@router.post(
    "/tipo_docbancario",
    summary="Lista los Tipos de Documentos Bancarios",
    description="Muestra listado de los Tipos de Documentos Bancarios",
    tags=["CP"],
)

async def get_tipo_docbancario_endpoint(params: ConexionParams):
    try:
        with create_db_managerAlchemy(params) as db:
            data = cobropago.get_tipo_docbancario(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SCPTIPODOCUMENTOBANCARIO:"
                   f" {str(e)}",
        )