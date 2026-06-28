import datetime
import logging
from typing import Dict, List

from utils.jsons_utils import export_table_to_json, export_table_to_json_paginated


# Para obtener los almacenes y poniendo alias con el nombre

def get_almacenes(db,export=False):
    doctype_name = "Warehouse"
    sqlserver_name = "SIVNOMALM"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (Almacén)
        #("warehouse_name", (f"LTRIM(RTRIM(NomAlmDescrip))+'_'+{account_concat_sql_expression}", 'string')),  # nombre del almacén
        ("warehouse_name", ("NA.NomAlmDescrip", 'string')),        # nombre del almacén
        ("is_group", (0, 'boolean')),  # identifica si es un almacén padre o no
        ("parent_warehouse", ("NA.NomAlmDescrip", 'string')),  # identifica el padre del almacén hijo
        ("account", ("CCta.ClCuCuenta", 'string')),  # identifca la cuenta que debe tener el código del almacén
        ("address_line_1", ("NA.NomAlmUbicac", 'string'))  # identifca la dirección que pueda tener el almacén
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
           SELECT 
            trim(NomAlmDescrip) AS warehouse_name, 
            '1' AS is_group, 
            '' AS parent_warehouse, 
            '' AS account, 
            '' AS address_line_1
            FROM SIVNOMALM
            WHERE NomAlActivo = ' ' 

        UNION ALL

        SELECT 
        (TRIM(NA.NomAlmDescrip) + '_' + 
        CAST(CCta.ClCuCuenta AS VARCHAR(10)) + 
        CAST(CCta.ClCuSubcuenta AS VARCHAR(10)) + 
        CASE 
            WHEN CCta.ClCuSubControl <> 0 OR CCta.ClCuAnalisis <> 0 
            THEN CAST(CCta.ClCuSubControl AS VARCHAR(10))
            ELSE ''
        END) AS warehouse_name,
        '0' AS is_group, 
        CAST(TRIM(NA.NomAlmDescrip) AS VARCHAR(100)) AS parent_warehouse,
        (CAST(CCta.ClCuCuenta AS VARCHAR(10)) + 
        CAST(CCta.ClCuSubcuenta AS VARCHAR(10)) + 
        CASE 
            WHEN CCta.ClCuSubControl <> 0 OR CCta.ClCuAnalisis <> 0 
            THEN CAST(CCta.ClCuSubControl AS VARCHAR(10))
            ELSE ''
        END) AS account,
        NA.NomAlmUbicac AS address_line_1
        FROM SIVNOMALM AS NA
        INNER JOIN SIVEXISTENCIAMOVIMIENTO AS EM ON NA.NomAlmCod = EM.NomAlmCod
        INNER JOIN SIVNOMPROD AS NM ON EM.ProduCodigo = NM.ProduCodigo
        INNER JOIN SIVCTASCONFIG AS CC ON NM.CtaCGInvId = CC.CtaCGInvId
        INNER JOIN SCGCLASIFICADORDECUENTAS AS CCta ON CC.ClcuIDCuenta = CCta.ClcuIDCuenta
        WHERE NA.NomAlActivo = ''
        GROUP BY 
        NA.NomAlmCod, NA.NomAlmDescrip, NA.NomAlmUbicac, NA.NomAlActivo, NM.CtaCGInvId, 
        CCta.ClCuCuenta, CCta.ClCuSubcuenta, CCta.ClCuSubControl, CCta.ClCuAnalisis
        ORDER BY warehouse_name;
        """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save = export,
    )