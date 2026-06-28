import datetime
import logging
from typing import Dict, List
from utils.jsons_utils import export_table_to_json, \
    export_table_to_json_paginated

# Para obtener las Facturas de Compras desde Cobros y Pagos y poniendo alias con el nombre
# del campo en el doctype
def get_factura_compra(db):
    doctype_name = "Purchase Invoice"
    sqlserver_name = "SCPPAGODOCUMENTO"
    module_name = "Setup"

    field_mapping = [
        ("invoice_number", ("PagdoaeDoc", 'string')),
        ("party_type", ("Supplier", 'string')),        
        ("party", ("CliDescrip", 'string')),  
        ("temporary_opening_account", ("699005 - Apertura - T", 'string')),  
        ("posting_date", ("PagdoaeFecha", 'string')), 
        ("due_date", ("NULL", 'string')),  # Campo vacío reemplazado por NULL
        ("item_name", ("Opening Invoice Item", 'string')),  
        ("outstanding_amount", ("1234", 'string')), # analizar esto. es la cant restante 
        ("qty", ("1", 'string')),
        ("cost_center", ("NULL",'')),  # Campo vacío reemplazado por NULL
        ("expense_element", ("NULL",''))  # Campo vacío reemplazado por NULL
    ]

    query = f"""
    SELECT 
        PD.PagdoaeDoc as invoice_number, 
        'Supplier' as party_type, 
        CP.CliDescripcion as party, 
        '699005 - Apertura - T' as temporary_opening_account,
        PD.PagdoaeFecha as posting_date, 
        CONVERT(VARCHAR(10), PD.PagdoaeFecha, 103) as posting_date,
        '' as due_date, 
        'Opening Invoice Item' as item_name, 
        ISNULL(saldos.saldo, 0) as outstanding_amount, 
        '1' as qty, 
        '' as cost_center, 
        '' as expense_element
    FROM [SCPPAGODOCUMENTO] as PD 
    INNER JOIN [SMGCLIENTEPROVEEDOR] as CP ON PD.CliCodigo = CP.CliCodigo
    LEFT JOIN (
    SELECT 
        SCPPAGODOCUMENTO.PagdoaeId, 
        SCPPAGODOCUMENTO.PagdoaeDoc, 
        SCPPAGODOCUMENTO.PagdoaeImporteMN,
        (SCPPAGODOCUMENTO.PagdoaeImporteMN - COALESCE(SUM(SCPPAGOCONT.PagCtaeImporte), 0)) AS saldo
    FROM SCPPAGODOCUMENTO
    LEFT OUTER JOIN SCPPAGOFACTURA ON SCPPAGOFACTURA.PagFaaeIdDoc = SCPPAGODOCUMENTO.PagdoaeId
    LEFT OUTER JOIN SCPPAGOCONT ON SCPPAGOCONT.PagaeId = SCPPAGOFACTURA.PagaeId AND SCPPAGOCONT.PagCtaeDebito = 1 
    WHERE SCPPAGODOCUMENTO.PagdoaeEstado IN (0, 1)
    GROUP BY SCPPAGODOCUMENTO.PagdoaeId, SCPPAGODOCUMENTO.PagdoaeDoc, SCPPAGODOCUMENTO.PagdoaeImporteMN
    ) saldos ON saldos.PagdoaeId = PD.PagdoaeId
    WHERE PD.PagdoaeEstado IN (0, 1)
    """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )

def get_factura_ventas(db):
    doctype_name = "Sales Invoice"
    sqlserver_name = "SCPCOBRODOCUMENTO"
    module_name = "Setup"

    field_mapping = [
        ("invoice_number", ("CobdoaeDoc", 'string')),
        ("party_type", ("Customer", 'string')),        
        ("party", ("CliDescrip", 'string')),  
        ("temporary_opening_account", ("699005 - Apertura - T", 'string')),  
        ("posting_date", ("CobdoaeFecha", 'string')), 
        ("due_date", ("NULL", 'string')),  # Campo vacío reemplazado por NULL
        ("item_name", ("Opening Invoice Item", 'string')),  
        ("outstanding_amount", ("1234", 'string')), # analizar esto. es la  cant restante 
        ("qty", ("1", 'string')),
        ("cost_center", ("NULL",'')),  # Campo vacío reemplazado por NULL
        ("expense_element", ("NULL",''))  # Campo vacío reemplazado por NULL
    ]

    query = f"""
    SELECT CD.CobdoaeDoc as invoice_number,
        'Customer' as party_type,
        CP.CliDescripcion as party,
        '699005 - Apertura - T' as temporary_opening_account,
        CONVERT(VARCHAR(10), CD.CobdoaeFecha, 103) as posting_date,
        '' as due_date,
        'Opening Invoice Item' as item_name,
        ISNULL(saldos.saldo, 0) as outstanding_amount,
        '1' as qty,
        '' as cost_center,
        '' as expense_element
    FROM[SCPCOBRODOCUMENTO] as CD
    INNER JOIN[SMGCLIENTEPROVEEDOR] as CP ON CD.CliCodigo = CP.CliCodigo
    LEFT JOIN(    
    SELECT 
        SCPCOBRODOCUMENTO.CobdoaeId, 
        SCPCOBRODOCUMENTO.CobdoaeDoc, SCPCOBRODOCUMENTO.CobdoaeImporteMN,
        (SCPCOBRODOCUMENTO.CobdoaeImporteMN - COALESCE(SUM(SCPCOBROCONT.CobCtaeImporte), 0)) AS saldo
    FROM SCPCOBRODOCUMENTO
    LEFT OUTER JOIN SCPCOBROFACTURA ON SCPCOBROFACTURA.CobFaaeIdDoc = SCPCOBRODOCUMENTO.CobdoaeId
    LEFT OUTER JOIN SCPCOBROCONT ON SCPCOBROCONT.CobaeId = SCPCOBROFACTURA.CobaeId
    AND SCPCOBROCONT.CobCtaeDebito = 1 
    WHERE SCPCOBRODOCUMENTO.CobdoaeEstado IN (0, 1)
    GROUP BY SCPCOBRODOCUMENTO.CobdoaeId,SCPCOBRODOCUMENTO.CobdoaeDoc,SCPCOBRODOCUMENTO.CobdoaeImporteMN)
    saldos on saldos.CobdoaeId = CD.CobdoaeId where CD.CobdoaeEstado IN (0, 1)
    """
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query)

def get_pagos_anticipados(db):
    doctype_name = "Payment Entry"
    sqlserver_name = "SCPPAGO"
    module_name = "Setup"

    field_mapping = [
        ("payment_type", ("Pay", 'string')),
        ("party_type", ("Supplier", 'string')),
        ("party", ("CP.CliDescripcion", 'string')),
        ("paid_amount", ("PC.PagCtaeImporte", 'string')),
        ("received_amount", ("PC.PagCtaeImporte", 'string')),
        ("base_received_amount", ("PC.PagCtaeImporte", 'string')),
        ("posting_date", ("P.PagaeFecha", 'string')),
        ("mode_of_payment", ("MP.tdbaeDescripcion", 'string')),
        ("paid_from", ("CC.ClCuDescripcion", 'string')),
        ("paid_from_account_currency", ("CUP", 'string')),
        ("paid_to", ("CC.ClCuDescripcion", 'string')),
        ("paid_to_account_currency", ("CUP", 'string')),
        ("company", ("DE.DatEntNom", 'string')),
        ("reference_no", ("PD.PagdoaeDoc", 'string')),
        ("reference_date", ("PD.PagdoaeFecha", 'string')),
        ("is_opening", ("Si", 'string')),
        ("unallocated_amount", ("1234", 'string'))
    ]

    query = f"""
         WITH ReceivedAmount AS (
            SELECT 
                PD.PagdoaeId, 
                SUM(CASE 
                    WHEN PD.MonCodigo = 100 THEN P.PagaeImporteMN 
                    ELSE P.PagaeImporteMEX
                END) AS received_amount
            FROM SCPPAGODOCUMENTO AS PD 
            INNER JOIN SCPPAGO AS P ON PD.PagdoaeId = P.PagdoaeId 
            WHERE P.TransaeCodigo = 17 
              AND P.PagaeFuncion = 9 
              AND PD.PagdoaeEstado <> 2 
              AND P.PagaeOperacion <> 3
            GROUP BY PD.PagdoaeId
        )
        SELECT 
            Pd.PagdoaeId, 
            'Pay' AS payment_type, 
            'Supplier' AS party_type,
            MAX(CP.CliDescripcion) AS party,
            MAX(CASE WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN ELSE PD.PagdoaeImporteMEX END) AS paid_amount,
            MAX(CASE WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN ELSE PD.PagdoaeImporteMEX END) AS received_amount,
            MAX(CASE WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN ELSE PD.PagdoaeImporteMEX END) AS base_received_amount,
            MAX(PD.PagdoaeFecha) AS posting_date,
            MAX(TD.tdbaeDescripcion) AS mode_of_payment,
            MAX(Debito.ClCuDescripcion) AS paid_from,
            MAX(M.MonSiglas) AS paid_from_account_currency,
            MAX(SMGDATOSENTIDAD.DatEntNom) AS company,
            MAX(PD.PagdoaeDoc) AS reference_no,
            MAX(PD.PagdoaeFecha) AS reference_date,
            'Si' AS is_opening,
            MAX(CASE 
                WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN - COALESCE(RA.received_amount, 0)
                ELSE PD.PagdoaeImporteMEX - COALESCE(RA.received_amount, 0)
            END) AS unallocated_amount
        FROM 
            SCPPAGODOCUMENTO AS PD 
        INNER JOIN
            SCPPAGO AS P ON PD.PagdoaeId = P.PagdoaeId 
        OUTER APPLY (
            SELECT TOP 1 CC.ClCuDescripcion
            FROM SCPPAGOCONT AS PCONT
            INNER JOIN SCGCLASIFICADORDECUENTAS AS CC ON PCONT.ClcuIDCuenta = CC.ClcuIDCuenta
            WHERE PCONT.PagaeId = P.PagaeId AND PCONT.PagCtaeDebito = 1
        ) AS Debito
        INNER JOIN SMGCLIENTEPROVEEDOR AS CP ON PD.CliCodigo = CP.CliCodigo
        INNER JOIN SCPTIPODOCUMENTOBANCARIO AS TD ON PD.tdbaeCodigo = TD.tdbaeCodigo
        CROSS JOIN SMGDATOSENTIDAD
        INNER JOIN SMGNOMMONEDAS AS M ON PD.MonCodigo = M.MonCodigo
        LEFT JOIN ReceivedAmount AS RA ON PD.PagdoaeId = RA.PagdoaeId
        WHERE 
            PD.PagdoaeEstado <> 2 AND P.PagaeCausa = 10 AND P.PagaeFuncion = 8 AND P.TransaeCodigo = 13 AND P.PagaeOperacion <> 3
        GROUP BY PD.PagdoaeId;
       """
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
    )

def get_cobros_anticipados(db):
        doctype_name = "Payment Entry"
        sqlserver_name = "SCPCOBRO"
        module_name = "Setup"

        field_mapping = [
            ("naming_series", ("ACC-PAY-.YYYY.-", 'string')),
            ("payment_type", ("Receive", 'string')),
            ("party_type", ("Customer", 'string')),
            ("party", ("CP.CliDescripcion", 'string')),
            ("paid_amount", ("CCont.CobCtaeImporte", 'string')),
            ("received_amount", ("CCont.PagCtaeImporte", 'string')),
            ("base_received_amount", ("CCont.PagCtaeImporte", 'string')),
            ("posting_date", ("C.CobaeFecha", 'string')),
            ("mode_of_payment", ("TD.tdbaeDescripcion", 'string')),
            ("paid_from", ("CC.ClCuDescripcion", 'string')),
            ("paid_from_account_currency", ("CUP", 'string')),
            ("paid_to", ("CC.ClCuDescripcion", 'string')),
            ("paid_to_account_currency", ("CUP", 'string')),
            ("reference_no", ("CD.CobdoaeDoc", 'string')),
            ("reference_date", ("CD.CoddoaeFecha", 'string')),
            ("is_opening", ("Si", 'string')),
            ("unallocated_amount", ("1234", 'string'))
        ]

        query = f"""
            WITH ReceivedAmount AS (
                SELECT 
                    CD.CobdoaeId, 
                    SUM(CASE 
                        WHEN CD.MonCodigo = 100 THEN C.CobaeImporteMN  
                        ELSE C.CobaeImporteMEX
                    END) AS received_amount
                FROM SCPCOBRODOCUMENTO AS CD 
                INNER JOIN SCPCOBRO AS C ON CD.CobdoaeId = C.CobdoaeId 
                WHERE 
                    C.TransaeCodigo = 15 
                    AND C.CobaeFuncion = 9 
                    AND CD.CobdoaeEstado <> 2 
                    AND C.CobaeOperacion <> 3
                GROUP BY CD.CobdoaeId                   
            )
            SELECT 
                'ACC-PAY-.YYYY.-' AS naming_series, 
                'Receive' AS payment_type, 
                'Customer' AS party_type,
                MAX(CP.CliDescripcion) AS party,
                MAX(CASE WHEN CD.MonCodigo = 100 THEN CD.CobdoaeImporteMN ELSE CD.CobdoaeImporteMEX END) AS paid_amount,
                MAX(RA.received_amount) AS received_amount,
                MAX(CASE WHEN CD.MonCodigo = 100 THEN CD.CobdoaeImporteMN ELSE CD.CobdoaeImporteMEX END) AS base_received_amount,
                MAX(CD.CobdoaeFecha) AS posting_date,
                MAX(TD.tdbaeDescripcion) AS mode_of_payment,
                MAX((CAST(Credito.ClCuCuenta AS VARCHAR(10)) + 
                    CAST(Credito.ClCuSubcuenta AS VARCHAR(10)) + 
                    CASE 
                        WHEN Credito.ClCuSubControl <> 0 OR Credito.ClCuAnalisis <> 0 
                            THEN CAST(Credito.ClCuSubControl AS VARCHAR(10))
                        ELSE ''
                    END)) AS paid_to,
                MAX((CAST(Debito.ClCuCuenta AS VARCHAR(10)) + 
                    CAST(Debito.ClCuSubcuenta AS VARCHAR(10)) + 
                    CASE 
                        WHEN Debito.ClCuSubControl <> 0 OR Debito.ClCuAnalisis <> 0 
                            THEN CAST(Debito.ClCuSubControl AS VARCHAR(10))
                        ELSE ''
                    END)) AS paid_from,
                COALESCE(
                    (SELECT TOP 1 M.MonSiglas
                    FROM SCPCOBRO AS C 
                    INNER JOIN SMGNOMMONEDAS AS M ON C.CobaeMoneda = M.MonCodigo
                    WHERE C.CobdoaeId = CD.CobdoaeId 
                    ORDER BY C.CobaeFecha DESC), 
                    MAX(M.MonSiglas)
                ) AS paid_to_account_currency,
                MAX(CD.CobdoaeDoc) AS reference_no,
                MAX(CD.CobdoaeFecha) AS reference_date,
                'Yes' AS is_opening,
                MAX(CASE 
                    WHEN CD.MonCodigo = 100 THEN CD.CobdoaeImporteMN - COALESCE(RA.received_amount, 0)
                    ELSE CD.CobdoaeImporteMEX - COALESCE(RA.received_amount, 0)
                END) AS unallocated_amount
            FROM SCPCOBRODOCUMENTO AS CD 
            INNER JOIN SCPCOBRO AS C ON CD.CobdoaeId = C.CobdoaeId 
            
            OUTER APPLY (
                SELECT  TOP 1 CC.ClCuCuenta, CC.ClCuSubcuenta, CC.ClCuSubControl, CC.ClCuAnalisis
                FROM SCPCOBROCONT AS CCONT
                INNER JOIN 
                    SCGCLASIFICADORDECUENTAS AS CC ON CCONT.ClcuIDCuenta = CC.ClcuIDCuenta
                WHERE 
                    CCONT.CobaeId = C.CobaeId AND CCONT.CobCtaeDebito = 0
                ) AS Debito
            OUTER APPLY (
                SELECT  TOP 1 CC.ClCuCuenta, CC.ClCuSubcuenta, CC.ClCuSubControl, CC.ClCuAnalisis
                FROM SCPCOBROCONT AS CCONT
                INNER JOIN 
                    SCGCLASIFICADORDECUENTAS AS CC ON CCONT.ClcuIDCuenta = CC.ClcuIDCuenta
                WHERE 
                    CCONT.CobaeId = C.CobaeId AND CCONT.CobCtaeDebito = 1
                GROUP BY 
                    CC.ClCuCuenta, CC.ClCuSubcuenta, cc.ClCuSubControl, cc.ClCuAnalisis
            ) AS Credito
            INNER JOIN SMGCLIENTEPROVEEDOR AS CP ON CD.CliCodigo = CP.CliCodigo
            INNER JOIN SCPTIPODOCUMENTOBANCARIO AS TD ON CD.tdbaeCodigo = TD.tdbaeCodigo
            INNER JOIN SMGNOMMONEDAS AS M ON CD.MonCodigo = M.MonCodigo
            LEFT JOIN ReceivedAmount AS RA ON CD.CobdoaeId = RA.CobdoaeId
            WHERE 
                CD.CobdoaeEstado <> 2 AND C.CobaeCausa = 10 AND C.CobaeFuncion = 8 AND C.TransaeCodigo = 10 AND C.CobaeOperacion <> 3
            GROUP BY CD.CobdoaeId
            HAVING MAX(CASE 
            WHEN CD.MonCodigo = 100 THEN CD.CobdoaeImporteMN - COALESCE(RA.received_amount, 0)
            ELSE CD.CobdoaeImporteMEX - COALESCE(RA.received_amount, 0)
            END) <> 0; 
        """
        return export_table_to_json(
            db=db,
            doctype_name=doctype_name,
            sqlserver_name=sqlserver_name,
            module_name=module_name,
            field_mapping=field_mapping,
            table_query=query,
        )

def get_doc_crediticios(db):
    doctype_name = "Payment Entry"
    sqlserver_name = "SCPPAGO"
    module_name = "Setup"

    field_mapping = [
       ("payment_type", ("Pay", 'string')),
       ("party_type", ("Supplier", 'string')),
       ("party", ("CP.CliDescripcion", 'string')),
       ("paid_amount",("PC.PagCtaeImporte", 'string')),
       ("received_amount",("PC.PagCtaeImporte", 'string')),
       ("base_received_amount",("PC.PagCtaeImporte", 'string')),
       ("posting_date",("P.PagaeFecha", 'string')),
       ("mode_of_payment",("MP.tdbaeDescripcion", 'string')),
       ("paid_from",("CC.ClCuDescripcion", 'string')),
       ("paid_from_account_currency",("CUP", 'string')),
       ("paid_to",("CC.ClCuDescripcion", 'string')),
       ("paid_to_account_currency",("CUP", 'string')),
       ("company",("DE.DatEntNom", 'string')),
       ("reference_no",("PD.PagdoaeDoc", 'string')),
       ("reference_date",("PD.PagdoaeFecha", 'string')),
       ("is_opening",("Si", 'string')),
       ("unallocated_amount",("1234", 'string'))
    ]

    query = f"""
            WITH ReceivedAmount AS (
                SELECT 
                    PD.PagdoaeId, 
                    SUM(CASE 
                        WHEN PD.MonCodigo = 100 THEN P.PagaeImporteMN 
                        ELSE P.PagaeImporteMEX
                    END) AS received_amount
                FROM SCPPAGODOCUMENTO AS PD 
                INNER JOIN SCPPAGO AS P ON PD.PagdoaeId = P.PagdoaeId 
                WHERE P.TransaeCodigo = 31 
                  AND P.PagaeFuncion = 16 
                  AND PD.PagdoaeEstado <> 2 
                  AND P.PagaeOperacion <> 3
                GROUP BY PD.PagdoaeId
            )
            SELECT 
                PD.PagdoaeId,
                'Pay' AS payment_type,
                'Supplier' AS party_type,
                MAX(CP.CliDescripcion) AS party,
                MAX(CASE WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN ELSE PD.PagdoaeImporteMEX END) AS paid_amount,
                MAX(CASE WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN ELSE PD.PagdoaeImporteMEX END) AS received_amount,
                MAX(CASE WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN ELSE PD.PagdoaeImporteMEX END) AS base_received_amount,
                MAX(PD.PagdoaeFecha) AS posting_date,
                MAX(TD.tdbaeDescripcion) AS mode_of_payment,
                MAX(Debito.ClCuDescripcion) AS paid_from,
                MAX(M.MonSiglas) AS paid_to_account_currency,
                MAX(SMGDATOSENTIDAD.DatEntNom) AS company,
                MAX(PD.PagdoaeDoc) AS reference_no,
                MAX(PD.PagdoaeFecha) AS reference_date,
                'Si' AS is_opening,
                MAX(CASE 
                    WHEN PD.MonCodigo = 100 THEN PD.PagdoaeImporteMN - COALESCE(RA.received_amount, 0)
                    ELSE PD.PagdoaeImporteMEX - COALESCE(RA.received_amount, 0)
                END) AS unallocated_amount
            FROM SCPPAGODOCUMENTO AS PD
            INNER JOIN SCPPAGO AS P ON PD.PagdoaeId = P.PagdoaeId
            OUTER APPLY (
                SELECT TOP 1 CC.ClCuDescripcion
                FROM SCPPAGOCONT AS PCONT
                INNER JOIN SCGCLASIFICADORDECUENTAS AS CC ON PCONT.ClcuIDCuenta = CC.ClcuIDCuenta
                WHERE PCONT.PagaeId = P.PagaeId AND PCONT.PagCtaeDebito = 1
            ) AS Debito
            INNER JOIN SMGCLIENTEPROVEEDOR AS CP ON PD.CliCodigo = CP.CliCodigo
            INNER JOIN SCPTIPODOCUMENTOBANCARIO AS TD ON PD.tdbaeCodigo = TD.tdbaeCodigo
            CROSS JOIN SMGDATOSENTIDAD
            INNER JOIN SMGNOMMONEDAS AS M ON PD.MonCodigo = M.MonCodigo
            LEFT JOIN ReceivedAmount AS RA ON PD.PagdoaeId = RA.PagdoaeId
            WHERE PD.PagdoaeEstado <> 2 
              AND P.PagaeCausa = 14 
              AND P.PagaeFuncion = 8 
              AND P.TransaeCodigo = 13 
              AND P.PagaeOperacion <> 3
            GROUP BY PD.PagdoaeId;
         """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
    )

    # Payment Type → debe ser Receive (si es anticipo de cliente) o  Pay (si es anticipo a proveedor).
    # Party Type → Customer o Supplier.
    # Party → el cliente o proveedor específico. CliDescripcion
    # Paid Amount → el monto del anticipo en la moneda del documento.
    # Received Amount → el monto recibido (normalmente igual al anterior, salvo comisiones).
    # Base Received Amount → el monto convertido a la moneda base de la empresa.
    # Posting Date → la fecha de la operación (normalmente la fecha de apertura).  fecha de hoy
    # Mode of Payment → efectivo, transferencia, etc.  tdbaeDescrpcion
    # Bank/Cash Account → la cuenta contable donde se registró el anticipo.
    # Company → la empresa correspondiente.
    # Reference No - PagdoaeDoc
    # Reference Date - PagdoaeFecha
    # is_opening -> Si
    # unallocated_amount saldo que queda por liquidar

def get_tipo_docbancario(db):
    doctype_name = "Mode of Payment"
    sqlserver_name = "SCPTIPODOCUMENTOBANCARIO"
    module_name = "Setup"

    field_mapping = [
        ("name", ("TD.tdbaeDescripcion", 'string')),
        ("creation", ("TD.tdbaeFechaModif", 'string')),
        ("mode_of_payment", ("TD.tdbaeDescripcion", 'string')),
        ("enabled", ("1", 'string')),
        ("type", ("Bank", 'string'))
    ]

    query = f"""
        SELECT TD.tdbaeDescripcion AS name, 
               TD.tdbaeFechaModif AS creation, 
               TD.tdbaeDescripcion AS mode_of_payment,
               '1' AS enabled,
               CASE 
                   WHEN TD.tdbaeDescripcion = 'Efectivo' THEN 'Efectivo' 
                   ELSE 'Banco' 
               END AS type
        FROM SCPTIPODOCUMENTOBANCARIO AS TD
    """
    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
)