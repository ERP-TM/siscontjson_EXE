import datetime
import logging
from typing import Dict, List, Tuple, Any, Optional, Callable


from utils.jsons_utils import (
    export_table_to_json,
    export_table_to_json_paginated,
    fetch_table_data,
    save_json_file,
)

from utils.data_cleaners import (
    clean_name_field,
    clean_email_field,
    clean_text_field,
    clean_numeric_field,
    clean_json_to_list,
    clean_address_custom,
    apply_field_cleaners,
    clean_website_field,
    clean_phone_field,
    clean_quotes_field,
    clean_iban_field,
)

from utils.constants import CUSTOMER_CATEGORIES, SUPPLIER_CATEGORIES, sql_in_clause


# Para obtener las unidades de medida y poniendo alias con el nombre
# del campo en el doctype
def get_unidad_medida(db, export=False):
    doctype_name = "UOM"
    sqlserver_name = "SMGNOMENCLADORUNIDADMEDIDA"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("uom_name", ("UMedDescrip", "string"))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
       SELECT
           {", ".join(select_clauses)}
        FROM SMGNOMENCLADORUNIDADMEDIDA
        WHERE UMedactiva = 1
    """
    print(query)

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
    )


# Obtener los clientes y ponerle el alias con el nombre del campo en el doctype
# def get_clientes(db, export=False):
#     doctype_name = "Customer"
#     sqlserver_name = "SMGCLIENTEPROVEEDOR"
#     module_name = "Selling"

#     # Mapeo de campos: alias -> (campo SQL, tipo)
#     field_mapping = [
#         ("reup_code", (None, "string")),
#         ("customer_name", ("CP.CliDescripcion", "string")),
#         ("territory", ("P.PaisDescripcion", "string")),
#         ("default_currency", (None, "string")),
#         ("customer_type", (None, "string")),
#         ("customer_group", ("TE.TipifiDescripcion", "string")),
#         ("nit_code", (None, "string")),
#         ("identity_number", (None, "string")),
#         ("bank_accounts", (None, "string")),
#         ("represents_company", (None, "string")),
#         ("companies", (None, "string")),
#         ("default_price_list", (None, "string")),
#         ("language", ("CP.CliHabla", "string")),
#         ("website", ("CP.CliSucurWEB", "string")),
#         ("customer_primary_contact", (None, "string")),
#         ("mobile_no", ("CP.CliTelefono", "string")),
#         ("email_id", ("CP.CliEmail", "string")),
#     ]

#     # Construcción de SELECT
#     select_clauses = []
#     for alias, (sql_field, _) in field_mapping:
#         if alias == "reup_code":
#             clause = f"""
#                 CASE
#                     WHEN COALESCE(TRIM(UPPER(CP.CliTcpMiPyme)), '') <> 'T'
#                         THEN CAST(CP.CliCodigo AS NVARCHAR(100))
#                     ELSE NULL
#                 END AS {alias}
#             """

#         elif alias == "customer_type":
#             clause = f"""
#                 CASE
#                     WHEN CP.CliTcpMiPyme = 'T' THEN 'Individual'
#                     ELSE 'Company'
#                 END AS {alias}
#             """

#         elif alias == "default_currency":
#             clause = f"""
#                 CASE
#                     WHEN P.PaisDescripcion = 'Cuba' THEN 'CUP'
#                     ELSE 'USD'
#                 END AS {alias}
#             """

#         elif alias == "nit_code":
#             clause = f"""
#                 CASE
#                     WHEN CP.CliTcpMiPyme = 'T' AND COALESCE(TRIM(CP.CliNit), '') = ''
#                         THEN CAST(CP.CliCodigo AS NVARCHAR(100))
#                     WHEN CP.CliTcpMiPyme = 'T'
#                         THEN CAST(CP.CliNit AS NVARCHAR(100))
#                     ELSE CAST(CP.CliNit AS NVARCHAR(100))
#                 END AS {alias}
#             """

#         elif alias == "identity_number":
#             clause = f"""
#                 CASE
#                     WHEN CP.CliTcpMiPyme = 'T' AND COALESCE(TRIM(CP.CliNit), '') = ''
#                         THEN CAST(CP.CliCodigo AS NVARCHAR(100))
#                     WHEN CP.CliTcpMiPyme = 'T'
#                         THEN CAST(CP.CliNit AS NVARCHAR(100))
#                     ELSE NULL
#                 END AS {alias}
#             """

#         elif alias == "bank_accounts":
#             clause = f"""
#                 (
#                     SELECT
#                         TRIM(DB2.CliDBTitular) AS titular,
#                         TRIM(DB2.CliDBCuenta) AS account_number,
#                         TRIM(DB2.CliDBSwiFT) AS swift_code
#                     FROM SCOCLIENTEDBANCARIOS AS DB2
#                     WHERE DB2.CliCodigo = CP.CliCodigo -- Comparación directa
#                     FOR JSON PATH
#                 ) AS {alias}
#             """

#         elif alias == "represents_company":
#             clause = f"""
#                 CAST((
#                     SELECT
#                         representative_name,
#                         designation
#                     FROM (
#                         SELECT CP.CliCMRepresentante AS representative_name, CP.CliCMCargo AS designation
#                         WHERE NULLIF(TRIM(CP.CliCMRepresentante), '') IS NOT NULL
#                         UNION ALL
#                         SELECT CP.CliSucurRepresentante1, CP.CliSucurCargo1
#                         WHERE NULLIF(TRIM(CP.CliSucurRepresentante1), '') IS NOT NULL
#                         UNION ALL
#                         SELECT CP.CliSucurRepresentante2, CP.CliSucurCargo2
#                         WHERE NULLIF(TRIM(CP.CliSucurRepresentante2), '') IS NOT NULL
#                         UNION ALL
#                         SELECT CP.CliSucurRepresentante3, CP.CliSucurCargo3
#                         WHERE NULLIF(TRIM(CP.CliSucurRepresentante3), '') IS NOT NULL
#                     ) AS Reps
#                     FOR JSON PATH
#                 ) AS NVARCHAR(MAX)) AS {alias}
#             """

#         elif alias == "default_price_list":
#             clause = f"'Empresa Estatal' AS {alias}"

#         elif alias == "companies":
#             # Usamos el alias TE que ya está definido en el JOIN de la query principal
#             clause = f"""
#                 CASE
#                     WHEN TE.TipifiEstado = 1 THEN TE.TipifiDescripcion
#                     ELSE NULL
#                 END AS {alias}
#             """

#         elif alias == "customer_primary_contact":
#             # Solo llamamos al valor que ya calculó el CROSS APPLY abajo
#             clause = f"CA_Contacto.Contacto AS {alias}"

#         else:
#             clause = f"{sql_field} AS {alias}"

#         select_clauses.append(clause)

#     # 🔧 Query Optimizado
#     query = f"""
#     SELECT
#         {', '.join(select_clauses)}
#     FROM SMGCLIENTEPROVEEDOR AS CP
#     LEFT JOIN SCOPAIS AS P
#         ON CP.CliPaisCodIntern = P.PaisCodIntern
#     LEFT JOIN SCOTIPIFEMPRESA AS TE
#         ON CP.TipifiCodigo = TE.TipifiCodigo

#     -- Esto calcula el contacto UNA VEZ de forma eficiente por cada fila
#     OUTER APPLY (
#         SELECT TOP 1
#             TRIM(CONCAT(TRIM(C.CliContacNombre), ' ', TRIM(C.CliContacApellidos))) as Contacto
#         FROM SCOCLIENTECONTACTOS AS C
#         WHERE C.CliCodigo = CP.CliCodigo
#           AND C.CliContacEstado = 1
#     ) AS CA_Contacto

#     WHERE
#         TRIM(UPPER(CP.CliCategoria)) IN ('C', 'CP', 'L', 'LP', 'LR', 'A')
#         AND CP.CliActivo = 1
#     """

#     print(query)

#     # Definir qué limpiador usar para cada campo
#     cleaners = {
#         "customer_name": clean_name_field,
#         "bank_accounts": clean_json_to_list,
#         "represents_company": clean_json_to_list,
#         "companies": clean_name_field,
#         "mobile_no": clean_name_field,
#         "website": clean_name_field,
#         "email_id": clean_email_field,
#     }

#     return export_table_to_json(
#         db=db,
#         doctype_name=doctype_name,
#         sqlserver_name=sqlserver_name + "-cliente",
#         module_name=module_name,
#         field_mapping=field_mapping,
#         table_query=query,
#         save=export,
#         field_cleaners=cleaners,
#     )


def get_clientes(db, export=False):
    doctype_name = "Customer"
    sqlserver_name = "SMGCLIENTEPROVEEDOR"
    module_name = "Selling"

    optimized_mapping = [
        ("reup_code", ("CP.CliCodigo", "string")),
        ("customer_name", ("CP.CliDescripcion", "string")),
        ("territory", ("P.PaisDescripcion", "string")),
        ("default_currency", ("Calc.Curr", "string")),
        ("customer_type", ("Calc.CType", "string")),
        ("customer_group", ("TE.TipifiDescripcion", "string")),
        ("nit_code", ("CAST(CP.CliNit AS NVARCHAR(100))", "string")),
        (
            "identity_number",
            (
                "CASE WHEN Calc.CType = 'Individual' THEN CAST(CP.CliNit AS NVARCHAR(100)) ELSE NULL END",
                "string",
            ),
        ),
        # --- SUB-CONSULTA CONTROLADA Y NORMALIZADA DESDE SQL ---
        (
            "default_bank_accounts",
            (
                """(
            SELECT account_number
            FROM (
                SELECT 
                    -- Limpieza en SQL Server idéntica a lo que hará clean_name_field
                    LTRIM(RTRIM(DB.CliDBCuenta)) AS account_number,
                    ROW_NUMBER() OVER (
                        PARTITION BY DB.CliDBCuenta  -- agrupa por numero de numero de cuenta y ordena por titular
                        ORDER BY LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(DB.CliDBTitular, CHAR(9), ' '), CHAR(10), ' '), CHAR(13), ' ')))
                    ) AS rn
                FROM SCOCLIENTEDBANCARIOS AS DB
                INNER JOIN SCOENTFINAN AS EF 
                    ON DB.EntFinanCodigo = EF.EntFinanCodigo
                WHERE DB.CliCodigo = CP.CliCodigo
                  AND DB.CliDBEntFinanEstado = 1
                  AND EF.EntFinanActivo = 1
            ) AS Sub
            WHERE rn = 1
            FOR JSON PATH
        )""",
                "string",
            ),
        ),
        (
            "language",
            (
                """CASE 
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('ESPANOL', 'ESPAÑOL', 'SPANISH') THEN 'es'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('INGLES', 'ENGLISH') THEN 'en'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('CHINO') THEN 'zh'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('ITALIANO') THEN 'it'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('RUSO') THEN 'ru'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('POLACO') THEN 'pl'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('PORTUGUES', 'PORTUGUÉS') THEN 'pt'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('FRANCES', 'FRANCÉS') THEN 'fr'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('TURCO') THEN 'tr'
                        ELSE NULL
                    END""",
                "string",
            ),
        ),
        ("website", ("CP.CliSucurWEB", "string")),
        ("customer_primary_contact", ("CA_Contacto.Contacto", "string")),
        ("mobile_no", ("CP.CliTelefono", "string")),
        ("email_id", ("CP.CliEmail", "string")),
        # ("customer_primary_address", ("CP.CliDireccion", "string")),
        # (
        #     "payment_terms",
        #     (
        #         "CASE WHEN CP.CliExtranj = 0 THEN 30 ELSE NULL END",
        #         "string",
        #     ),
        # ),
        # (
        #     "customer_primary_address",
        #     (
        #         # Agregado lógica de respaldo para evitar vacíos
        #         # """CASE
        #         #     WHEN P.PaisDescripcion = 'Cuba' THEN ISNULL(NULLIF(CP.CliDireccion, ''), CP.CliCMDireccion)
        #         #     ELSE ISNULL(NULLIF(CP.CliCMDireccion, ''), CP.CliDireccion)
        #         # END""",
        #         """CASE
        #             WHEN P.PaisDescripcion = 'Cuba' THEN ISNULL(NULLIF(CP.CliDireccion, ''), 'Dirección no especificada')
        #             ELSE NULL
        #         END""",
        #         "string",
        #     ),
        # ),
    ]

    # IMPORTANTE: base_query_from debe empezar con "FROM"
    base_query_from = f"""
    FROM SMGCLIENTEPROVEEDOR AS CP
    LEFT JOIN SCOPAIS AS P ON CP.CliPaisCodIntern = P.PaisCodIntern
    LEFT JOIN SCOTIPIFEMPRESA AS TE ON CP.TipifiCodigo = TE.TipifiCodigo
    OUTER APPLY (
        SELECT TOP 1 
            TRIM(CONCAT(TRIM(C.CliContacNombre), ' ', TRIM(C.CliContacApellidos))) as Contacto
        FROM SCOCLIENTECONTACTOS AS C
        WHERE C.CliCodigo = CP.CliCodigo AND C.CliContacEstado = 1
    ) AS CA_Contacto
    CROSS APPLY (
        SELECT 
            CASE WHEN CP.CliTcpMiPyme = 'T' THEN 'Individual' ELSE 'Company' END as CType,
            CASE WHEN P.PaisDescripcion = 'Cuba' THEN 'CUP' ELSE 'USD' END as Curr,
            CASE WHEN P.PaisDescripcion = 'Cuba' THEN 'Empresa Estatal' ELSE 'USD' END as PList
    ) AS Calc
    WHERE
        CP.CliCategoria IN ({sql_in_clause(CUSTOMER_CATEGORIES)})
        AND CP.CliActivo = 1
    """

    order_clause = "ORDER BY CP.CliCodigo"

    cleaners = {
        "customer_name": clean_name_field,
        "territory": clean_name_field,
        "default_currency": clean_name_field,
        "customer_type": clean_name_field,
        "customer_group": clean_text_field,
        "nit_code": clean_numeric_field,
        "identity_number": clean_numeric_field,
        "default_bank_accounts": clean_json_to_list,
        "language": clean_name_field,
        "website": clean_website_field,
        "customer_primary_address": clean_text_field,
        "mobile_no": clean_phone_field,
        "email_id": clean_email_field,
        # "represents_company": clean_json_to_list,
        # "companies": clean_name_field,
    }

    print(base_query_from)

    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name + "-cliente",
        module_name=module_name,
        field_mapping=optimized_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause,
        save=export,
        field_cleaners=cleaners,
    )


# Obtener los proveedores y ponerle el alias con el nombre del campo en el doctype
def get_proveedores(db, export=False):
    doctype_name = "Supplier"
    sqlserver_name = "SMGCLIENTEPROVEEDOR"
    module_name = "Buying"

    # Mapeo optimizado: (Campo Destino, (Campo SQL o Alias de Calc, Tipo))
    optimized_mapping = [
        # ("reup_code", ("CP.CliCodigo", "string")),
        ("supplier_name", ("CP.CliDescripcion", "string")),
        ("country", ("P.PaisDescripcion", "string")),
        ("supplier_group", ("TE.TipifiDescripcion", "string")),
        ("supplier_type", ("Calc.CType", "string")),
        ("default_currency", ("Calc.Curr", "string")),
        # ("default_price_list", ("Calc.PList", "string")),
        # ("language", ("CP.CliHabla", "string")),
        (
            "language",
            (
                """CASE 
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('ESPANOL', 'ESPAÑOL', 'SPANISH') THEN 'Español'
                        WHEN UPPER(LTRIM(RTRIM(CP.CliHabla))) COLLATE Latin1_General_CI_AI IN ('INGLES', 'ENGLISH') THEN 'Inglés'
                        ELSE NULL 
                    END""",
                "string",
            ),
        ),
        ("website", ("CP.CliSucurWEB", "string")),
        ("supplier_primary_contact", ("CA_Contacto.Contacto", "string")),
        ("mobile_no", ("CP.CliTelefono", "string")),
        ("email_id", ("CP.CliEmail", "string")),
        # ("supplier_primary_address", ("CP.CliDireccion", "string")),
        ("nit_code", ("CAST(CP.CliNit AS NVARCHAR(100))", "string")),
        ("reup_code", ("CP.CliCodigo", "string")),
        # (
        #     "payment_terms",
        #     (
        #         "CASE WHEN CP.CliExtranj = 0 THEN 30 ELSE NULL END",
        #         "string",
        #     ),
        # ),
        # (
        #     "supplier_primary_address",
        #     (
        #         # Agregado lógica de respaldo para evitar vacíos
        #         # """CASE
        #         #     WHEN P.PaisDescripcion = 'Cuba' THEN ISNULL(NULLIF(CP.CliDireccion, ''), CP.CliCMDireccion)
        #         #     ELSE ISNULL(NULLIF(CP.CliCMDireccion, ''), CP.CliDireccion)
        #         # END""",
        #         # "string",
        #         """CASE
        #             WHEN P.PaisDescripcion = 'Cuba' THEN ISNULL(NULLIF(CP.CliDireccion, ''), 'Dirección no especificada')
        #             ELSE NULL
        #         END""",
        #         "string",
        #     ),
        # ),
    ]

    # Base query usando CROSS APPLY para la lógica de negocio (País -> Moneda/Lista Precios)
    base_query_from = f"""
    FROM SMGCLIENTEPROVEEDOR AS CP
    LEFT JOIN SCOPAIS AS P ON CP.CliPaisCodIntern = P.PaisCodIntern
    LEFT JOIN SCOTIPIFEMPRESA AS TE ON CP.TipifiCodigo = TE.TipifiCodigo
    OUTER APPLY (
        SELECT TOP 1 
            TRIM(CONCAT(TRIM(C.CliContacNombre), ' ', TRIM(C.CliContacApellidos))) as Contacto
        FROM SCOCLIENTECONTACTOS AS C
        WHERE C.CliCodigo = CP.CliCodigo AND C.CliContacEstado = 1
    ) AS CA_Contacto
    CROSS APPLY (
        SELECT 
            'Company' as CType,
            CASE WHEN P.PaisDescripcion = 'Cuba' THEN 'CUP' ELSE 'USD' END as Curr,
            CASE WHEN P.PaisDescripcion = 'Cuba' THEN 'Empresa Estatal' ELSE 'USD' END as PList
    ) AS Calc
    WHERE 
        TRIM(UPPER(CP.CliCategoria)) IN ({sql_in_clause(SUPPLIER_CATEGORIES)})
        AND CP.CliActivo = 1
    """

    order_clause = "ORDER BY CP.CliCodigo"

    cleaners = {
        "supplier_name": clean_name_field,
        "country": clean_name_field,
        "supplier_group": clean_name_field,
        "supplier_type": clean_name_field,
        "default_currency": clean_name_field,
        "language": clean_name_field,
        "website": clean_website_field,
        "supplier_primary_contact": clean_text_field,
        "mobile_no": clean_phone_field,
        "email_id": clean_email_field,
        "nit_code": clean_numeric_field,
        "reup_code": clean_numeric_field,
        # "supplier_primary_address": clean_text_field,
    }

    # Usamos export_table_to_json_paginated para mantener la misma lógica que Clientes
    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name + "-proveedor",
        module_name=module_name,
        field_mapping=optimized_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause,
        save=export,
        field_cleaners=cleaners,
    )


# def get_bank_accounts(db, export=False):
#     doctype_name = "Bank Account"
#     sqlserver_name = "SCOCLIENTEDBANCARIOS"
#     module_name = "Accounts"

#     # CASE centralizado para el tipo de banco
#     bank_type_case = """
#         CASE
#             WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%METROP%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANME%' THEN 'BANMET'
#             WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANDE%' THEN 'BANDEC'
#             WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BFI%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%FINANC%' THEN 'BFI'
#             WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BPA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%POPU%' THEN 'BPA'
#             WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BNC%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%NACIO%' THEN 'BNC'
#             WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BICSA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%COMERC%' THEN 'BICSA'
#             ELSE 'EXTRANJERO'
#         END"""

#     # Query unificada usando CliDescripcion en ambos casos
#     query = f"""
#         SELECT DISTINCT
#             DB.CliDBTitular AS account_name,
#             DB.CliDBCuenta AS bank_account_no,
#             {bank_type_case} AS bank_type,
#             EF.EntFinanDescripcion AS bank,
#             '' AS party_type,
#             '' AS party,
#             DB.CliDBIBAN AS iban,
#             EF.EntFinanCodigo AS branch_code
#         FROM SCOClIENTEDBANCARIOS AS DB
#         INNER JOIN SCOENTFINAN AS EF ON DB.EntFinanCodigo = EF.EntFinanCodigo
#         INNER JOIN SMGCLIENTEPROVEEDOR AS CP ON DB.CliCodigo = CP.CliCodigo
#         WHERE DB.CliDBEntFinanEstado = 1 AND EF.EntFinanActivo = 1 AND CP.CliActivo = 1
#           AND TRIM(UPPER(CP.CliCategoria)) IN ('C', 'A', 'CP', 'L', 'LP', 'LR')

#         UNION

#         SELECT DISTINCT
#             DB.CliDBTitular AS account_name,
#             DB.CliDBCuenta AS bank_account_no,
#             {bank_type_case} AS bank_type,
#             EF.EntFinanDescripcion AS bank,
#             'Supplier' AS party_type,
#             CP.CliDescripcion AS party,
#             DB.CliDBIBAN AS iban,
#             EF.EntFinanCodigo AS branch_code
#         FROM SCOClIENTEDBANCARIOS AS DB
#         INNER JOIN SCOENTFINAN AS EF ON DB.EntFinanCodigo = EF.EntFinanCodigo
#         INNER JOIN SMGCLIENTEPROVEEDOR AS CP ON DB.CliCodigo = CP.CliCodigo
#         WHERE DB.CliDBEntFinanEstado = 1 AND EF.EntFinanActivo = 1 AND CP.CliActivo = 1
#           AND TRIM(UPPER(CP.CliCategoria)) IN ('P', 'A', 'CP', 'R', 'LP', 'LR')
#     """

#     field_mapping = [
#         ("account_name", ("account_name", "string")),
#         ("bank_account_no", ("bank_account_no", "string")),
#         ("bank_type", ("bank_type", "string")),
#         ("bank", ("bank", "string")),
#         ("party_type", ("party_type", "string")),
#         ("party", ("party", "string")),
#         ("iban", ("iban", "string")),
#         ("branch_code", ("branch_code", "string")),
#     ]

#     cleaners = {
#         "account_name": clean_name_field,
#         "account_number": clean_name_field,
#         "bank_type": clean_name_field,
#         "bank": clean_name_field,
#         "party_type": clean_name_field,
#         "party": clean_name_field,
#         "branch_code": clean_name_field,
#     }

#     print(query)

#     return export_table_to_json(
#         db=db,
#         doctype_name=doctype_name,
#         sqlserver_name=sqlserver_name + "-cuentas_bancarias",
#         module_name=module_name,
#         field_mapping=field_mapping,
#         table_query=query,
#         save=export,
#         field_cleaners=cleaners,
#     )


def get_bank_accounts(db, export=False):
    doctype_name = "Bank Account"
    sqlserver_name = "SCOCLIENTEDBANCARIOS"
    module_name = "Accounts"

    bank_type_case = """
        CASE 
            WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%METROP%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANME%' THEN 'BANMET'
            WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANDE%' THEN 'BANDEC'
            WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BF%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%FINANC%' THEN 'BFI'
            WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BPA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%POPU%' THEN 'BPA'
            WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BNC%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%NACIO%' THEN 'BNC'
            WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BICSA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%COMERC%' THEN 'BICSA'
            ELSE 'EXTRANJERO' 
        END"""

    # query = f"""
    #     WITH AllAccounts AS (
    #         -- Clientes (sin party)
    #         SELECT DISTINCT
    #             -- Aplicamos el reemplazo de caracteres invisibles en SQL
    #             LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(DB.CliDBTitular, CHAR(9), ' '), CHAR(10), ' '), CHAR(13), ' '))) AS account_name,
    #             DB.CliDBCuenta       AS bank_account_no,
    #             {bank_type_case}     AS bank_type,
    #             EF.EntFinanDescripcion AS bank,
    #             ''                   AS party_type,
    #             ''                   AS party,
    #             DB.CliDBIBAN         AS iban,
    #             EF.EntFinanCodigo    AS branch_code
    #         FROM SCOClIENTEDBANCARIOS AS DB
    #         INNER JOIN SCOENTFINAN          AS EF ON DB.EntFinanCodigo = EF.EntFinanCodigo
    #         INNER JOIN SMGCLIENTEPROVEEDOR  AS CP ON DB.CliCodigo      = CP.CliCodigo
    #         WHERE DB.CliDBEntFinanEstado = 1
    #           AND EF.EntFinanActivo      = 1
    #           AND CP.CliActivo           = 1
    #           AND TRIM(UPPER(CP.CliCategoria)) IN ({sql_in_clause(CUSTOMER_CATEGORIES)})

    #         UNION ALL

    #         -- Proveedores (con party)
    #         SELECT DISTINCT
    #             -- Aplicamos el mismo reemplazo aquí
    #             LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(DB.CliDBTitular, CHAR(9), ' '), CHAR(10), ' '), CHAR(13), ' '))) AS account_name,
    #             DB.CliDBCuenta       AS bank_account_no,
    #             {bank_type_case}     AS bank_type,
    #             EF.EntFinanDescripcion AS bank,
    #             'Supplier'           AS party_type,
    #             CP.CliDescripcion    AS party,
    #             DB.CliDBIBAN         AS iban,
    #             EF.EntFinanCodigo    AS branch_code
    #         FROM SCOClIENTEDBANCARIOS AS DB
    #         INNER JOIN SCOENTFINAN          AS EF ON DB.EntFinanCodigo = EF.EntFinanCodigo
    #         INNER JOIN SMGCLIENTEPROVEEDOR  AS CP ON DB.CliCodigo      = CP.CliCodigo
    #         WHERE DB.CliDBEntFinanEstado = 1
    #           AND EF.EntFinanActivo      = 1
    #           AND CP.CliActivo           = 1
    #           AND TRIM(UPPER(CP.CliCategoria)) IN ({sql_in_clause(SUPPLIER_CATEGORIES)})
    #     ),
    #     Ranked AS (
    #         SELECT *,
    #             ROW_NUMBER() OVER (
    #                 PARTITION BY bank_account_no         -- agrupa duplicados por número de cuenta
    #                 ORDER BY
    #                     CASE WHEN party_type = 'Supplier' THEN 0 ELSE 1 END,  -- Supplier gana siempre
    #                     account_name
    #             ) AS rn
    #         FROM AllAccounts
    #     )
    #     SELECT
    #         account_name,
    #         bank_account_no,
    #         bank_type,
    #         bank,
    #         party_type,
    #         party,
    #         iban,
    #         branch_code
    #     FROM Ranked
    #     WHERE rn = 1
    # """
    query = f"""
        WITH AllAccounts AS (
            -- Clientes (sin party)
            SELECT DISTINCT
                -- Aplicamos el reemplazo de caracteres invisibles en SQL
                LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(DB.CliDBTitular, CHAR(9), ' '), CHAR(10), ' '), CHAR(13), ' '))) AS account_name,
                DB.CliDBCuenta       AS bank_account_no,
                {bank_type_case}     AS bank_type,
                EF.EntFinanDescripcion AS bank,
                ''                   AS party_type,
                ''                   AS party,
                DB.CliDBIBAN          AS iban,
                EF.EntFinanCodigo    AS branch_code
            FROM SCOClIENTEDBANCARIOS AS DB
            INNER JOIN SCOENTFINAN          AS EF ON DB.EntFinanCodigo = EF.EntFinanCodigo
            INNER JOIN SMGCLIENTEPROVEEDOR  AS CP ON DB.CliCodigo      = CP.CliCodigo
            WHERE DB.CliDBEntFinanEstado = 1
              AND EF.EntFinanActivo      = 1
              AND CP.CliActivo           = 1
              AND TRIM(UPPER(CP.CliCategoria)) IN ({sql_in_clause(CUSTOMER_CATEGORIES)})

            UNION ALL

            -- Proveedores (con party)
            SELECT DISTINCT
                -- Aplicamos el mismo reemplazo aquí
                LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(DB.CliDBTitular, CHAR(9), ' '), CHAR(10), ' '), CHAR(13), ' '))) AS account_name,
                DB.CliDBCuenta       AS bank_account_no,
                {bank_type_case}     AS bank_type,
                EF.EntFinanDescripcion AS bank,
                'Supplier'           AS party_type,
                CP.CliDescripcion    AS party,
                DB.CliDBIBAN          AS iban,
                EF.EntFinanCodigo    AS branch_code
            FROM SCOClIENTEDBANCARIOS AS DB
            INNER JOIN SCOENTFINAN          AS EF ON DB.EntFinanCodigo = EF.EntFinanCodigo
            INNER JOIN SMGCLIENTEPROVEEDOR  AS CP ON DB.CliCodigo      = CP.CliCodigo
            WHERE DB.CliDBEntFinanEstado = 1
              AND EF.EntFinanActivo      = 1
              AND CP.CliActivo           = 1
              AND TRIM(UPPER(CP.CliCategoria)) IN ({sql_in_clause(SUPPLIER_CATEGORIES)})
        ),
        Ranked AS (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY bank_account_no
                    ORDER BY
                        CASE WHEN party_type = 'Supplier' THEN 0 ELSE 1 END,
                        account_name
                ) AS rn
            FROM AllAccounts
        )
        SELECT
            account_name,
            bank_account_no,
            bank_type,
            bank,
            party_type,
            party,
            iban,
            branch_code
        FROM Ranked
        WHERE rn = 1
    """

    field_mapping = [
        ("account_name", ("account_name", "string")),
        ("bank_account_no", ("bank_account_no", "string")),
        ("bank_type", ("bank_type", "string")),
        ("bank", ("bank", "string")),
        ("party_type", ("party_type", "string")),
        ("party", ("party", "string")),
        ("iban", ("iban", "string")),
        ("branch_code", ("branch_code", "string")),
    ]

    cleaners = {
        "account_name": clean_name_field,
        "bank_account_no": clean_name_field,
        "bank_type": clean_name_field,
        "bank": clean_name_field,
        "party_type": clean_name_field,
        "party": clean_name_field,
        "branch_code": clean_name_field,
        "iban": clean_iban_field,
    }

    print(query)

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name + "-cuentas_bancarias",
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
        field_cleaners=cleaners,
    )


def get_contactos(db, export=False, grouped=False):
    doctype_name = "Contact"
    sqlserver_name = "SCOCLIENTECONTACTOS"
    module_name = "CRM"

    # Mapeo de campos: alias -> (campo SQL, tipo)
    field_mapping = [
        ("first_name", ("C.CliContacNombre", "string")),
        ("last_name", ("C.CliContacApellidos", "string")),
        ("mobile_no", ("C.CliContacTlfno", "string")),
        ("email_id", ("C.CliContacEmail", "string")),
        ("identity_number", ("C.CliContacCI", "string")),
        ("cli_codigo", ("CP.CliCodigo", "string")),
        ("cli_categoria", ("CP.CliCategoria", "string")),
        ("cli_descripcion", ("CP.CliDescripcion", "string")),
    ]

    # Construcción de SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT
            {", ".join(select_clauses)}
        FROM SCOCLIENTECONTACTOS AS C
        LEFT JOIN SMGCLIENTEPROVEEDOR AS CP
            ON C.CliCodigo = CP.CliCodigo
        WHERE C.CliContacTlfno != '' AND C.CliContacEmail != ''
            AND CP.CliActivo = 1
    """

    print(query)

    print(f"Export: {export}, Grouped: {grouped}")

    try:
        # 1) Extraer datos planos
        rows = fetch_table_data(db, field_mapping, query)

        # if export:
        if grouped:
            # 2) Transformar a formato padre-hijo de Frappe
            contactos = [transform_contact_row(row) for row in rows]

            # 3) Guardar con la estructura esperada
            output_path = save_json_file(
                doctype_name, contactos, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")

            return contactos
        else:
            # return rows
            # ¡OJO AQUÍ! Si no viene agrupado, también hay que limpiar los campos individuales
            # Camino seguro: Mantiene los datos intactos pero repara el correo textualmente
            rows_limpias = []
            for row in rows:
                row_copia = row.copy()
                correo_limpio = clean_email_field(row.get("email_id"))
                if not correo_limpio:
                    original = str(row.get("email_id", ""))
                    correo_limpio = (
                        original.split(" ")[0].split("\xa0")[0].lower().strip()
                    )
                row_copia["email_id"] = correo_limpio
                # AQUÍ el cambio: usar clean_phone_field en vez de solo quitar ';'
                row_copia["mobile_no"] = clean_phone_field(row.get("mobile_no")) or ""
                row_copia["first_name"] = str(row.get("first_name", "")).strip()
                row_copia["last_name"] = str(row.get("last_name", "")).strip()
                rows_limpias.append(row_copia)
            return rows_limpias

    except Exception as e:
        logging.error(f"Error exportando {doctype_name}: {e}")
        raise


def transform_contact_row(row: dict) -> dict:
    """Convierte en estructura padre-hijo de Contact aplicando los limpiadores correspondientes"""

    # 1. Limpiar y procesar los campos antes de asignarlos
    # (Asegúrate de que estas funciones estén importadas en este archivo)
    first_name = clean_name_field(row.get("first_name"))
    last_name = clean_name_field(row.get("last_name"))
    identity_number = clean_name_field(row.get("identity_number"))

    mobile_no = clean_phone_field(row.get("mobile_no"))
    email_id = clean_email_field(row.get("email_id"))

    # 2. Construir la estructura base del contacto con datos limpios
    contact = {
        "first_name": first_name,
        "last_name": last_name,
        "identity_number": identity_number,
        "phone_nos": [],
        "email_ids": [],
        "links": [],
    }

    # 3. Validar que el teléfono sea válido tras la limpieza antes de agregarlo
    if mobile_no:
        contact["phone_nos"].append(
            {
                "phone": mobile_no,
                "is_primary_mobile_no": 1,
            }
        )

    # 4. Validar que el email sea válido tras la limpieza.
    # Si clean_email_field devolvió None (por ejemplo por traer " Activo"), NO se agregará.
    if email_id:
        contact["email_ids"].append({"email_id": email_id, "is_primary": 1})

    # Agregar links basado en la categoría del cliente/proveedor (limpiando códigos)
    categoria = row.get("cli_categoria", "").strip().upper()
    cli_codigo = clean_name_field(row.get("cli_codigo"))
    cli_descripcion = clean_name_field(row.get("cli_descripcion"))

    if cli_codigo and cli_descripcion:
        if categoria in ["C", "CP", "L", "LP", "LR"]:
            contact["links"].append(
                {"link_doctype": "Customer", "link_name": cli_descripcion}
            )
        if categoria in ["P", "CP", "R", "CR", "LR"]:
            contact["links"].append(
                {"link_doctype": "Supplier", "link_name": cli_descripcion}
            )

    return contact


# def transform_contact_row(row: dict) -> dict:
#     """Convierte en estructura padre-hijo de Contact"""

#     contact = {
#         "first_name": row.get("first_name"),
#         "last_name": row.get("last_name"),
#         "identity_number": row.get("identity_number"),
#         "phone_nos": [],
#         "email_ids": [],
#         "links": [],
#     }

#     if row.get("mobile_no"):
#         contact["phone_nos"].append(
#             {
#                 "phone": row["mobile_no"],
#                 "is_primary_mobile_no": 1,
#             }
#         )

#     if row.get("email_id"):
#         contact["email_ids"].append({"email_id": row["email_id"], "is_primary": 1})

#     # Agregar links basado en la categoría del cliente/proveedor
#     categoria = row.get("cli_categoria", "").strip().upper()
#     cli_codigo = row.get("cli_codigo")
#     cli_descripcion = row.get("cli_descripcion")

#     if cli_codigo and cli_descripcion:
#         if categoria in ["C", "CP", "L", "LP", "LR"]:
#             # Es cliente
#             contact["links"].append(
#                 {"link_doctype": "Customer", "link_name": cli_descripcion}
#             )
#         if categoria in ["P", "CP", "R", "CR", "LR"]:
#             # Es proveedor
#             contact["links"].append(
#                 {"link_doctype": "Supplier", "link_name": cli_descripcion}
#             )

#     return contact


# Funcion que muestra los contactos por clientes/proveedores pero solo para el endpoint
def get_clientes_con_contactos(db):
    # Mapeo de campos: alias -> (campo SQL, tipo)
    field_mapping = [
        ("cli_codigo", ("CP.CliCodigo", "string")),
        ("cli_descripcion", ("CP.CliDescripcion", "string")),
        ("cli_categoria", ("CP.CliCategoria", "string")),
        ("cli_direccion", ("CP.CliDireccion", "string")),
        ("categoria", (None, "string")),  # Valor derivado con CASE
        ("cantidad_contactos", ("COUNT(C.CliCodigo)", "integer")),
        (
            "contactos",
            (
                "STRING_AGG(CONCAT(C.CliContacNombre COLLATE DATABASE_DEFAULT, ' ', C.CliContacApellidos COLLATE DATABASE_DEFAULT, ' (', C.CliContacTlfno COLLATE DATABASE_DEFAULT, ', ', C.CliContacEmail COLLATE DATABASE_DEFAULT, ')'), ' | ')",
                "string",
            ),
        ),
    ]

    # Construcción de SELECT
    select_clauses = []
    for alias, (sql_field, _) in field_mapping:
        if alias == "categoria":
            clause = """
                CASE
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'C' THEN 'Cliente'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'P' THEN 'Proveedor'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'A' THEN 'Ambos'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'CP' THEN 'Cliente y Proveedor'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'L' THEN 'Cliente Potencial'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'R' THEN 'Proveedor Potencial'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'CR' THEN 'Cliente y proveedor potencial'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'LP' THEN 'Cliente potencial y proveedor'
                    WHEN TRIM(UPPER(CP.CliCategoria)) = 'LR' THEN 'Cliente potencial y Proveedor potencial'
                    ELSE NULL
                END AS categoria
            """
        else:
            clause = f"{sql_field} AS {alias}"
        select_clauses.append(clause)

    query = f"""
    SELECT
        {", ".join(select_clauses)}
    FROM SCOCLIENTECONTACTOS AS C
    LEFT JOIN SMGCLIENTEPROVEEDOR AS CP
        ON C.CliCodigo = CP.CliCodigo
    WHERE
        C.CliContacTlfno IS NOT NULL AND C.CliContacTlfno != ''
        AND C.CliContacEmail IS NOT NULL AND C.CliContacEmail != ''
        AND CP.CliActivo = 1
        AND TRIM(UPPER(CP.CliCategoria)) IN ('C', 'P', 'A', 'CP', 'L', 'R', 'CR', 'LP', 'LR')
    GROUP BY
        CP.CliCodigo, CP.CliDescripcion, CP.CliCategoria,
        CP.CliDireccion
    ORDER BY CP.CliDescripcion;
    """

    return fetch_table_data(db, field_mapping, query)


# def get_banks(db, export=False):
#     doctype_name = "Bank"
#     sqlserver_name = "SCOEntFinan"
#     module_name = "Accounts"

#     # 1. Modificamos el mapeo para incluir la limpieza de SQL directamente aquí
#     field_mapping = [
#         ("bank_name", ("TRIM(UPPER(EF.EntFinanDescripcion))", "string")),
#         ("bank_type", (None, "string")),
#         ("swift_number", ("TRIM(UPPER(CLD.CliDBSWIFT))", "string")),
#     ]

#     select_clauses = []
#     for alias, (sql_field, _) in field_mapping:
#         if alias == "bank_type":
#             # Nota: Cambié los LIKE a MAYÚSCULAS dentro del CASE ya que el campo evaluado
#             # ya tiene UPPER. Esto evita que falle la coincidencia en el motor SQL.
#             clause = """
#                 CASE
#                     WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%METROP%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANME%' THEN 'BANMET'
#                     WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANDE%' THEN 'BANDEC'
#                     WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BFI%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%FINANC%' THEN 'BFI'
#                     WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BPA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%POPU%' THEN 'BPA'
#                     WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BNC%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%NACIO%' THEN 'BNC'
#                     WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BICSA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%COMERC%' THEN 'BICSA'
#                     ELSE 'EXTRANJERO'
#                 END AS bank_type
#             """
#         else:
#             # Aquí se generará automáticamente: TRIM(UPPER(EF.EntFinanDescripcion)) AS bank_name
#             # y también: TRIM(UPPER(CLD.CliDBSWIFT)) AS swift_number
#             clause = f"{sql_field} AS {alias}"
#         select_clauses.append(clause.strip())

#     query = f"""
#         SELECT DISTINCT
#             {", ".join(select_clauses)}
#         FROM SCOENTFINAN AS EF INNER JOIN SCOClIENTEDBANCARIOS AS CLD ON EF.EntFinanCodigo = CLD.EntFinanCodigo
#         WHERE  (EF.EntFinanActivo = 1) AND (CLD.CliDBEntFinanEstado = 1)
#     """

#     print(query)

#     cleaners = {
#         "bank_name": clean_name_field,
#         "bank_type": clean_name_field,
#         "swift_number": clean_name_field,
#     }

#     return export_table_to_json(
#         db=db,
#         doctype_name=doctype_name,
#         sqlserver_name=sqlserver_name + "-bancos",
#         module_name=module_name,
#         field_mapping=field_mapping,
#         table_query=query,
#         save=export,
#         field_cleaners=cleaners,
#     )


def get_banks(db, export=False):
    doctype_name = "Bank"
    sqlserver_name = "SCOEntFinan"
    module_name = "Accounts"

    field_mapping = [
        ("bank_name", ("TRIM(UPPER(EF.EntFinanDescripcion))", "string")),
        ("bank_type", (None, "string")),
    ]

    # Reconstruimos el query usando GROUP BY en lugar de DISTINCT
    query = """
        SELECT 
            TRIM(UPPER(EF.EntFinanDescripcion)) AS bank_name,
            CASE 
                WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%METROP%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANME%' THEN 'BANMET' 
                WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BANDE%' THEN 'BANDEC' 
                WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BF%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%FINANC%' THEN 'BFI' 
                WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BPA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%POPU%' THEN 'BPA' 
                WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BNC%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%NACIO%' THEN 'BNC' 
                WHEN TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%BICSA%' OR TRIM(UPPER(EF.EntFinanDescripcion)) LIKE '%COMERC%' THEN 'BICSA' 
                ELSE 'EXTRANJERO'
            END AS bank_type
        FROM SCOENTFINAN AS EF 
        INNER JOIN SCOClIENTEDBANCARIOS AS CLD ON EF.EntFinanCodigo = CLD.EntFinanCodigo 
        WHERE (EF.EntFinanActivo = 1) AND (CLD.CliDBEntFinanEstado = 1)
        GROUP BY 
            TRIM(UPPER(EF.EntFinanDescripcion))
    """

    print(query)

    cleaners = {
        "bank_name": clean_name_field,
        "bank_type": clean_name_field,
    }

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name + "-bancos",
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
        field_cleaners=cleaners,
    )


def get_bank_type(db, export=False):
    doctype_name = "Bank"
    sqlserver_name = "SNOCONFIGURACION"
    module_name = "Accounts"
    field_mapping = [
        ("bank_name", (None, "string")),
        ("bank_type", (None, "string")),
        ("description", (None, "string")),
        ("swift_number", (None, "string")),
        ("code", (None, "string")),
    ]

    query = """
        SELECT 'Banco Metropolitano'  AS bank_name, 'BANMET'     AS bank_type, 'Banco Metropolitano'  AS description, 'BMNBCUHH' AS swift_number, '22' AS code
        UNION ALL
        SELECT 'Banco de crédito y comercio',      'BANDEC',     'Banco de crédito y comercio',      'BDCRCUHH', '20'
        UNION ALL
        SELECT 'Banco financiero internacional',   'BFI',        'Banco financiero internacional',   'BFICCUHH', '23'
        UNION ALL
        SELECT 'Banco popular de ahorro',          'BPA',        'Banco popular de ahorro',          'BPAHCUHH', '12'
        UNION ALL
        SELECT 'Banco internacional de comercio',  'BICSA',      'Banco internacional de comercio',  'BIDCCUHH', '11'
        UNION ALL
        SELECT 'Banco nacional de Cuba',           'BNC',        'Banco nacional de Cuba',           'BNACESM1', '21'
        UNION ALL
        SELECT 'Bancos extranjeros',               'EXTRANJERO', 'Bancos extranjeros',               '',         '15'
    """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name + "-bancos",
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
    )


def get_direcciones(db, export=False, grouped=False):
    doctype_name = "Address"
    sqlserver_name = "SMGCLIENTEPROVEEDOR"
    module_name = "Contacts"

    field_mapping = [
        ("address_title", (None, "string")),
        ("address_type", (None, "string")),
        ("address_line1", (None, "string")),
        # ("state", (None, "string")),  # Provincia
        # ("city", (None, "string")),  # Municipio
        ("state", ("CP.ProvCod", "string")),  # Provincia
        ("city", ("CP.MunicCod", "string")),  # Municipio
        ("country", ("P.PaisDescripcion", "string")),
        ("cli_categoria", ("CP.CliCategoria", "string")),
        ("cli_descripcion", ("CP.CliDescripcion", "string")),
    ]

    # --- AJUSTE AQUÍ: Construcción inteligente del SELECT ---
    select_clauses = []
    for alias, (sql_field, _) in field_mapping:
        if alias == "address_type":
            clause = f"'Office' AS {alias}"
        elif alias in ["address_title", "address_line1"]:
            clause = f"ISNULL(NULLIF(TRIM(CP.CliDireccion), ''), 'Dirección no especificada') as {alias}"
        else:
            # Para los campos que sí tienen un valor en el mapeo (como country o categoria)
            clause = f"{sql_field} as {alias}"

        select_clauses.append(clause)

    query = f"""
            SELECT
                {", ".join(select_clauses)}
            FROM SMGCLIENTEPROVEEDOR AS CP
            LEFT JOIN SCOPAIS AS P ON CP.CliPaisCodIntern = P.PaisCodIntern
            WHERE CP.CliActivo = 1
            AND P.PaisDescripcion = 'Cuba'
            AND (NULLIF(CP.CliDireccion, '') IS NOT NULL)
        """

    print(query)

    print(f"Export: {export}, Grouped: {grouped}")
    try:
        # 1) Extraer datos planos
        rows = fetch_table_data(db, field_mapping, query)

        # Aplicando limpiadores
        cleaners = {
            "address_title": clean_address_custom,
            "address_type": clean_text_field,
            "address_line1": clean_address_custom,
            "city": clean_name_field,
            "state": clean_name_field,
            "country": clean_name_field,
            "cli_descripcion": clean_name_field,
        }
        rows = apply_field_cleaners(rows, cleaners)

        # if export:
        if grouped:
            # 2) Transformar a formato padre-hijo de Frappe
            # direcciones = [transform_direccion_row(row) for row in rows]
            direcciones = []
            for row in rows:
                # --- LÓGICA DE EXCLUSIÓN ESTRICTA ---
                # Validamos que AMBOS existan y no sean solo espacios
                state_val = str(row.get("state") or "").strip()
                city_val = str(row.get("city") or "").strip()

                if state_val and city_val:
                    # Solo si ambos tienen datos, se procesa la dirección
                    direcciones.append(transform_direccion_row(row))
                else:
                    # Si falta cualquiera de los dos, se ignora el registro
                    continue

            # 3) Guardar con la estructura esperada
            output_path = save_json_file(
                doctype_name, direcciones, module_name, sqlserver_name
            )
            logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")

            return direcciones
        else:
            return rows

    except Exception as e:
        logging.error(f"Error exportando {doctype_name}: {e}")
        raise


def transform_direccion_row(row: dict) -> dict:
    """Convierte en estructura padre-hijo de Direcciones"""

    direccion = {
        "address_title": row.get("address_title"),
        "address_type": row.get("address_type"),
        "address_line1": row.get("address_line1"),
        "state": row.get("state"),
        "city": row.get("city"),
        "country": row.get("country"),
        "links": [],
    }

    # Agregar links basado en la categoría del cliente/proveedor
    categoria = str(row.get("cli_categoria") or "").strip().upper()
    cli_descripcion = row.get("cli_descripcion")

    if cli_descripcion:
        if categoria in ["A", "C", "CP", "L", "LP", "LR", "CR"]:
            direccion["links"].append(
                {"link_doctype": "Customer", "link_name": cli_descripcion}
            )

        if categoria in ["A", "P", "CP", "R", "CR", "LR", "LP"]:
            direccion["links"].append(
                {"link_doctype": "Supplier", "link_name": cli_descripcion}
            )

    return direccion
