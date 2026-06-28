import datetime
import logging
from typing import Dict, List
import pprint

from utils.jsons_utils import (
    export_table_to_json,
    export_table_to_json_paginated,
    fetch_table_data,
)

from sqlalchemy import text


# Funcion para obtener los datos de SCPTrabajadores segun el query necesario
# para el JSON
# def get_trabajadores(db, export=False) -> List[Dict]:
#     doctype_name = "Employee"
#     sqlserver_name = "SCPTRABAJADORES"
#     module_name = "Setup"

#     field_mapping = [
#         ("identity_number", ("T.CPTrabConsecutivoID", "string")),
#         ("first_name", ("MAX(T.CPTrabNombre)", "string")),
#         ("last_name", ("MAX(T.CPTrabPriApellido)", "string")),
#         ("second_surname", ("MAX(T.CPTrabSegApellido)", "string")),
#         ("gender", ("MAX(T.TrabSexo)", "string")),
#         ("occupational_category", ("MAX(C.CategODescripcion)", "string")),
#         ("designation", ("MAX(CAR.CargDescripcion)", "string")),
#         ("employment_type", ("MAX(TT.TipTrabDescripcion)", "string")),
#         ("date_of_joining", ("MAX(T.TrabFechaAlta)", "string")),
#         ("contract_end_date", ("MAX(T.TrabFechaBaja)", "string")),
#         ("bank_ac_no", ("MAX(T.TrabTmagnMN)", "string")),
#         ("company_email", ("MAX(T.TrabCorreo)", "string")),
#         (
#             "accumulate_vacations",
#             (
#                 """MAX(
#                     CASE
#                         WHEN T.TrabCpAcumVac = 1 THEN 'Accumulate and Enjoy'
#                         WHEN T.TrabCpAcumVac = 2 AND T.TrabCPLiqVac = 1 THEN 'Accumulate and Don''t Enjoy'
#                         WHEN T.TrabCpAcumVac = 2 AND T.TrabCPLiqVac = 0 THEN 'Don''t Accumulate'
#                     END
#                 )""",
#                 "string",
#             ),
#         ),
#         ("department", ("MAX(Area.AreaDescrip)", "string")),
#         ("employee_number", ("MAX(T.TrabNoInterno)", "string")),
#         # ("job_position", ("MAX(CAR.CargDescripcion)", "string")),
#         (
#             "job_position",
#             (
#                 """MAX(
#                     CASE
#                         WHEN CAR.CargDescripcion IS NOT NULL AND CAR.CargDescripcion <> ''
#                         AND Area.AreaDescrip IS NOT NULL AND Area.AreaDescrip <> ''
#                         AND E.EscSDescripcion IS NOT NULL AND E.EscSDescripcion <> ''
#                         THEN CAR.CargDescripcion
#                         ELSE ''
#                     END
#                 )""",
#                 "string",
#             ),
#         ),
#         ("salary_group", ("MAX(E.EscSDescripcion)", "string")),
#         ("salary_mode", ("'Bank'", "string")),
#         (
#             "bank_name",
#             (
#                 """MAX(
#                     CASE DB.ConfigTBanco
#                         WHEN 1 THEN 'Metropolitano'
#                         WHEN 2 THEN 'BANDEC'
#                         WHEN 3 THEN 'BPA'
#                     END
#                 )""",
#                 "string",
#             ),
#         ),
#     ]

#     select_clauses = [
#         f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
#     ]

#     query = f"""
#     SELECT
#         {', '.join(select_clauses)}
#     FROM SCPTrabajadores AS T
#     LEFT JOIN SNOCARGOS AS CAR ON T.CargId = CAR.CargId
#     LEFT JOIN SNOCATEGOCUP AS C ON T.CategId = C.CategId
#     LEFT JOIN SNOTIPOTRABAJADOR AS TT ON T.TipTrabId = TT.TipTrabId
#     LEFT JOIN SRHPersonas AS P ON T.CPTrabConsecutivoID = P.SRHPersonasId
#     LEFT JOIN SRHPersonasDireccion AS PD ON P.SRHPersonasId = PD.SRHPersonasId
#     LEFT JOIN TEREPARTOS AS R ON PD.TRepartosCodigo = R.TRepartosCodigo
#     LEFT JOIN SMGAREASUBAREA AS Area ON T.AreaCodigo = Area.AreaCodigo
#     LEFT JOIN SNOESACALASAL AS E ON T.SalEscId = E.EscSId
#     LEFT JOIN SNOCONFIGURACION AS DB ON 1 = 1
#     WHERE (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
#     GROUP BY T.CPTrabConsecutivoID
#     """

#     print(query)

#     return export_table_to_json(
#         db=db,
#         doctype_name=doctype_name,
#         sqlserver_name=sqlserver_name,
#         module_name=module_name,
#         field_mapping=field_mapping,
#         table_query=query,
#         save=export,
#     )


def get_trabajadores(db, export=False) -> List[Dict]:
    doctype_name = "Employee"
    sqlserver_name = "SCPTRABAJADORES"
    module_name = "Setup"

    field_mapping = [
        ("identity_number", ("T.CPTrabConsecutivoID", "string")),
        ("first_name", ("MAX(T.CPTrabNombre)", "string")),
        ("last_name", ("MAX(T.CPTrabPriApellido)", "string")),
        ("second_surname", ("MAX(T.CPTrabSegApellido)", "string")),
        ("gender", ("MAX(T.TrabSexo)", "string")),
        ("occupational_category", ("MAX(C.CategODescripcion)", "string")),
        ("designation", ("MAX(CAR.CargDescripcion)", "string")),
        ("employment_type", ("MAX(TT.TipTrabDescripcion)", "string")),
        ("date_of_joining", ("MAX(T.TrabFechaAlta)", "string")),
        ("contract_end_date", ("MAX(T.TrabFechaBaja)", "string")),
        ("bank_ac_no", ("MAX(T.TrabTmagnMN)", "string")),
        ("company_email", ("MAX(T.TrabCorreo)", "string")),
        (
            "accumulate_vacations",
            (
                """MAX(
                    CASE
                        WHEN T.TrabCpAcumVac = 1 THEN 'Accumulate and Enjoy'
                        WHEN T.TrabCpAcumVac = 2 AND T.TrabCPLiqVac = 1 THEN 'Accumulate and Don''t Enjoy'
                        WHEN T.TrabCpAcumVac = 2 AND T.TrabCPLiqVac = 0 THEN 'Don''t Accumulate'
                    END
                )""",
                "string",
            ),
        ),
        ("department", ("MAX(Area.AreaDescrip)", "string")),
        ("employee_number", ("MAX(T.TrabNoInterno)", "string")),
        # CAMBIO 1: Job Position simplificado al nombre del cargo
        ("job_position", ("MAX(CAR.CargDescripcion)", "string")),
        # CAMBIO 2: Salary Group con lógica Sueldista vs Jornalero
        (
            "salary_group",
            (
                """MAX(
                    CASE 
                        WHEN T.TrabSistPago = 2 THEN E_Sueldista.EscSDescripcion
                        ELSE E_Jornalero.EscSDescripcion
                    END
                )""",
                "string",
            ),
        ),
        ("salary_mode", ("'Bank'", "string")),
        (
            "bank_name",
            (
                """MAX(
                    CASE DB.ConfigTBanco
                        WHEN 1 THEN 'Metropolitano'
                        WHEN 2 THEN 'BANDEC'
                        WHEN 3 THEN 'BPA'
                    END
                )""",
                "string",
            ),
        ),
    ]

    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    # CAMBIO 3: Actualización de JOINs en el query string
    query = f"""
    SELECT
        {', '.join(select_clauses)}
    FROM SCPTrabajadores AS T
    LEFT JOIN SNOCARGOS AS CAR 
        ON T.CargId = CAR.CargId 
        AND (CAR.CargDesactivado = '' OR CAR.CargDesactivado IS NULL)
    LEFT JOIN SNOCATEGOCUP AS C ON T.CategId = C.CategId
    LEFT JOIN SNOTIPOTRABAJADOR AS TT ON T.TipTrabId = TT.TipTrabId
    LEFT JOIN SRHPersonas AS P ON T.CPTrabConsecutivoID = P.SRHPersonasId
    LEFT JOIN SRHPersonasDireccion AS PD ON P.SRHPersonasId = PD.SRHPersonasId
    LEFT JOIN TEREPARTOS AS R ON PD.TRepartosCodigo = R.TRepartosCodigo
    LEFT JOIN SMGAREASUBAREA AS Area ON T.AreaCodigo = Area.AreaCodigo
    
    /* JOIN para Sueldistas */
    LEFT JOIN SNOESACALASAL AS E_Sueldista 
        ON T.SalEscId = E_Sueldista.EscSId 
        AND T.TrabSistPago = 2
        
    /* JOINS para Jornaleros */
    LEFT JOIN SNONOMENCLDETARIFAHORARIA AS NTH 
        ON T.NomTariId = NTH.NomTariId 
        AND T.TrabSistPago <> 2
    LEFT JOIN SNOESACALASAL AS E_Jornalero 
        ON NTH.EscSalNomTariID = E_Jornalero.EscSId 
        AND T.TrabSistPago <> 2
        
    LEFT JOIN SNOCONFIGURACION AS DB ON 1 = 1
    WHERE (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
    GROUP BY T.CPTrabConsecutivoID
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


# Para obtener las categorias ocupacionales y poniendo alias con el nombre
# del campo en el doctype
def get_categorias_ocupacionales(db, export=False):
    doctype_name = "Occupational Category"
    sqlserver_name = "SNOCATEGOCUP"
    module_name = "Cuba"

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("category_name", ("CategODescripcion", "string"))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
       SELECT
           {', '.join(select_clauses)}
        FROM SNOCATEGOCUP
        WHERE CategDesactivado = ' ' OR CategDesactivado IS NULL
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


# Para obtener los cargos de los trabajadores
# No le pongo field_mapping por ser un solo campo tipo texto
def get_cargos_trabajadores(db, export=False):
    doctype_name = "Designation"
    sqlserver_name = "SNOCARGOS"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("designation_name", ("CargDescripcion", "string"))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
           SELECT
               {', '.join(select_clauses)}
            FROM SNOCARGOS
            WHERE CargDesactivado  = '' OR CargDesactivado IS NULL
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


# Para obtener los tipos de trabajadores
# No field_mapping por ser solo campo tipo texto
def get_tipos_trabajadores(db, export=False):
    doctype_name = "Employment Type"
    sqlserver_name = "SNOTIPOTRABAJADOR"
    module_name = "HR"

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("employee_type_name", ("TipTrabDescripcion", "string"))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
          SELECT
                  {', '.join(select_clauses)}
            FROM SNOTIPOTRABAJADOR s
            WHERE TipTrabDesactivado  = '' OR TipTrabDesactivado IS NULL
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


# Para obtener los tipos de  retenciones
def get_tipos_retenciones(db, export=False):
    doctype_name = "Withholding Type"
    sqlserver_name = "SCPCONRETPAGAR"
    module_name = "Cuba"

    # Mapeo de campos con información adicional sobre su tipo
    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("withholding_type_name", ("CPCRetDescripcion", "string")),
        ("debt_to", ("CRetDeudaCon", "integer")),
        ("salary_component", ("CPCRetDescripcion", "string")),
        ("priority", ("CRetPPrioridad", "integer")),
        ("child_support", ("CRetPPenAlimenticia", "boolean")),
        ("by_installments", ("CRetPConPlazos", "integer")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]
    query = f"""
        SELECT 
            {', '.join(select_clauses)}
        FROM SCPCONRETPAGAR s LEFT JOIN SCGCLASIFICADORDECUENTAS c ON 
        s.ClcuIDCuenta = c.ClcuIDCuenta
        WHERE CRetPDesactivado  = '' OR CRetPDesactivado IS NULL
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


# Para obtener maestro de  retenciones
def get_maestro_retenciones(db, export=False):
    doctype_name = "XXXXXX"
    sqlserver_name = "SCPMAESTRORETENCION"
    module_name = "XXXXXX"

    # Mapeo de campos con información adicional sobre su tipo
    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        (
            "employee_name",
            (
                "s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido + ' ' + "
                "s2.CPTrabSegApellido",
                "string",
            ),
        ),
        ("withholding_type", ("s.CPCRetPCodigo", "string")),
        # ("banking_record", ("", '')),
        ("debt", ("s.RetDeuda", "decimal")),
        ("term_amount", ("s.RetPlazo", "decimal")),
        ("payroll_frecuency", ("s.PeriCodigo", "integer")),
        ("fortnight", ("s.CorteCodigo", "integer")),
        ("from_date", ("s.RetFechaAlta", "date")),
        ("salary_component", ("", "")),
        ("customer", ("", "")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT
            {', '.join(select_clauses)}
        from
            SCPMAESTRORETENCION s
        left join SCPTRABAJADORES s2 on s.CPTrabConsecutivoID = 
        s2.CPTrabConsecutivoID
        where
             (s2.TrabDesactivado = '' or s2.TrabDesactivado IS NULL) AND 
             s.RetCantPlazo <= 6 
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


# Para obtener loa pensionados
def get_pensionados(db, export=False):
    doctype_name = "Customer"
    sqlserver_name = "SNOMANTPENS"
    module_name = "Selling"

    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        (
            "customer_name",
            (
                "MantPensNombre + ' ' + MantPensPriApe + ' ' + " "MantPensSegApe",
                "string",
            ),
        ),
        ("customer_primary_address", ("MantPensDir", "string")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT 
        {', '.join(select_clauses)}
        FROM SNOMANTPENS
        WHERE MantPensDesactivada  = '' OR MantPensDesactivada IS NULL
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


# Para obtener tasas de destajo
def get_tasas_destajos(db, export=False):
    doctype_name = "Piecework Rate"
    sqlserver_name = "SNONOMENCLADORTASASDESTAJO"
    module_name = "Stock"
    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("piece_rate_description", ("TasaDDescripcion", "string")),
        ("piece_rate", ("TasaDTasa", "float")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT 
            {', '.join(select_clauses)}
        FROM SNONOMENCLADORTASASDESTAJO
        WHERE TasaDesactivado  != '' OR TasaDesactivado IS NULL
    """
    print(f"doctype_name:{doctype_name}")

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
    )


# Para obtener colectivos
def get_colectivos(db, export=False):
    doctype_name = "Employee Group"
    sqlserver_name = "SNONOMENCLADORCOLECTIVOS"
    module_name = "Setup"

    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("employee_group_name", ("ColecDescripcion", "string")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT 
            {', '.join(select_clauses)}
        FROM SNONOMENCLADORCOLECTIVOS
        WHERE ColecDesactivado  != '' OR ColecDesactivado IS NOT NULL
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


# Para obtener departamentos
def get_departamentos(db, export=False):
    doctype_name = "Department"
    sqlserver_name = "SMGAREASUBAREA"
    module_name = "Setup"

    field_mapping = [
        # (alias, (sql_field, doctype_field_type))
        ("parent_department", ("parent_department", "string")),
        ("department_name", ("department_name", "string")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT
            {', '.join(select_clauses)}
        FROM (
            SELECT NULL as parent_department, s.AreaDescrip as department_name
            FROM SMGAREASUBAREA s
            WHERE s.AreaDesactivada IS NULL  OR s.AreaDesactivada = ''
            UNION
            SELECT s.AreaDescrip as parent_department, s1.sareaDescrip as department_name
            FROM SMGAREASUBAREA s
            INNER JOIN SMGAREASUBAREA1 s1 ON s.AreaCodigo = s1.AreaCodigo
            WHERE (s.AreaDesactivada IS NULL OR s.AreaDesactivada = '')
            AND (s1.sAreaDesactivada IS NULL OR s1.sAreaDesactivada = '')
        ) as combined
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


# Para submayor de vacaciones
def get_submayor_vacaciones(db, export=False, mes: int | None = None, anno: int | None = None):
    doctype_name = "Employee Opening Vacation Subledger"
    sqlserver_name = "SNOSMVACACIONES"
    module_name = "Cuba"

    # Simplificamos el mapeo ya que la subconsulta se encargará de traer 
    # exactamente la fila con el SMVacId máximo por trabajador.
    field_mapping = [
        ("initial_balance_in_amount", ("s.SMVacSaldoFinalD", "float")),
        ("initial_balance_in_days", ("s.SMVacSaldoFinalI", "float")),
        ("employee", ("s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido", "string")),
        ("opening_date", ("s.SMVacFechaModif", "string")),
    ]
    
    # Condición de mes/año basada en SMVacMesOperacion y el año de la fecha de modificación
    # Nota: Ajusta YEAR(s.SMVacFechaModif) si el año viene en otro campo específico.
    filtro_fecha = ""
    if mes is not None and anno is not None:
        filtro_fecha = f"AND s.SMVacMesOperacion = {mes} AND YEAR(s.SMVacFechaModif) = {anno}"

    # Construimos la consulta utilizando un CTE (WITH) y ROW_NUMBER() para SQL Server
    base_query_from = f"""
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY CPTrabConsecutivoID 
                       ORDER BY SMVacId DESC
                   ) as rn
            FROM SNOSMVACACIONES s
            WHERE s.SMVacDesactivado = ''
              AND s.SMVacSaldoInicialD > 0
              {filtro_fecha}
        ) s
        JOIN SCPTRABAJADORES s2
            ON s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID
        WHERE s.rn = 1 AND s2.TrabDesactivado = ''
    """
    
    print(base_query_from)

    # Como ya filtramos por el registro de mayor valor (rn = 1), 
    # ya no es necesario el GROUP BY en la consulta externa.
    order_clause = "ORDER BY s.SMVacId DESC"

    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause,
        save=export,
    )


# Para submayor de salarios no reclamados
def get_submayor_salarios_no_reclamados(db, export=False):
    doctype_name = "Opening of the Unclaimed Salary Subledger"
    sqlserver_name = "SNOSMREINTEGRONR"
    module_name = "Cuba"

    field_mapping = [
        (
            "employee",
            (
                "s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido + ' ' + "
                "s2.CPTrabSegApellido",
                "string",
            ),
        ),
        ("amount", ("s.SMrnrImporte", "float")),
        ("reimbursement_date", ("s.SMrnrFecha", "date")),
    ]

    base_query_from = """
        FROM SNOSMREINTEGRONR s join SCPTRABAJADORES s2 on 
        s.CPTrabConsecutivoID = s2.CPTrabConsecutivoID 
        WHERE (s.SMrnrDebito = 0 AND s.SMrnrIdenPaga IS NULL) AND 
        s2.TrabDesactivado = ''
    """

    order_clause = "ORDER BY s.SMrnrIdentificador"

    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause,
        save=export,
    )


def get_corte_sc408(db, current_year=None, export=False):
    doctype_name = "sc408 model"
    sqlserver_name = "SNOMODSC408CORTE"
    module_name = "Cuba"

    # Si no se proporciona el año actual, lo obtenemos
    if current_year is None:
        current_year = datetime.datetime.now().year

    previous_year = current_year - 1

    # Definimos el mapping sin funciones agregadas
    field_mapping = [
        (
            "employee",
            (
                "s2.CPTrabNombre + ' ' + s2.CPTrabPriApellido",
                "string",
            ),
        ),
        ("year", ("s.sccorteanoCalendario", "integer")),
        ("month", ("s.sccorteMesCalendario", "integer")),
        (
            "sc408_date",
            (
                "CONCAT(s.sccorteanoCalendario, '-', RIGHT('0' + CAST(s.sccorteMesCalendario AS VARCHAR(2)), 2), '-01')",
                "string",
            ),
        ),
        ("worked_days", ("s.sccorteSalarioTiempoDias", "float")),
        ("earned_salary", ("s.sccorteSalarioTiempoImporte", "float")),
        ("vacation_days", ("s.sccorteVacacionesDias", "float")),
        ("vacation_amount", ("s.sccorteVacacionesImporte", "float")),
        ("subsidies_days", ("s.sccorteSubsidioDias", "float")),
        ("subsidy_amount", ("s.sccorteSubsidioImporte", "float")),
        (
            "payroll_frequency",
            (
                "CASE WHEN reg.PeriCodigo = 1 THEN 'Monthly' WHEN reg.PeriCodigo = 2 THEN 'Bi-weekly' END",
                "string",
            ),
        ),
        ("total_days", ("s.sccorteTotDias", "float")),
        ("total_amount", ("s.sccorteTotImporte", "float")),
        ("period_days", ("s.sccorteDiasRealesCorte", "float")),
    ]

    # Consulta para contar el total de registros (número de filas sin agrupar)
    count_query = f"""
        SELECT COUNT(*)
        FROM SNOMODSC408CORTE s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID =
        s2.CPTrabConsecutivoID
        LEFT JOIN SNOREGIMENTRAB reg ON s2.RetraId = reg.RetraId
        WHERE (s2.TrabDesactivado = '' OR s2.TrabDesactivado IS NULL)
        AND s.sccorteanoCalendario IN ({current_year}, {previous_year})
    """

    # Consulta base SIN GROUP BY
    base_query_from = f"""
        FROM SNOMODSC408CORTE s
        JOIN SCPTRABAJADORES s2 ON s.CPTrabConsecutivoID =
        s2.CPTrabConsecutivoID
        LEFT JOIN SNOREGIMENTRAB reg ON s2.RetraId = reg.RetraId
        WHERE (s2.TrabDesactivado = '' OR s2.TrabDesactivado IS NULL)
          AND s.sccorteanoCalendario IN ({current_year}, {previous_year})
    """

    order_clause = "ORDER BY s2.CPTrabConsecutivoID"

    # Opcional: solo para imprimir, sin usarlo después
    select_clauses = [
        f"{sql_field} AS {alias}" for alias, (sql_field, _) in field_mapping
    ]
    debug_query = f"SELECT {', '.join(select_clauses)} {base_query_from} {order_clause}"
    print("Generated SQL query sc408:\n", debug_query)

    # Aquí asumimos que db es un Session o Connection de SQLAlchemy
    result = db.execute(text(count_query))
    total_items = (
        result.scalar()
    )  # o scalar_one()/scalar_one_or_none() según tu versión

    # if total_items == 0:
    if not total_items:
        logging.warning(
            f"No hay datos de Corte para los años {current_year} o " f"{previous_year}"
        )
        return []

    return export_table_to_json_paginated(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        base_query_from=base_query_from,
        order_clause=order_clause,
        save=export,
    )


# Nomenclador del Grupo Salarial
def get_grupo_salarial(db, export=False):
    doctype_name = "Salary Group"
    sqlserver_name = "SNOESACALASAL"
    module_name = "Cuba"

    # field_mapping = [
    #     ("scale_group", ("e.EscSDescripcion", "string")),
    #     ("scale_salary", ("s.SalEscSalarioEscala", "string")),
    # ]

    # Definimos las expresiones complejas para el mapeo
    # Usamos el CASE para decidir qué descripción de escala tomar
    salary_group_expr = """
        CASE 
            WHEN T.TrabSistPago = 2 THEN E_Sueldista.EscSDescripcion
            ELSE E_Jornalero.EscSDescripcion
        END
    """

    field_mapping = [
        ("scale_group", (salary_group_expr, "string")),
        ("scale_salary", ("S.SalEscSalarioEscala", "string")),
    ]

    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    # query = f"""
    #    SELECT
    #        {', '.join(select_clauses)}
    #     FROM  SNOESACALASAL e
    #     INNER JOIN SNOSALESCDAT AS s
    #     ON
    #     e.EscSId = s.EscSId
    #     WHERE
    #     (e.EscSDesactivada IS NULL OR e.EscSDesactivada = '');
    # """

    query = f"""
        SELECT DISTINCT
            {', '.join(select_clauses)}
        FROM SCPTRABAJADORES AS T
        
        -- Join para Sueldistas (Escala directa del trabajador)
        LEFT JOIN SNOESACALASAL AS E_Sueldista 
            ON T.SalEscId = E_Sueldista.EscSId 
            AND T.TrabSistPago = 2
            
        -- Joins para Jornaleros (Escala a través de Tarifa Horaria)
        LEFT JOIN SNONOMENCLDETARIFAHORARIA AS NTH 
            ON T.NomTariId = NTH.NomTariId 
            AND T.TrabSistPago <> 2
        LEFT JOIN SNOESACALASAL AS E_Jornalero 
            ON NTH.EscSalNomTariID = E_Jornalero.EscSId 
            AND T.TrabSistPago <> 2
            
        -- Unión con la tabla de montos salariales
        INNER JOIN SNOSALESCDAT AS S 
            ON S.EscSId = (
                CASE 
                    WHEN T.TrabSistPago = 2 THEN E_Sueldista.EscSId 
                    ELSE E_Jornalero.EscSId 
                END
            )
        
        WHERE 
            -- Solo trabajadores activos
            (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
            
            -- Filtro para asegurar que el trabajador tiene una escala válida asignada
            AND (
                (T.TrabSistPago = 2 AND T.SalEscId IS NOT NULL AND T.SalEscId <> 0)
                OR 
                (T.TrabSistPago <> 2 AND T.NomTariId IS NOT NULL)
            )
            
            -- Filtro para asegurar que la escala no esté desactivada
            AND (
                (T.TrabSistPago = 2 AND (E_Sueldista.EscSDesactivada IS NULL OR E_Sueldista.EscSDesactivada = ''))
                OR
                (T.TrabSistPago <> 2 AND (E_Jornalero.EscSDesactivada IS NULL OR E_Jornalero.EscSDesactivada = ''))
            )
        ORDER BY S.SalEscSalarioEscala ASC;
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


def get_puestos_trabajos(db, export=False):
    doctype_name = "Job Position"
    sqlserver_name = "PUESTOS_TRABAJO"
    module_name = "Cuba"

    field_mapping = [
        ("code", ("code", "integer")),
        ("department", ("department", "string")),
        ("salary_group", ("salary_group", "string")),
        ("designation", ("designation", "string")),
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    #     query = f"""
    # WITH CombinacionesUnicas AS (
    #     SELECT DISTINCT
    #         A.AreaDescrip AS department,
    #         E.EscSDescripcion AS salary_group,
    #         C.CargDescripcion AS designation
    #     FROM SCPTRABAJADORES AS T
    #     /* Unimos las tablas para obtener las descripciones */
    #     LEFT JOIN SMGAREASUBAREA AS A
    #         ON T.AreaCodigo = A.AreaCodigo
    #     LEFT JOIN SNOESACALASAL AS E
    #         ON T.SalEscId = E.EscSId
    #     LEFT JOIN SNOCARGOS AS C
    #         ON T.CargId = C.CargId
    #     WHERE
    #          /* Condición: La escala salarial no puede ser NULL ni 0 */
    #         T.SalEscId IS NOT NULL AND T.SalEscId <> 0
    #         /* Trabajador activo */
    #         AND (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
    #         /* Cargo activo o nulo (porque usamos LEFT JOIN) */
    #         /* Condición 2: El cargo no debe estar desactivado */
    #         AND (C.CargDesactivado = '' OR C.CargDesactivado IS NULL)
    # )
    # /* Ahora seleccionamos de las combinaciones únicas y aplicamos el código */
    # SELECT
    #     ROW_NUMBER() OVER (ORDER BY department, salary_group, designation) AS code,
    #     department,
    #     salary_group,
    #     designation
    # FROM CombinacionesUnicas;
    #     """

    query = """
    WITH CombinacionesUnicas AS (
    SELECT DISTINCT
        A.AreaDescrip AS department,
        -- Si es sueldista (TrabSistPago = 2), usa la escala del trabajador
        -- Si es jornalero, usa la escala a través de la tarifa horaria
        CASE 
            WHEN T.TrabSistPago = 2 THEN E.EscSDescripcion
            ELSE E_Jornalero.EscSDescripcion
        END AS salary_group,
        C.CargDescripcion AS designation
    FROM SCPTRABAJADORES AS T

    LEFT JOIN SMGAREASUBAREA AS A
        ON T.AreaCodigo = A.AreaCodigo

    /* JOIN para Sueldistas: escala salarial directa del trabajador */
    LEFT JOIN SNOESACALASAL AS E
        ON T.SalEscId = E.EscSId
        AND T.TrabSistPago = 2

    /* JOIN para Jornaleros: escala salarial a través de tarifa horaria */
    LEFT JOIN SNONOMENCLDETARIFAHORARIA AS NTH
        ON T.NomTariId = NTH.NomTariId
        AND T.TrabSistPago <> 2

    LEFT JOIN SNOESACALASAL AS E_Jornalero
        ON NTH.EscSalNomTariID = E_Jornalero.EscSId
        AND T.TrabSistPago <> 2

    LEFT JOIN SNOCARGOS AS C
        ON T.CargId = C.CargId

    WHERE
        /* Condición de escala según tipo de pago */
        (
            -- Sueldista: escala directa no nula
            (T.TrabSistPago = 2 AND T.SalEscId IS NOT NULL AND T.SalEscId <> 0)
            OR
            -- Jornalero: debe tener tarifa horaria asignada
            (T.TrabSistPago <> 2 AND T.NomTariId IS NOT NULL)
        )
        /* Trabajador activo */
        AND (T.TrabDesactivado = '' OR T.TrabDesactivado IS NULL)
        /* Cargo activo */
        AND (C.CargDesactivado = '' OR C.CargDesactivado IS NULL)
)

SELECT
    ROW_NUMBER() OVER (ORDER BY department, salary_group, designation) AS code,
    department,
    salary_group,
    designation
FROM CombinacionesUnicas;
    """

    print(f"Generated SQL query:\n{query}")

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query,
        save=export,
    )


# def get_configuracion_contribuciones_impuestos(db):
#     doctype_name = "Contribution and Taxes Settings"
#     sqlserver_name = "SNOContImpuestos"
#     module_name = "Cuba"

#     query = """
#         SELECT
#             c.ContImpId,
#             c.ContImpDescripcion AS name1,
#             CASE
#                 WHEN c.ContImpTipo = 'C' THEN 'Contribution'
#                 ELSE 'Tax'
#             END AS type,
#             l.ContImpaPartir1 AS from_amount,
#             l.ContImpHasta AS to_amount,
#             l.ContImpPorciento1 AS porciento
#         FROM SNOContImpuestos c
#         LEFT JOIN SNOContImpuestosLevel1 l
#             ON c.ContImpId = l.ContImpId
#         WHERE
#             c.ContImpDesactivada IS NULL
#             OR c.ContImpDesactivada = ''
#         ORDER BY c.ContImpId, l.ContImpaPartir1
#     """

#     print(query)

#     # field_mapping correcto
#     field_mapping = [
#         ("name1", ("name1", "string")),
#         ("type", ("type", "string")),
#         ("from_amount", ("from_amount", "float")),
#         ("to_amount", ("to_amount", "float")),
#         ("porciento", ("percent", "float")),
#     ]

#     # Ejecutar la query usando fetch_table_data
#     rows = fetch_table_data(db, field_mapping, query)

#     # print(">>> Rows recibidas:", len(rows))
#     # if rows:
#     #     print(">>> Primera fila:", rows[0])

#     data = _format_contribuciones_impuestos(rows)
#     # print(">>> DATA FINAL:")
#     # print(json.dumps(data, indent=4, ensure_ascii=False))

#     save_json_file(
#         doctype_name=doctype_name,
#         data=data,
#         module_name=module_name,
#         sqlserver_name=sqlserver_name,
#     )

#     # Devuelve directamente lo que espera la UI
#     return {
#         "doctype": doctype_name,
#         "data": data,
#     }


# def _format_contribuciones_impuestos(rows: list) -> list:
#     impuestos = {}

#     for row in rows:
#         key = row["name1"]

#         if key not in impuestos:
#             impuestos[key] = {"name1": row["name1"], "type": row["type"], "ranges": []}

#         if row["from_amount"] is not None:
#             impuestos[key]["ranges"].append(
#                 {
#                     "from_amount": float(row["from_amount"] or 0),
#                     "to_amount": float(row["to_amount"] or 0),
#                     "percent": float(row["porciento"] or 0),
#                 }
#             )

#     return list(impuestos.values())


def get_configuracion_contribuciones_impuestos(
    db, export: bool = False, grouped: bool = False
):
    doctype_name = "Contributions and Taxes Setting"
    sqlserver_name = "SNOContImpuestos"
    module_name = "Cuba"

    field_mapping = [
        ("name1", ("c.ContImpDescripcion", "string")),
        (
            "type",
            (
                "CASE WHEN c.ContImpTipo = 'I' THEN 'Tax' WHEN c.ContImpTipo = 'C' THEN 'Contribution' END",
                "string",
            ),
        ),
        ("from_amount", ("l.ContImpaPartir1", "float")),
        ("to_amount", ("l.ContImpHasta", "integer")),
        ("porciento", ("l.ContImpPorciento1", "float")),
    ]

    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT DISTINCT
            {', '.join(select_clauses)}
        FROM SNOContImpuestos c
        LEFT JOIN SNOContImpuestosLevel1 l
            ON c.ContImpId = l.ContImpId
            AND (
                l.ContImpDesactivada1 = '' OR l.ContImpDesactivada1 IS NULL
            )
        WHERE
            c.ContImpDesactivada = '' OR c.ContImpDesactivada IS NULL
    """
    print(query)

    try:
        # 1) Extrayendo los datos planos
        rows = fetch_table_data(db, field_mapping, query)
        # print("Imprimiendo rows")
        # pprint.pprint(rows[:5])

        # if export:
        if grouped:
            # 2) Transformar a formato padre-hijo
            contribuciones_impuestos = transform_contribuciones_impuestos(rows)
            # print("imprimiendo contribuciones e impuestos")
            # pprint.pprint(contribuciones_impuestos)

            return contribuciones_impuestos

        else:
            return rows

    except Exception as e:
        logging.error(f"Error exportando {doctype_name}: {e}")
        raise


def transform_contribuciones_impuestos(rows: list) -> list:
    contribuciones = {}

    for row in rows:
        key = row["name1"].strip()

        # Si aún no existe el nombre, lo inicializamos
        if key not in contribuciones:
            contribuciones[key] = {
                "name1": key,
                "type": row["type"],
                "ranges": [],
            }

        # Solo agregamos rango si existe from_amount
        if row.get("from_amount") is not None:
            rango = {
                "from_amount": row["from_amount"],
                "to_amount": row["to_amount"],
                "percent": row["porciento"],
            }

            # Evitar duplicados
            if rango not in contribuciones[key]["ranges"]:
                contribuciones[key]["ranges"].append(rango)

    # Ordenar rangos por from_amount para cada contribución
    for key in contribuciones:
        contribuciones[key]["ranges"].sort(key=lambda x: x["from_amount"])

    # Devolver como lista de contribuciones
    return list(contribuciones.values())


def get_asignacion_contribuciones_impuestos(
    db, export: bool = False, grouped: bool = False
):
    doctype_name = "Allocation of Contributions and Taxes"
    sqlserver_name = "SNOContImpuestosLevel1"
    module_name = "Cuba"

    field_mapping = [
        ("naming_series", ("'HR-CAL-.YYYY.-'", "string")),
        (
            "employee",
            (
                "t.CPTrabNombre + ' ' + t.CPTrabPriApellido",
                "string",
            ),
        ),
        ("name1", ("i.ContImpDescripcion", "string")),
        (
            "type",
            (
                "CASE WHEN i.ContImpTipo = 'I' THEN 'Tax' "
                "WHEN i.ContImpTipo = 'C' THEN 'Contribution' END",
                "string",
            ),
        ),
        # ("from_amount", ("l1.ContImpaPartir1", "float")),
        # ("to_amount", ("CAST(l1.ContImpHasta AS INT)", "integer")),
        # ("porciento", ("l1.ContImpPorciento1", "float")),
    ]

    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
        SELECT
            {', '.join(select_clauses)}
        FROM SCPTRABAJADORES t
        INNER JOIN SCPTRABAJADORES4 t4
            ON t.CPTrabConsecutivoID = t4.CPTrabConsecutivoID
        INNER JOIN SNOContImpuestos i
            ON t4.ContImpId = i.ContImpId
        LEFT JOIN SNOContImpuestosLevel1 l1
            ON i.ContImpId = l1.ContImpId
            AND (l1.ContImpDesactivada1 = '' OR l1.ContImpDesactivada1 IS NULL)
        WHERE
            t.TrabDesactivado = '' OR t.TrabDesactivado IS NULL
        ORDER BY employee
    """

    rows = fetch_table_data(db, field_mapping, query)
    print("Imprimiendo rows")
    pprint.pprint(rows[:5])

    # if export:
    if grouped:
        asignacion_contribuciones = transform_asignacion(rows)
        print("imprimiendo contribuciones e impuestos")
        pprint.pprint(asignacion_contribuciones)
        return asignacion_contribuciones
    else:
        return rows


def transform_asignacion(rows: list) -> list:
    empleados = {}

    for row in rows:
        emp = row["employee"].strip()
        impuesto = row["name1"].strip()

        if emp not in empleados:
            empleados[emp] = {
                "naming_series": row["naming_series"],
                "employee": emp,
                "allocations": {},
            }

        # Solo guardamos la información del impuesto sin rangos
        if impuesto not in empleados[emp]["allocations"]:
            empleados[emp]["allocations"][impuesto] = {
                "contributions": impuesto,
                "type": row["type"],
            }

    # convertir allocations de dict → lista
    resultado = []
    for emp in empleados.values():
        emp["allocations"] = list(emp["allocations"].values())
        resultado.append(emp)

    return resultado


# def transform_asignacion(rows: list) -> list:
#     empleados = {}

#     for row in rows:
#         emp = row["employee"].strip()
#         impuesto = row["name1"].strip()

#         if emp not in empleados:
#             empleados[emp] = {
#                 "naming_series": row["naming_series"],
#                 "employee": emp,
#                 "allocations": {},
#             }

#         if impuesto not in empleados[emp]["allocations"]:
#             empleados[emp]["allocations"][impuesto] = {
#                 "name1": impuesto,
#                 "type": row["type"],
#                 "ranges": [],
#             }

#         rango = {
#             "from_amount": row["from_amount"],
#             "to_amount": row["to_amount"],
#             "porciento": row["porciento"],
#         }

#         if rango not in empleados[emp]["allocations"][impuesto]["ranges"]:
#             empleados[emp]["allocations"][impuesto]["ranges"].append(rango)

#     # ordenar rangos
#     for emp in empleados.values():
#         for imp in emp["allocations"].values():
#             imp["ranges"].sort(key=lambda x: x["from_amount"])

#     # convertir allocations de dict → lista
#     resultado = []
#     for emp in empleados.values():
#         emp["allocations"] = list(emp["allocations"].values())
#         resultado.append(emp)

#     return resultado
