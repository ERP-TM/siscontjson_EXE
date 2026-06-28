import datetime
import logging
import json
import csv
from typing import Dict, List
from utils.jsons_utils import export_table_to_json

# Para obtener las Facturas de Compras desde Cobros y Pagos y poniendo alias con el nombre
# del campo en el doctype

def get_pago_con_saldo(db) -> list:
    saldo_por_documento = Saldo_restante(db)
    
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT PD.PagdoaeId, PD.PagdoaeDoc, CP.CliDescripcion, PD.PagdoaeFecha, PD.PagdoaeImporteMN
            FROM [SCPPAGODOCUMENTO] as PD
            LEFT JOIN [SMGCLIENTEPROVEEDOR] as CP ON PD.CliCodigo = CP.CliCodigo
            ORDER BY PD.PagdoaeId
        """)
        
        registros = cursor.fetchall()

    resultados = []
    for row in registros:
        pagdoaeId = row.PagdoaeId
        saldo = saldo_por_documento.get(pagdoaeId, 0)

        resultado = {
            "invoice_number": row.PagdoaeDoc,
            "party_type": "Supplier",
            "party": row.CliDescripcion,
            "temporary_opening_account": "699005 - Apertura - T",
            "posting_date": row.PagdoaeFecha,
            "due_date": "",
            "item_name": "Opening Invoice Item",
            "outstanding_amount": row.PagdoaeImporteMN - saldo,
            "qty": 1,
            "cost_center": "",
            "expense_element": ""
        }
        resultados.append(resultado)

    return resultados  # Retorna lista de dict con datos para CSV


def Saldo_restante(db):
    saldo_por_documento = {}
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT 
                SCPPAGODOCUMENTO.PagdoaeId, SCPPAGODOCUMENTO.PagdoaeDoc, SCPPAGODOCUMENTO.PagdoaeImporteMN,
                COALESCE(SUM(SCPPAGOCONT.PagCtaeImporte), 0) AS saldo
            FROM SCPPAGODOCUMENTO
            LEFT OUTER JOIN SCPPAGOFACTURA ON SCPPAGOFACTURA.PagFaaeIdDoc = SCPPAGODOCUMENTO.PagdoaeId
            LEFT OUTER JOIN SCPPAGOCONT ON SCPPAGOCONT.PagaeId = SCPPAGOFACTURA.PagaeId
                AND SCPPAGOCONT.PagCtaeDebito = 1 
            WHERE SCPPAGODOCUMENTO.PagdoaeEstado IN (0, 1)
            GROUP BY SCPPAGODOCUMENTO.PagdoaeId,SCPPAGODOCUMENTO.PagdoaeDoc,SCPPAGODOCUMENTO.PagdoaeImporteMN
        """)

        for row in cursor.fetchall():
            saldo_por_documento[row.PagdoaeId] = row.saldo

    print(saldo_por_documento)
    return saldo_por_documento


def json_a_csv(json_result, nombre_archivo='resultado.csv'):
    # Convertir JSON string a lista de diccionarios
    datos = json.loads(json_result)

    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
        if len(datos) > 0:
            campos = datos[0].keys()
            escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(datos)

    








#    # Aquí puedes exportar resultados a JSON usando tu función
#    return export_table_to_json(
#        db=db,
#        doctype_name="Purchase Invoice",
#        sqlserver_name="SCPPAGODOCUMENTO",
#        module_name="Setup",
#        field_mapping=[  # ajusta si es necesario
#            ("invoice_number", ("PagdoaeDoc", 'string')),
#            ("party_type", ("Supplier", 'string')),
#            ("party", ("CliDescripcion", 'string')),
#            ("temporary_opening_account", ("699005 - Apertura - T", 'string')),
#            ("posting_date", ("PagdoaeFecha", 'string')),
#            ("due_date", ("", 'string')),
#            ("item_name", ("Opening Invoice Item", 'string')),
#            ("outstanding_amount", ("outstanding_amount", 'float')),
#            ("qty", ("1", 'int')),
#            ("cost_center", ("", 'string')),
#            ("expense_element", ("", 'string'))
#        ],
#        table_query=resultados
#        #data=resultados  # Pasar los datos ya procesados
#    )



