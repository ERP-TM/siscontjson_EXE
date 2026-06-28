import datetime
import logging
from typing import Dict, List

from utils.jsons_utils import export_table_to_json, \
    export_table_to_json_paginated


# Para obtener los centros de costo y poniendo alias con el nombre
# del campo en el doctype
def get_centro_costo(db):
    doctype_name = "Cost Center"
    sqlserver_name = "SCCCENTROCOSTO"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (Centro Costo)
        ("name", ("OC.OCostDescrip", 'string')),
        ("cost_center_number", ("OC.OCostCodigo", 'string')),
        ("cost_center_name", ("OC.OCostDescrip", 'string')),
        ("creation", ("OC.OCostFechaModif", 'string')),
        ("expense_account", ("OC.OCostCGastoId", 'string')),
        ("department", ("A.AreaDescrip", 'string')),
        ("sub_department", ("SA.SAreaDescrip", 'string')),
        ("is_group", ("0", 'string')),
        ("disabled", ("0", 'string')),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ] + ["""(SELECT TOP 1 DatEntNom FROM SMGDatosEntidad) AS parent_cost_center
    """]

    query = f"""    
        SELECT 
            OC.OCostCodigo AS cost_center_number,
            OC.OCostDescrip AS name,
            OC.OCostDescrip AS cost_center_name,
            OC.OCostFechaModif AS creation,
             (CAST(CC.ClCuCuenta AS VARCHAR(10)) 
            + CASE 
                 WHEN CC.ClCuSubcuenta <> 0 
                     THEN CAST(CC.ClCuSubcuenta AS VARCHAR(10)) 
                 ELSE '' 
               END
            + CASE 
                 WHEN CC.ClCuSubControl <> 0 OR CC.ClCuAnalisis <> 0 
                     THEN CAST(CC.ClCuSubControl AS VARCHAR(10)) 
                 ELSE '' 
               END
            ) AS expense_account,            
            A.AreaDescrip AS department,
            SA.SareaDescrip AS sub_department,
            0 AS is_group,
            (case
              when OC.OCostActivo IS NULL OR OC.OCostActivo = '' then 0
              else 1
              end) AS disabled
        FROM SCCOBJCOSTO AS OC
        INNER JOIN SCGCLASIFICADORDECUENTAS AS CC 
            ON OC.OCostCGastoId = CC.ClcuIDCuenta
        INNER JOIN SMGAREASUBAREA AS A 
            ON OC.AreaCodigo = A.AreaCodigo
        INNER JOIN SMGAREASUBAREA1 AS SA 
            ON OC.AreaCodigo = SA.AreaCodigo 
           AND OC.SareaCodigo = SA.SareaCodigo 
           AND A.AreaCodigo = SA.AreaCodigo
        """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )