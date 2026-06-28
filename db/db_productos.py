import logging
import csv
import pandas as pd

from utils.jsons_utils import (
    export_table_to_json,
    serialize_value,
    fetch_table_data,
    save_json_file)

from sqlalchemy import text


# Para obtener los productos y poniendo alias con el nombre
# metodo para obtener los grupos de productos, en este caso se deja fijo, ya que ese dato no existe en SISCONT5
def get_grupo_productos(db,export=False):
    doctype_name = "Item Group"
    sqlserver_name = "Item Group"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (Grupo de Productos)
        ("item_group_name", ("Apertura de SISCONT5", 'string')),
        ("is_group", (1, "boolean")),
        # nombre del grupo de productos que se habilitó para los productos de SISCONT5

    ]

    # Construimos la cláusula SELECT
    query = f"""
    SELECT TOP (1) 
            'Servicios de Compras' as item_group_name,
            CAST(1 AS bit) as is_group
            FROM SCRNomenServiciosComprados
            WHERE (ServCActivo = '')
            
    UNION ALL
    
    SELECT TOP (1) 
            'Servicios de Ventas' as item_group_name,
            CAST(1 AS bit) as is_group
            FROM SCOSERVICIO
            WHERE (SVActiva = 1)

    UNION ALL
            
    SELECT TOP (1)
           'Apertura de SISCONT5' as item_group_name,
           CAST(1 AS bit) as is_group
            FROM SIVNOMPROD INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON SIVNOMPROD.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo INNER JOIN
            SMGNOMENCLADORUNIDADMEDIDA ON SIVNOMPROD.UMedId = SMGNOMENCLADORUNIDADMEDIDA.UMedId
            WHERE (SIVNOMPROD.ProduDesactiva = '') AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
            ORDER BY item_group_name
        """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
    )


# metodo para obtener los productos de la base de datos de SISCONT5
def get_productos(db):
    doctype_name = "Item"
    sqlserver_name = "SIVNOMPROD"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (Productos)
        ("item_group", ("Apertura de SISCONT5", 'string')),
        # nombre del grupo de productos que se habilitó para los productos de SISCONT5
        ("item_code", ("ProduCodigo", 'string')),  # identifica el código de producto
        ("stock_uom", ("UMedSiglas", 'string')),  # identifica la unidad de medida del producto
        ("item_name", ("ProduDescrip", 'string')),  # identifca el nombre del producto
        ("is_stock_item", (1, 'boolean')),  # identifca que el producto se mantiene en almacén
        ("description", ("ProduDescrip", 'string')),  # identifca el nombre detallado del producto
        ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
        ("has_batch_no", ("ProduLote", "string")),  # identifica si se define por lotes o no
        ("is_fixed_asset", (0, "boolean")),  # identifica que es o no un activo fijo
        ("asset_category", ("c", "string"))
    ]

    # Construimos la clausula SELECT
    query = """
            SELECT DISTINCT 
               'Apertura de SISCONT5' as item_group,
               CAST(SIVNOMPROD.ProduCodigo AS varchar(50)) as item_code,
               CAST(trim(SMGNOMENCLADORUNIDADMEDIDA.UMedSiglas) AS varchar(50)) as stock_uom,
               CAST(SIVNOMPROD.ProduDescrip AS varchar(255)) as item_name,
               CAST(1 AS bit) as is_stock_item,  -- Cambiado a bit para booleano
               CAST(trim(SIVNOMPROD.ProduDescripDetallada) AS varchar(MAX)) as description,
               CAST('Cuba' AS varchar(50)) as country_of_origin,
               CAST(CASE WHEN SIVNOMPROD.ProduLote = '1' THEN 1 ELSE 0 END AS bit) as has_batch_no,  -- Convertido a booleano
               CAST(0 AS bit) as is_fixed_asset,  -- Cambiado a bit para booleano
               CAST('' AS varchar(50)) as asset_category

            FROM SIVNOMPROD 
            INNER JOIN SIVEXISTENCIAMOVIMIENTO ON SIVNOMPROD.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo 
            INNER JOIN SMGNOMENCLADORUNIDADMEDIDA ON SIVNOMPROD.UMedId = SMGNOMENCLADORUNIDADMEDIDA.UMedId
            WHERE (SIVNOMPROD.ProduDesactiva = '') AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)

            UNION ALL
                        
            SELECT        
                CAST('Servicios de Compras' AS varchar(50)) AS item_group, 
                CAST(SCRNomenServiciosComprados.ServCCodigo AS varchar(25)) AS item_code, 
                CAST(SMGNOMENCLADORUNIDADMEDIDA.UMedSiglas AS varchar(3)) AS stock_uom, 
                trim(CAST(SCRNomenServiciosComprados.ServCDescripcion AS varchar(255))) AS item_name, 
                CAST(0 AS bit) AS is_stock_item, 
                CAST('' AS varchar(MAX)) AS description, 
                CAST('Cuba' AS varchar(50)) AS country_of_origin, 
                CAST(0 AS bit) AS has_batch_no, 
                CAST(0 AS bit) AS is_fixed_asset, 
                CAST('' AS varchar(50)) AS asset_category            
            
            FROM  SCRNomenServiciosComprados INNER JOIN
            SMGNOMENCLADORUNIDADMEDIDA ON SCRNomenServiciosComprados.ServCUMedId = SMGNOMENCLADORUNIDADMEDIDA.UMedId
            WHERE (SCRNomenServiciosComprados.ServCActivo = '')            
            
            UNION ALL
            
            SELECT
                CAST('Servicios de Ventas' AS varchar(50)) as item_group,        
                CAST(SCOSERVICIO.SVCodigo AS varchar(25)) as item_code,
                CAST(SMGNOMENCLADORUNIDADMEDIDA.UMedSiglas AS varchar(3)) as stock_uom,
                trim(CAST(SCOSERVICIO.SVDescripcion AS varchar(85))) as item_name,
                CAST(0 AS bit) as is_stock_item,
                CAST('' AS varchar(MAX)) as description,
                CAST('Cuba' AS varchar(50)) as country_of_origin,
                CAST(0 AS bit) as has_batch_no,
                CAST(0 AS bit) as is_fixed_asset,
                CAST('' AS varchar(50)) as asset_category
                           
            FROM  SCOSERVICIO INNER JOIN
            SMGNOMENCLADORUNIDADMEDIDA ON SCOSERVICIO.UMedId = SMGNOMENCLADORUNIDADMEDIDA.UMedId
            WHERE (SCOSERVICIO.SVActiva = 1)
            ORDER BY item_code
        """

    return export_table_dic_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
    )


# metodo para obtener las existencias en formato json, de los productos de SISCONT5
def get_existencias_json(db):
    """
    Este metodo retorna un documento de reconciliación de los inventarios (Stock Reconciliation) que se usan en el ERP,
    para lograr cargar las existencias de los productos que están en SISCONT5.
    """

    doctype_name = "Stock Reconciliation"
    sqlserver_name = "SIVEXISTENCIAMOVIMIENTOS"
    module_name = "Cuba"

    field_mapping = [
        ("purpose", ("Opening Stock", "string")),
        ("barcode", ("", "string")),
        ("has_item_scanned", ("0", "boolean")),
        ("item_code", ("NM.ProduCodigo", "string")),
        ("item_name", ("NM.ProduDescrip", "string")),
        ("item_group", ("Apertura de SISCONT5", "string")),
        ("warehouse", ("NA.NomAlmDescrip", "string")),
        ("qty", ("EM.ExMovCantidadFisica", "string")),
        ("valuation_rate", ("NM.ProduPrecioMN", "string")),
        ("amount", ("EM.ExMovImportMNResv", "string")),
        ("allow_zero_valuation_rate", ("0", "boolean")),
        ("use_serial_batch_fields", ("NM.ProduLote", "boolean")),
        ("reconcile_all_serial_batch", ("0", "boolean")),
        ("serial_and_batch_bundle", ("0", "boolean")),
        ("serial_no", ("0", "boolean")),
        ("batch_no", ("0", "boolean")),
        ("current_qty", ("0", "boolean")),
        ("current_amount", ("0", "boolean")),
        ("current_valuation_rate", ("0", "boolean")),
        ("current_serial_no", ("0", "boolean")),
        ("quantity_difference", ("0", "boolean")),
        ("amount_difference", ("0", "boolean")),
    ]

    query = """
                SELECT
                'Opening Stock' as purpose,
                '' as barcode,
                0 as has_item_scanned,
                CAST(NM.ProduCodigo AS VARCHAR(14)) as item_code,
                NM.ProduDescrip as item_name,
                'Apertura de SISCONT5' as item_group,
                TRIM(NA.NomAlmDescrip) + '_' +
                CAST(CCta.ClCuCuenta AS VARCHAR(10)) +
                CASE WHEN ISNULL(CCta.ClCuSubcuenta, '') <> '' 
                     THEN CAST(CCta.ClCuSubcuenta AS VARCHAR(10)) ELSE '' END +
                CASE WHEN ISNULL(CCta.ClCuSubControl, '') <> '' 
                     THEN CAST(CCta.ClCuSubControl AS VARCHAR(10)) ELSE '' END +
                CASE WHEN ISNULL(CCta.ClCuAnalisis, '') <> '' 
                     THEN CAST(CCta.ClCuAnalisis AS VARCHAR(10)) ELSE '' END as warehouse,
                EM.ExMovCantidadFisica as qty,
                NM.ProduPrecioMN as valuation_rate,
                EM.ExMovImportMNResv as amount,
                0 as allow_zero_valuation_rate,
                NM.ProduLote as use_serial_batch_fields,
                0 as reconcile_all_serial_batch,
                '' as serial_and_batch_bundle,
                '' as current_serial_and_batch_bundle,
                '' as serial_no,
                '' as batch_no,
                0 as current_qty,
                0 as current_amount,
                0 as current_valuation_rate,
                '' as current_serial_no,
                0 as quantity_difference,
                0 as amount_difference
            FROM SIVNOMALM AS NA
            INNER JOIN SIVEXISTENCIAMOVIMIENTO AS EM ON NA.NomAlmCod = EM.NomAlmCod
            INNER JOIN SIVNOMPROD AS NM ON EM.ProduCodigo = NM.ProduCodigo
            INNER JOIN SIVCTASCONFIG AS CC ON NM.CtaCGInvId = CC.CtaCGInvId
            INNER JOIN SCGCLASIFICADORDECUENTAS AS CCta ON CC.ClcuIDCuenta = CCta.ClcuIDCuenta
            WHERE NA.NomAlActivo = '' AND EM.ExMovCantidadFisica > 0
            ORDER BY EM.NomAlmCod, warehouse
            """

    try:
        # 1) Extraer datos planos
        rows = fetch_table_data(db, field_mapping, query)
        #print(f"Número de registros obtenidos: {len(rows)}")

        # 2) Crear estructura padre-hijo
        # El documento padre (Stock Reconciliation)
        documento_padre = {
            "purpose": "Opening Stock",
            "items": [],  # Aquí irán todos los items hijos
            "amended_from": None,
            "docstatus": 1,
            "naming_series": "MAT-RECO-.YYYY.-",
            "company": "",  # Ajusta este valor
            "posting_date": "",  # Ajusta la fecha según necesites
            "posting_time": "00:00:00",
            "set_posting_time": 0,
            "set_warehouse": "",
            "expense_account": "9910"       #temporalmente esta cuenta, para lograr ajustar las existencias
        }

        # 3) Agregar cada fila como un item hijo
        for row in rows:
            item_hijo = {
                "item_code": row.get("item_code"),
                "item_name": row.get("item_name"),
                "warehouse": row.get("warehouse"),
                "qty": row.get("qty"),
                "valuation_rate": row.get("valuation_rate"),
                "amount": row.get("amount"),
                "batch_no": row.get("batch_no"),
                "serial_no": row.get("serial_no"),
                "current_qty": 0,
                "current_valuation_rate": 0,
                "current_amount": 0,
                "quantity_difference": 0,   #row.get("qty"),
                "amount_difference": 0      #row.get("amount")
            }
            documento_padre["items"].append(item_hijo)

        # 4) Crear lista con el documento (puedes tener múltiples documentos)
        documentos = [documento_padre]

        # 5) Guardar con la estructura esperada, padre-hijo
        output_path = save_json_file(
            doctype_name, documentos, module_name, sqlserver_name
        )
        logging.info(f"{doctype_name}.json guardado correctamente en {output_path}")
        #print(f"Documento creado con {len(documento_padre['items'])} items")

        return documentos

    except Exception as e:
        logging.error(f"Error exportando {doctype_name}: {e}")
        raise

# metodo para obtener las existencias en formato csv, de los productos de SISCONT5
def get_existencias_csv(db):
    query = """
            SELECT
                '' as barcode,
                0 as has_item_scanned,
                CAST(NM.ProduCodigo AS VARCHAR(14)) as item_code,
                NM.ProduDescrip as item_name,
                'Apertura de SISCONT5' as item_group,
                TRIM(NA.NomAlmDescrip) + '_' +
                CAST(CCta.ClCuCuenta AS VARCHAR(10)) +
                CAST(CCta.ClCuSubcuenta AS VARCHAR(10)) +
                CAST(CCta.ClCuSubControl AS VARCHAR(10)) AS warehouse,
                EM.ExMovCantidadFisica as qty,
                NM.ProduPrecioMN as valuation_rate,
                EM.ExMovImportMNResv as amount,
                0 as allow_zero_valuation_rate,
                NM.ProduLote as use_serial_batch_fields,
                0 as reconcile_all_serial_batch,
                '' as serial_and_batch_bundle,
                '' as current_serial_and_batch_bundle,
                '' as serial_no,
                '' as batch_no,
                0 as current_qty,
                0 as current_amount,
                0 as current_valuation_rate,
                '' as current_serial_no,
                0 as quantity_difference,
                0 as amount_difference
            FROM SIVNOMALM AS NA
            INNER JOIN SIVEXISTENCIAMOVIMIENTO AS EM ON NA.NomAlmCod = EM.NomAlmCod
            INNER JOIN SIVNOMPROD AS NM ON EM.ProduCodigo = NM.ProduCodigo
            INNER JOIN SIVCTASCONFIG AS CC ON NM.CtaCGInvId = CC.CtaCGInvId
            INNER JOIN SCGCLASIFICADORDECUENTAS AS CCta ON CC.ClcuIDCuenta = CCta.ClcuIDCuenta
            WHERE NA.NomAlActivo = '' AND EM.ExMovCantidadFisica > 0
            ORDER BY EM.NomAlmCod
        """

    # Ejecuta la query de la BD con pandas sobre un DataFrame
    df_query = pd.read_sql_query(query, db)

    # encabezados del csv que corresponden a la descripción del dato
    visible_headers = [
        "Barcode", "Has Item Scanned", "Item Code", "Item Name", "Item Group",
        "Warehouse", "Quantity", "Valuation Rate", "Amount",
        "Allow Zero Valuation Rate", "Use Serial No / Batch Fields",
        "Reconcile All Serial Nos / Batches", "Serial / Batch Bundle",
        "Current Serial / Batch Bundle", "Serial No", "Batch No",
        "Current Qty", "Current Amount", "Current Valuation Rate",
        "Current Serial No", "Quantity Difference", "Amount Difference"
    ]

    # encabezados del csv que corresponden a la descripción del campo de la tabla del doctype
    technical_headers = [
        "barcode", "has_item_scanned", "item_code", "item_name", "item_group",
        "warehouse", "qty", "valuation_rate", "amount",
        "allow_zero_valuation_rate", "use_serial_batch_fields",
        "reconcile_all_serial_batch", "serial_and_batch_bundle",
        "current_serial_and_batch_bundle", "serial_no", "batch_no",
        "current_qty", "current_amount", "current_valuation_rate",
        "current_serial_no", "quantity_difference", "amount_difference"
    ]

    # proceso donde se comienza la escritura del fichero
    with open("existencias.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # Fila 1, datos de encabezados para ERPNext que son necesarios para lograr la carga del csv
        writer.writerow(["Editar en masa Items"])

        # Fila 2, Encabezados de descripción
        writer.writerow(visible_headers)

        # Fila 3, Encabezados de los nombres de los campos
        writer.writerow(technical_headers)

        # Fila 4,
        writer.writerow([""] * len(technical_headers))

        # Fila 5, datos de encabezados para ERPNext que son necesarios para lograr la carga del csv
        writer.writerow(["El formato CSV es sensible a mayÃºsculas y minÃºsculas"])

        # Fila 6, datos de encabezados para ERPNext que son necesarios para lograr la carga del csv
        writer.writerow(["No edite los encabezados que estÃ¡n preestablecidos en la plantilla"])

        # Fila 7, datos de encabezados para ERPNext que son necesarios para lograr la carga del csv
        writer.writerow(["------"])

        # Datos que tendrá el fichero csv
        for _, row in df_query.iterrows():
            writer.writerow([row[col] for col in technical_headers])

    #result = pd.read_csv("existencias.csv")
    return "existencias.csv"

    # doctype_name = "Stock Reconciliation"
    # sqlserver_name = "SIVEXISTENCIAMOVIMIENTO"
    # module_name = "Setup"
    #
    #
    # field_mapping = [
    #     # Campos del doctype principal (Existencias de apertura)
    #     ("barcode", (" ", 'string')),  # identifica el código de producto
    #     ("item_code", ("ProduCodigo", 'string')),  # identifica el código de producto
    #     ("item_name", ("ProduDescrip", 'string')),  # identifca el nombre del producto
    #     ("item_group", ("Apertura de SISCONT5", 'string')),
    #     # nombre del grupo de productos que se habilitó para los productos de SISCONT5
    #     ("warehouse", ("NomAlmDescrip", 'string')),  # identifica el almacén donde está ubicado el producto
    #     ("qty", ("ExMovCantidadFisica", 'string')),
    #     # identifca la cantidad que tiene el producto en el momento de la apertura
    #     ("valuation_rate", ("ProduPrecioMN", 'string')),
    #     # identifca el precio que tiene el producto en el momento de la apertura
    #     ("amount", ("ExMovImportMNResv", 'string')),
    #     # identifca el importe que tiene el producto en el momento de la apertura
    #     ("use_serial_batch_fields", ("ProduLote", "string"))  # identifica si se define por lotes o no
    # ]
    # # Construimos la cláusula SELECT
    #
    # query = f"""
    #               SELECT
    #               ' ' as barcode,
    #               NM.ProduCodigo as item_code,
    #               NM.ProduDescrip as item_name,
    #               'Apertura de SISCONT5' as item_group,
    #               trim(NA.NomAlmDescrip) + '_' + CAST(CCta.ClCuCuenta AS VARCHAR(10)) + CAST(CCta.ClCuSubcuenta AS VARCHAR(10)) + CAST(CCta.ClCuSubControl AS VARCHAR(10)) AS warehouse,
    #               EM.ExMovCantidadFisica as qty,
    #               NM.ProduPrecioMN as valuation_rate,
    #               EM.ExMovImportMNResv as amount,
    #               NM.ProduLote as use_serial_batch_fields
    #
    #               FROM SIVNOMALM AS NA INNER JOIN
    #                     SIVEXISTENCIAMOVIMIENTO AS EM ON NA.NomAlmCod = EM.NomAlmCod INNER JOIN
    #                     SIVNOMPROD AS NM ON EM.ProduCodigo = NM.ProduCodigo INNER JOIN
    #                     SIVCTASCONFIG AS CC ON NM.CtaCGInvId = CC.CtaCGInvId INNER JOIN
    #                     SCGCLASIFICADORDECUENTAS AS CCta ON CC.ClcuIDCuenta = CCta.ClcuIDCuenta
    #               WHERE        (NA.NomAlActivo = '') AND (EM.ExMovCantidadFisica > 0)
    #               GROUP BY NA.NomAlmCod, NA.NomAlmDescrip, NA.NomAlmUbicac, NA.NomAlActivo, NM.CtaCGInvId, CCta.ClCuCuenta, CCta.ClCuSubcuenta, CCta.ClCuSubControl, CCta.ClCuAnalisis, EM.ExMovCantidadFisica, EM.ExMovImportMNResv,
    #                          EM.NomAlmCod, NM.ProduCodigo, NM.ProduDescrip, NM.ProduPrecioMN, NM.ProduLote
    #
    #               ORDER BY EM.NomAlmCod
    #             """
    #
    # return export_table_to_json(
    #     db=db,
    #     doctype_name=doctype_name,
    #     sqlserver_name=sqlserver_name,
    #     module_name=module_name,
    #     field_mapping=field_mapping,
    #     table_query=query
    # )

def serialize_productos_aft(productos_aft):
    productos_serializados = []

    for producto in productos_aft:
        producto_serializado = {}

        for campo, (valor, tipo_campo) in producto:
            # Serializar el valor según su tipo
            valor_serializado = serialize_value(valor, tipo_campo)

            # Solo incluir en el resultado si no es None
            if valor_serializado is not None:
                producto_serializado[campo] = valor_serializado

        productos_serializados.append(producto_serializado)

    return productos_serializados

# metodo para crear un nuevo fichero json que contenga los datos de los productos que forman parte de un AFT
def get_productos_aft():
    productos_aft = [
        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999111", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 111", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 111", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("111 EDIFICACIONES DE MADERA O PLASTICO", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999112", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 112", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 112", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("112 EDIFICAIONES DE PANELERIA", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999113", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 113", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 113", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("113 EDIFIC.DE MAMPOSTERIA Y OTROS MATER", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999121", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 121", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 121", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("121 CONST.PUENTES DE ACERO,HIERR U HORM", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999122", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 122", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 122", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("122 CONSTRUCCIONES DE PUENTES DE MADERA", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999123", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 123", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 123", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("123 CONST.MUELLES,ESPIG.EMBARCA.DE MADE", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999124", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 124", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 124", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("124 CONST.MUELLES,ESPIG,EMBARCA,DE HORM", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999125", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 125", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 125", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("125 CONST.DIQUES SECOS,FLOTAN,VARADEROS", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999126", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 126", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 126", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("126 CONSTRUCCIONES DE SILOS Y TANQUES", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999130", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 130", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 130", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("130 OTRAS CONSTRUCCION. NO CLASIFICADAS", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999131", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 131", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 131", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("131 CONSTRUCCIONES MINERAS", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999211", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 211", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 211", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("211 MUEBLES Y ESTANTES", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999212", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 212", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 212", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("212 ENSERES Y EQUIPOS DE OFICINA", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999213", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 213", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 213", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("213 EQUIPOS DE COMPUTACION", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999311", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 311", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 311", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("311 EQUIPOS DE TRANSPORTE AEREO", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999321", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 321", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 321", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("321 EQUIPOS DE TRANSPORTE MARITIMO", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999331", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 331", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 331", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("331 EQUIPOS DE TRANSP.TERR.FERROVIARIO", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999332", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 332", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 332", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("332 EQUIPOS DE TRANSP.TERRESTRE LIGERO", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999333", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 333", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 333", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("333 OTROS EQUIPOS DE TRANSP.TERRESTRE", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999341", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 341", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 341", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("341 EQUIPOS TRANSP.CON DEPREC.UNITARIA", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999411", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 411", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 411", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("411 MAQUINARIAS EN GENERAL", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999421", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 421", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 421", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("421 MAQUINAR.Y EQUIP.CON DEP.UNITARIA", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999431", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 431", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 431", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("431 APARATOS Y EQUIP.TECNIC.ESPECIALES", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999511", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 511", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 511", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("511 ANIMALES DE TRABAJO", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999521", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 521", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 521", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("521 DEDIC.A RECRIA,PROD.LECHE O CARNE", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999611", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 611", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 611", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("611 PLANTACIONES AGRICOLAS PERMANENTES", "string"))},

        {("item_group", ("Apertura de SISCONT5", 'string')),
         # nombre del grupo de productos que se habilitó para los productos de SISCONT5
         ("item_code", ("9999711", 'string')),  # identifica el código de producto
         ("stock_uom", ("Nos.", 'string')),  # identifica la unidad de medida del producto
         ("item_name", ("APERTURA 711", 'string')),  # identifca el nombre del producto
         ("is_stock_item", (0, 'boolean')),  # identifca que el producto se mantiene en almacén
         ("description", ("APERTURA 711", 'string')),  # identifca el nombre detallado del producto
         ("country_of_origin", ("Cuba", "string")),  # identifica el pais de origen
         ("has_batch_no", ("0", "string")),  # identifica si se define por lotes o no
         ("is_fixed_asset", (1, "boolean")),  # identifica que es o no un activo fijo
         ("asset_category", ("711 OTROS ACTIVOS", "string"))}
    ]

    # Uso de la función
    productos_serializados = serialize_productos_aft(productos_aft)
    return productos_serializados


# Ejecuta consulta SQL, serializa los datos según tipo y guarda un archivo JSON.
def export_table_dic_to_json(db, doctype_name, sqlserver_name, module_name,
                             field_mapping, table_query) -> list:
    field_type_map = {alias: field_type for alias, (_, field_type) in
                      field_mapping}
    # llamando a la funcion que retorna la lista de los productos que corresponden a los AFT
    productos_aft = get_productos_aft()

    try:
        result = db.execute(text(table_query))
        columns = result.keys()
        rows = result.fetchall()
        result = [
            {
                key: serialize_value(value, field_type_map.get(key, 'auto'))
                for key, value in zip(columns, row)
            }
            for row in rows
        ]
        # concatenar listas
        result_final = result + productos_aft

        output_path = save_json_file(doctype_name, result_final, module_name,
                                     sqlserver_name)
        logging.info(
            f"{doctype_name}.json guardado correctamente en {output_path}")
        return result_final

    except Exception as e:
        logging.error(f"Error exportando {doctype_name}: {e}")
        raise


# función que retorna la lista de precios que tiene siscont, tanto las que son fijas, có la lista parametrizada que tienen algunas empresas que usan siscont
def get_lista_precios(db,export=False):
    doctype_name = "Price List"
    sqlserver_name = "Price List"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (Price List)
        ("price_list_name", ("CliDescripcion", 'string')),  # nombre de la lista de precios
        ("currency", ("CUP", 'string')),  # moneda que define la lista de precios
        ("enabled", (1, 'boolean')),  # define si la lista está habilitada para usar
        ("buying", (0, 'boolean')),  # usada para las compras
        ("selling", (1, 'boolean'))  # usada para las ventas
    ]

    # Construimos la cláusula SELECT
    # consulta que retorna todas las posibles listas de precios que tiene SISCONT
    query = f"""
        SELECT DISTINCT
        CONCAT(SMGCLIENTEPROVEEDOR.CliCodigo,' - ',
        SMGCLIENTEPROVEEDOR.CliDescripcion,' _CUP') as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        
        FROM ScoListaPrecioProducto 
        INNER JOIN SMGCLIENTEPROVEEDOR 
        ON ScoListaPrecioProducto.LPrecioClienteCodigo = SMGCLIENTEPROVEEDOR.CliCodigo
	    WHERE (ScoListaPrecioProducto.LPrecioTipo = 1) and (ScoListaPrecioProducto.LPrecioCUP <> 0)
	    
	    UNION ALL
	    
	    SELECT DISTINCT
        CONCAT(SMGCLIENTEPROVEEDOR.CliCodigo,' - ',
        SMGCLIENTEPROVEEDOR.CliDescripcion,' _USD') as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        
        FROM ScoListaPrecioProducto 
        INNER JOIN SMGCLIENTEPROVEEDOR 
        ON ScoListaPrecioProducto.LPrecioClienteCodigo = SMGCLIENTEPROVEEDOR.CliCodigo
	    WHERE (ScoListaPrecioProducto.LPrecioTipo = 1) and (ScoListaPrecioProducto.LPrecioMLC <> 0)

	    
	    UNION ALL
	    
	    SELECT TOP (1)
        'Precio de Ventas_CUP' as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        
        FROM  SIVNOMPROD
        WHERE (ProduDesactiva = '') AND (ProduPrecioVentMN <> 0)
	    
	    UNION ALL
	    
	    SELECT TOP (1)
        'Precio de Ventas_USD' as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        
        FROM  SIVNOMPROD
        WHERE (ProduDesactiva = '') AND (ProduPrecioVentMLC <> 0)
	    
	    UNION ALL
	    
	    SELECT TOP (1)
        'Precio de Ventas por Ficha de costo_CUP' as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
          
        FROM  SIVNOMPROD
        WHERE (ProduPrecioFCMN <> 0) AND (ProduDesactiva = '') AND (ProduFC = 1)
	    
	    UNION ALL
	    
	    SELECT TOP (1)
        'Precio de Ventas por Ficha de costo_USD' as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
          
        FROM  SIVNOMPROD
        WHERE (ProduPrecioFCMLC <> 0) AND (ProduDesactiva = '') AND (ProduFC = 1)
	    
	    UNION ALL
	    
	    SELECT DISTINCT 
        CONCAT(CAST(ScoListaPrecioProducto.LPrecioOrganismoCodigo  AS VARCHAR),' - ',TEORGANISMO.OrganDescripcion,' _CUP') as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM  ScoListaPrecioProducto INNER JOIN
              TEORGANISMO ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
		WHERE (ScoListaPrecioProducto.LPrecioTipo = 2) and (ScoListaPrecioProducto.LPrecioCUP <> 0)

        UNION ALL
        
        SELECT DISTINCT 
        CONCAT(CAST(ScoListaPrecioProducto.LPrecioOrganismoCodigo  AS VARCHAR),' - ',TEORGANISMO.OrganDescripcion,' _USD') as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM  ScoListaPrecioProducto INNER JOIN
              TEORGANISMO ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
		WHERE (ScoListaPrecioProducto.LPrecioTipo = 2) and (ScoListaPrecioProducto.LPrecioMLC <> 0)

        UNION ALL
        
        SELECT DISTINCT 
        REPLACE(CONCAT(CAST(LPrecioTipificacionCodigo AS VARCHAR), ' - ', SCOTIPIfEMPRESA.TipifiDescripcion,' _CUP'), ' ', '') as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM ScoListaPrecioProducto INNER JOIN
		SCOTIPIfEMPRESA ON ScoListaPrecioProducto.LPrecioTipificacionCodigo = SCOTIPIfEMPRESA.TipifiCodigo
		WHERE (ScoListaPrecioProducto.LPrecioTipo = 3)and (ScoListaPrecioProducto.LPrecioCUP <> 0)
        
        UNION ALL
        
        SELECT DISTINCT 
        REPLACE(CONCAT(CAST(LPrecioTipificacionCodigo AS VARCHAR), ' - ', SCOTIPIfEMPRESA.TipifiDescripcion,' _CUP'), ' ', '') as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM ScoListaPrecioProducto INNER JOIN
		SCOTIPIfEMPRESA ON ScoListaPrecioProducto.LPrecioTipificacionCodigo = SCOTIPIfEMPRESA.TipifiCodigo
		WHERE (ScoListaPrecioProducto.LPrecioTipo = 3)and (ScoListaPrecioProducto.LPrecioMLC <> 0)
        
        
        UNION ALL
        
        SELECT DISTINCT 
        CONCAT(ScoListaPrecioProducto.LPrecioTipificacionCodigo, ' - ', 
        ScoListaPrecioProducto.LPrecioOrganismoCodigo, '  ', 
        TEORGANISMO.OrganDescripcion, ' _CUP') AS price_list_name,
		'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM ScoListaPrecioProducto 
        INNER JOIN TEORGANISMO ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        WHERE (ScoListaPrecioProducto.LPrecioTipo = 4) and (ScoListaPrecioProducto.LPrecioCUP <> 0)
        
        UNION ALL
        
        SELECT DISTINCT 
        CONCAT(ScoListaPrecioProducto.LPrecioTipificacionCodigo, ' - ', 
        ScoListaPrecioProducto.LPrecioOrganismoCodigo, '  ', 
        TEORGANISMO.OrganDescripcion, ' _USD') AS price_list_name,
		'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM ScoListaPrecioProducto 
        INNER JOIN TEORGANISMO ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        WHERE (ScoListaPrecioProducto.LPrecioTipo = 4) and (ScoListaPrecioProducto.LPrecioMLC <> 0)
        
        
        UNION ALL
        
        SELECT  DISTINCT
        CONCAT(SMGCLIENTEPROVEEDOR.CliCodigo,' - ',SMGCLIENTEPROVEEDOR.CliDescripcion,' Servicios_CUP') as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SMGCLIENTEPROVEEDOR INNER JOIN
        SCOServicioListaPrecios ON SMGCLIENTEPROVEEDOR.CliCodigo = SCOServicioListaPrecios.SVPrecioClienteCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 1) AND (SCOServicioListaPrecios.SVPrecioCUP <> 0)
        
        UNION ALL
        
        SELECT  DISTINCT
        CONCAT(SMGCLIENTEPROVEEDOR.CliCodigo,' - ',SMGCLIENTEPROVEEDOR.CliDescripcion,' Servicios_USD') as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SMGCLIENTEPROVEEDOR INNER JOIN
        SCOServicioListaPrecios ON SMGCLIENTEPROVEEDOR.CliCodigo = SCOServicioListaPrecios.SVPrecioClienteCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 1) AND (SCOServicioListaPrecios.SVPrecioMLC <> 0)
        
        UNION ALL
        
        SELECT DISTINCT
        CONCAT(SCOServicioListaPrecios.SVPrecioOrganismoCodigo,' - ',TEORGANISMO.OrganDescripcion,' Servicios_CUP') as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SCOServicioListaPrecios INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 2) AND (SCOServicioListaPrecios.SVPrecioCUP <> 0)
        
        UNION ALL
        
        SELECT DISTINCT
        CONCAT(SCOServicioListaPrecios.SVPrecioOrganismoCodigo,' - ',TEORGANISMO.OrganDescripcion,' Servicios_USD') as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SCOServicioListaPrecios INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 2) AND (SCOServicioListaPrecios.SVPrecioMLC <> 0)
                
        UNION ALL
        
        SELECT DISTINCT 
        CONCAT(SCOServicioListaPrecios.SVPrecioTipificacionCodigo,' - ',SCOTIPIFEMPRESA.TipifiDescripcion,' Servicios_CUP') as price_list_name,
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 3) AND (SCOServicioListaPrecios.SVPrecioCUP <> 0)
        
        UNION ALL
        
        SELECT DISTINCT 
        CONCAT(SCOServicioListaPrecios.SVPrecioTipificacionCodigo,' - ',SCOTIPIFEMPRESA.TipifiDescripcion,' Servicios_USD') as price_list_name,
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 3) AND (SCOServicioListaPrecios.SVPrecioMLC <> 0)        
                
        UNION ALL
        
        SELECT DISTINCT 
        CONCAT(SCOServicioListaPrecios.SVPrecioTipificacionCodigo, ' - ', 
        SCOServicioListaPrecios.SVPrecioOrganismoCodigo, '  ', 
        TEORGANISMO.OrganDescripcion, ' _CUP') AS price_list_name,
        
        'CUP' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 4) AND (SCOServicioListaPrecios.SVPrecioCUP <> 0)       
        
        UNION ALL
        
        SELECT DISTINCT 
        CONCAT(SCOServicioListaPrecios.SVPrecioTipificacionCodigo, ' - ', 
        SCOServicioListaPrecios.SVPrecioOrganismoCodigo, '  ', 
        TEORGANISMO.OrganDescripcion, ' _USD') AS price_list_name,
        
        'USD' as currency,
        '1' as enabled,
        '0' as buying,
        '1' as selling
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 4) AND (SCOServicioListaPrecios.SVPrecioMLC <> 0)
        ORDER BY price_list_name
        
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


# función que retorna los items que corresponden a las diferentes listas de precios que pueden estar presentes en SISCONT
def get_precio_productos(db,export=False):
    doctype_name = "Item Price"
    sqlserver_name = "Item Price"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (Item Price)
        ("item_code", ("ProduCodigo", 'string')),  # Código del items
        ("price_list", ('price_list_name', 'string')),  # nombre de la lista de precios
        ("price_list_rate", ('LPrecioMLC', 'string')),  # valor de precio del item
        ("customer", ("", 'string')),  # cliente
        ("supplier", ("", 'string')),  # proveedor
        ("buying", (0, 'boolean')),  # de tipo compras
        ("selling", (1, 'boolean')),  # de tipo ventas
        ("currency", ("CUP", 'string'))  # moneda

    ]

    # consulta que retorna todos los items en cada lista de precio antes definida
    query = f"""
        SELECT
            ScoListaPrecioProducto.ProduCodigo as item_code,
            CONCAT(SMGCLIENTEPROVEEDOR.CliCodigo,' - ',
            SMGCLIENTEPROVEEDOR.CliDescripcion,' _CUP') as price_list,        
            CAST(ScoListaPrecioProducto.LPrecioCUP AS DECIMAL(18,6)) as price_list_rate, 
            CAST(SMGCLIENTEPROVEEDOR.CliDescripcion AS VARCHAR(50)) as customer,
            CAST('' AS VARCHAR(50)) as supplier,
            CAST(0 AS bit) as buying,
            CAST(1 AS bit) as selling,
            CAST('CUP' AS VARCHAR(10)) as currency
            
            FROM ScoListaPrecioProducto 
            INNER JOIN SMGCLIENTEPROVEEDOR 
            ON ScoListaPrecioProducto.LPrecioClienteCodigo = SMGCLIENTEPROVEEDOR.CliCodigo
            INNER JOIN SIVEXISTENCIAMOVIMIENTO
            ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (ScoListaPrecioProducto.LPrecioTipo = 1) AND (ScoListaPrecioProducto.LPrecioCUP <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0) 

        UNION ALL
        
        SELECT
            ScoListaPrecioProducto.ProduCodigo as item_code,
            CONCAT(SMGCLIENTEPROVEEDOR.CliCodigo,' - ',
            SMGCLIENTEPROVEEDOR.CliDescripcion,' _USD') as price_list,        
            CAST(ScoListaPrecioProducto.LPrecioMLC AS DECIMAL(18,6)) as price_list_rate, 
            CAST(SMGCLIENTEPROVEEDOR.CliDescripcion AS VARCHAR(50)) as customer,
            CAST('' AS VARCHAR(50)) as supplier,
            CAST(0 AS bit) as buying,
            CAST(1 AS bit) as selling,
            CAST('USD' AS VARCHAR(10)) as currency
            
            FROM ScoListaPrecioProducto 
            INNER JOIN SMGCLIENTEPROVEEDOR 
            ON ScoListaPrecioProducto.LPrecioClienteCodigo = SMGCLIENTEPROVEEDOR.CliCodigo
            INNER JOIN SIVEXISTENCIAMOVIMIENTO
            ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (ScoListaPrecioProducto.LPrecioTipo = 1) AND (ScoListaPrecioProducto.LPrecioMLC <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)

        UNION ALL
        
        SELECT
            SIVNOMPROD.ProduCodigo as item_code,
            'Precio de Ventas_CUP' as price_list,
            CAST(SIVNOMPROD.ProduPrecioVentMN AS DECIMAL(18,6)) as price_list_rate,            
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'CUP' as currency
        
            FROM  SIVNOMPROD INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON SIVNOMPROD.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (SIVNOMPROD.ProduDesactiva = '') AND (SIVNOMPROD.ProduPrecioVentMN <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
            
        UNION ALL
        
        SELECT
            SIVNOMPROD.ProduCodigo as item_code,
            'Precio de Ventas_USD' as price_list,
            CAST(SIVNOMPROD.ProduPrecioVentMLC AS DECIMAL(18,6)) as price_list_rate,            
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'USD' as currency
        
            FROM  SIVNOMPROD INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON SIVNOMPROD.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (SIVNOMPROD.ProduDesactiva = '') AND (SIVNOMPROD.ProduPrecioVentMLC <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
        
        UNION ALL
        
        SELECT
            SIVNOMPROD.ProduCodigo as item_code,
            'Precio de Ventas por Ficha de costo_CUP' as price_list,
            CAST(SIVNOMPROD.ProduPrecioFCMN AS DECIMAL(18,6)) as price_list_rate,            
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'CUP' as currency
          
            FROM  SIVNOMPROD INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON SIVNOMPROD.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (SIVNOMPROD.ProduPrecioFCMN <> 0) AND (SIVNOMPROD.ProduDesactiva = '') AND (ProduFC = 1) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
        
        UNION ALL
        
        SELECT
            SIVNOMPROD.ProduCodigo as item_code,
            'Precio de Ventas por Ficha de costo_USD' as price_list,
            CAST(SIVNOMPROD.ProduPrecioFCMLC AS DECIMAL(18,6)) as price_list_rate,            
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'USD' as currency
          
            FROM  SIVNOMPROD INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON SIVNOMPROD.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (SIVNOMPROD.ProduPrecioFCMLC <> 0) AND (SIVNOMPROD.ProduDesactiva = '') AND (ProduFC = 1) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
        
        UNION ALL
        
        SELECT  
            ScoListaPrecioProducto.ProduCodigo as item_code,
            CONCAT(CAST(ScoListaPrecioProducto.LPrecioOrganismoCodigo  AS VARCHAR(50)),' - ',TEORGANISMO.OrganDescripcion,' _CUP') as price_list,
            CAST(ScoListaPrecioProducto.LPrecioCUP AS DECIMAL(18,6)) as price_list_rate,            
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'CUP' as currency
            
            FROM  ScoListaPrecioProducto INNER JOIN
            TEORGANISMO ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
		    WHERE (ScoListaPrecioProducto.LPrecioTipo = 2) and (ScoListaPrecioProducto.LPrecioCUP <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)

		UNION ALL

		SELECT  
            ScoListaPrecioProducto.ProduCodigo as item_code,
            CONCAT(CAST(ScoListaPrecioProducto.LPrecioOrganismoCodigo  AS VARCHAR(50)),' - ',TEORGANISMO.OrganDescripcion,' _USD') as price_list,
            CAST(ScoListaPrecioProducto.LPrecioMLC AS DECIMAL(18,6)) as price_list_rate,            
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'USD' as currency
            
            FROM  ScoListaPrecioProducto INNER JOIN
            TEORGANISMO ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
		    WHERE (ScoListaPrecioProducto.LPrecioTipo = 2) and (ScoListaPrecioProducto.LPrecioMLC <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
        
        UNION ALL
        
        SELECT  
		    ScoListaPrecioProducto.ProduCodigo as item_code,
            REPLACE(CONCAT(CAST(LPrecioTipificacionCodigo AS VARCHAR(50)), ' - ', SCOTIPIfEMPRESA.TipifiDescripcion,' _CUP'), ' ', '') as price_list,
            CAST(ScoListaPrecioProducto.LPrecioCUP AS DECIMAL(18,6)) as price_list_rate,		   
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'CUP' as currency
            
            FROM ScoListaPrecioProducto INNER JOIN
		    SCOTIPIfEMPRESA ON ScoListaPrecioProducto.LPrecioTipificacionCodigo = SCOTIPIfEMPRESA.TipifiCodigo INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
		    WHERE (ScoListaPrecioProducto.LPrecioTipo = 3)and (ScoListaPrecioProducto.LPrecioCUP <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
        
        UNION ALL
        
        SELECT  
		    ScoListaPrecioProducto.ProduCodigo as item_code,
            REPLACE(CONCAT(CAST(LPrecioTipificacionCodigo AS VARCHAR(50)), ' - ', SCOTIPIfEMPRESA.TipifiDescripcion,' _USD'), ' ', '') as price_list,
            CAST(ScoListaPrecioProducto.LPrecioMLC AS DECIMAL(18,6)) as price_list_rate,
		    
            '' as customer,
            '' as supplier,
            '0' as buying,
            '1' as selling,
            'USD' as currency
            
            FROM ScoListaPrecioProducto INNER JOIN
            SCOTIPIfEMPRESA ON ScoListaPrecioProducto.LPrecioTipificacionCodigo = SCOTIPIfEMPRESA.TipifiCodigo INNER JOIN
            SIVEXISTENCIAMOVIMIENTO ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
		    WHERE (ScoListaPrecioProducto.LPrecioTipo = 3) and (ScoListaPrecioProducto.LPrecioMLC <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
		
		UNION ALL

        SELECT  
            ScoListaPrecioProducto.ProduCodigo as item_code,
            CONCAT(ScoListaPrecioProducto.LPrecioTipificacionCodigo,' - ',
            ScoListaPrecioProducto.LPrecioOrganismoCodigo,'  ',
            TEORGANISMO.OrganDescripcion) as price_list,			
            CAST(ScoListaPrecioProducto.LPrecioCUP AS DECIMAL(18,6)) as price_list_rate, 
            CAST('' AS VARCHAR(50)) as customer,
            CAST('' AS VARCHAR(50)) as supplier,
            CAST(0 AS bit) as buying,
            CAST(1 AS bit) as selling,
            CAST('CUP' AS VARCHAR(10)) as currency
            
            FROM ScoListaPrecioProducto 
            INNER JOIN TEORGANISMO 
            ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo 
            INNER JOIN SIVNOMPROD 
            ON ScoListaPrecioProducto.ProduCodigo = SIVNOMPROD.ProduCodigo 
            INNER JOIN SMGNOMENCLADORUNIDADMEDIDA 
            ON SIVNOMPROD.UMedId = SMGNOMENCLADORUNIDADMEDIDA.UMedId 
            INNER JOIN SIVEXISTENCIAMOVIMIENTO
            ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (ScoListaPrecioProducto.LPrecioTipo = 4) and (ScoListaPrecioProducto.LPrecioCUP <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
        
        UNION ALL
        
        SELECT  
            ScoListaPrecioProducto.ProduCodigo as item_code,
            CONCAT(ScoListaPrecioProducto.LPrecioTipificacionCodigo,' - ',
            ScoListaPrecioProducto.LPrecioOrganismoCodigo,'  ',
            TEORGANISMO.OrganDescripcion) as price_list,			
            CAST(ScoListaPrecioProducto.LPrecioMLC AS DECIMAL(18,6)) as price_list_rate, 
            CAST('' AS VARCHAR(50)) as customer,
            CAST('' AS VARCHAR(50)) as supplier,
            CAST(0 AS bit) as buying,
            CAST(1 AS bit) as selling,
            CAST('USD' AS VARCHAR(10)) as currency
            
            FROM ScoListaPrecioProducto 
            INNER JOIN TEORGANISMO 
            ON ScoListaPrecioProducto.LPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo 
            INNER JOIN SIVNOMPROD 
            ON ScoListaPrecioProducto.ProduCodigo = SIVNOMPROD.ProduCodigo 
            INNER JOIN SMGNOMENCLADORUNIDADMEDIDA 
            ON SIVNOMPROD.UMedId = SMGNOMENCLADORUNIDADMEDIDA.UMedId
            INNER JOIN SIVEXISTENCIAMOVIMIENTO
            ON ScoListaPrecioProducto.ProduCodigo = SIVEXISTENCIAMOVIMIENTO.ProduCodigo
            WHERE (ScoListaPrecioProducto.LPrecioTipo = 4) and (ScoListaPrecioProducto.LPrecioMLC <> 0) AND (SIVEXISTENCIAMOVIMIENTO.ExMovCantidadFisica > 0)
            
        UNION ALL
        
        SELECT        
            CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,
            CONCAT(LTRIM(RTRIM(CONVERT(VARCHAR(50), SCOServicioListaPrecios.SVPrecioClienteCodigo))), 
            ' - ', SMGCLIENTEPROVEEDOR.CliDescripcion, ' Servicios_CUP') as price_list,
            CAST(SCOServicioListaPrecios.SVPrecioCUP AS DECIMAL(18,6)) as price_list_rate,
            CAST(SMGCLIENTEPROVEEDOR.CliDescripcion AS VARCHAR(50)) as customer,
            CAST('' AS VARCHAR(50)) as supplier,
            CAST(0 AS bit) as buying,
            CAST(1 AS bit) as selling,
            CAST('CUP' AS VARCHAR(10)) as currency
            
            FROM SCOServicioListaPrecios 
            INNER JOIN SMGCLIENTEPROVEEDOR 
            ON SCOServicioListaPrecios.SVPrecioClienteCodigo = SMGCLIENTEPROVEEDOR.CliCodigo 
            INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo

            WHERE (SCOServicioListaPrecios.SVPrecioTipo = 1) 
            AND (SCOServicioListaPrecios.SVPrecioCUP <> 0) AND (SCOSERVICIO.SVActiva = 1)
            
        UNION ALL
        
        SELECT        
            CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,
            CONCAT(LTRIM(RTRIM(CONVERT(VARCHAR(50), SCOServicioListaPrecios.SVPrecioClienteCodigo))), 
            ' - ', SMGCLIENTEPROVEEDOR.CliDescripcion, ' Servicios_USD') as price_list,
            CAST(SCOServicioListaPrecios.SVPrecioMLC AS DECIMAL(18,6)) as price_list_rate,
            CAST(SMGCLIENTEPROVEEDOR.CliDescripcion AS VARCHAR(50)) as customer,
            CAST('' AS VARCHAR(50)) as supplier,
            CAST(0 AS bit) as buying,
            CAST(1 AS bit) as selling,
            CAST('USD' AS VARCHAR(10)) as currency
            
            FROM SCOServicioListaPrecios 
            INNER JOIN SMGCLIENTEPROVEEDOR 
            ON SCOServicioListaPrecios.SVPrecioClienteCodigo = SMGCLIENTEPROVEEDOR.CliCodigo
            INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo
            WHERE (SCOServicioListaPrecios.SVPrecioTipo = 1) 
            AND (SCOServicioListaPrecios.SVPrecioMLC <> 0) AND (SCOSERVICIO.SVActiva = 1)
            
        UNION ALL
        
        SELECT        
        CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,
        CONCAT(LTRIM(RTRIM(CONVERT(VARCHAR(50), SCOServicioListaPrecios.SVPrecioTipificacionCodigo))), 
            ' - ', SCOTIPIFEMPRESA.TipifiDescripcion, ' Servicios_CUP') as price_list,        
        CAST(SCOServicioListaPrecios.SVPrecioCUP AS DECIMAL(18,6)) as price_list_rate,
        CAST('' AS VARCHAR(50)) as customer,
        CAST('' AS VARCHAR(50)) as supplier,
        CAST(0 AS bit) as buying,
        CAST(1 AS bit) as selling,
        CAST('CUP' AS VARCHAR(10)) as currency
        
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo
        INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 2) AND (SCOServicioListaPrecios.SVPrecioCUP <> 0) AND (SCOSERVICIO.SVActiva = 1)
        
        UNION ALL
        
        SELECT        
        CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,
        CONCAT(LTRIM(RTRIM(CONVERT(VARCHAR(50), SCOServicioListaPrecios.SVPrecioTipificacionCodigo))), 
            ' - ', SCOTIPIFEMPRESA.TipifiDescripcion, ' Servicios_USD') as price_list,        
        CAST(SCOServicioListaPrecios.SVPrecioMLC AS DECIMAL(18,6)) as price_list_rate,
        CAST('' AS VARCHAR(50)) as customer,
        CAST('' AS VARCHAR(50)) as supplier,
        CAST(0 AS bit) as buying,
        CAST(1 AS bit) as selling,
        CAST('USD' AS VARCHAR(10)) as currency
        
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo
        INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 2) AND (SCOServicioListaPrecios.SVPrecioMLC <> 0) AND (SCOSERVICIO.SVActiva = 1)
        
        UNION ALL
        
        SELECT
        CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,        
        CONCAT(LTRIM(RTRIM(CONVERT(VARCHAR(50), SCOServicioListaPrecios.SVPrecioOrganismoCodigo))), 
            ' - ', TEORGANISMO.OrganDescripcion, ' Servicios_CUP') as price_list, 
        CAST(SCOServicioListaPrecios.SVPrecioCUP AS DECIMAL(18,6)) as price_list_rate,
        CAST('' AS VARCHAR(50)) as customer,
        CAST('' AS VARCHAR(50)) as supplier,
        CAST(0 AS bit) as buying,
        CAST(1 AS bit) as selling,
        CAST('CUP' AS VARCHAR(10)) as currency
        
        FROM  SCOServicioListaPrecios INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 3) AND (SCOServicioListaPrecios.SVPrecioCUP <> 0) AND (SCOSERVICIO.SVActiva = 1)
        
        UNION ALL
        
        SELECT
        CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,        
        CONCAT(LTRIM(RTRIM(CONVERT(VARCHAR(50), SCOServicioListaPrecios.SVPrecioOrganismoCodigo))), 
            ' - ', TEORGANISMO.OrganDescripcion, ' Servicios_USD') as price_list, 
        CAST(SCOServicioListaPrecios.SVPrecioMLC AS DECIMAL(18,6)) as price_list_rate,
        CAST('' AS VARCHAR(50)) as customer,
        CAST('' AS VARCHAR(50)) as supplier,
        CAST(0 AS bit) as buying,
        CAST(1 AS bit) as selling,
        CAST('USD' AS VARCHAR(10)) as currency
        
        FROM  SCOServicioListaPrecios INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 3) AND (SCOServicioListaPrecios.SVPrecioMLC <> 0) AND (SCOSERVICIO.SVActiva = 1)
        
        UNION ALL
        
        SELECT        
        CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,
        CONCAT(SCOServicioListaPrecios.SVPrecioTipificacionCodigo, ' - ', 
        SCOServicioListaPrecios.SVPrecioOrganismoCodigo, '  ', 
        TEORGANISMO.OrganDescripcion, ' _CUP') AS price_list,
        CAST(SCOServicioListaPrecios.SVPrecioCUP AS DECIMAL(18,6)) as price_list_rate, 
        CAST('' AS VARCHAR(50)) as customer,
        CAST('' AS VARCHAR(50)) as supplier,
        CAST(0 AS bit) as buying,
        CAST(1 AS bit) as selling,
        CAST('CUP' AS VARCHAR(10)) as currency        
        
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 4) AND (SCOServicioListaPrecios.SVPrecioCUP <> 0) AND (SCOSERVICIO.SVActiva = 1)
        
        UNION ALL
        
        SELECT        
        CAST(SCOServicioListaPrecios.SVCodigo AS VARCHAR(50)) as item_code,
        CONCAT(SCOServicioListaPrecios.SVPrecioTipificacionCodigo, ' - ', 
        SCOServicioListaPrecios.SVPrecioOrganismoCodigo, '  ', 
        TEORGANISMO.OrganDescripcion, ' _USD') AS price_list,
        CAST(SCOServicioListaPrecios.SVPrecioMLC AS DECIMAL(18,6)) as price_list_rate, 
        CAST('' AS VARCHAR(50)) as customer,
        CAST('' AS VARCHAR(50)) as supplier,
        CAST(0 AS bit) as buying,
        CAST(1 AS bit) as selling,
        CAST('USD' AS VARCHAR(10)) as currency        
        
        FROM SCOServicioListaPrecios INNER JOIN
        SCOTIPIFEMPRESA ON SCOServicioListaPrecios.SVPrecioTipificacionCodigo = SCOTIPIFEMPRESA.TipifiCodigo INNER JOIN
        TEORGANISMO ON SCOServicioListaPrecios.SVPrecioOrganismoCodigo = TEORGANISMO.OrganCodigo
        INNER JOIN SCOSERVICIO ON SCOServicioListaPrecios.SVCodigo = SCOSERVICIO.SVCodigo
        WHERE (SCOServicioListaPrecios.SVPrecioTipo = 4) AND (SCOServicioListaPrecios.SVPrecioMLC <> 0) AND (SCOSERVICIO.SVActiva = 1)
        
    """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
    )
