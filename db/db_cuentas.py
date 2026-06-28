from typing import List, Dict

# from db.database import DatabaseManager
from db.db_connection import runSQLQuery, createJSON
from db.db_connection import Connection
# Importo la clase StreamingResponse para implementar la descarga del fichero JSON
from fastapi.responses import StreamingResponse
from collections import OrderedDict
from sqlalchemy.engine import Engine

#Importo el modulo json
import os
import logging
import pandas as pd


def getAccounts(conn:Connection, name:str):
        """
        Este metodo retorna las cuentas basadas en el Clasificador de Cuentas
        """

        #Esta query obtiene las cuantas del clasificador de cuentas y la combina con las tablas del tipo de grupo y subgrupo
        queryClas = f"""SELECT [ClCuCuenta] AS ID, [ClCuDescripcion] AS account_name,
                              CASE
                                WHEN [ClCuUltimoNivel] = 1 THEN 0 ELSE 1
                              END AS is_group,
                              [ClCuSubElemento] AS expense_element_num,
                              CAST([ClCuCuenta] AS varchar) AS cuentaId,
                              CAST([ClCuSubCuenta] AS varchar) AS subcuentaId,
                              [ClCuSubControl] AS subcontrol,
                              [ClCuAnalisis] AS analisis,
                              [ClCuDeudora] AS nature,
							  [ParamCostConcepto] AS cost_concepto
                              FROM [{name}].[dbo].[SCGCLASIFICADORDECUENTAS]
							  LEFT JOIN [{name}].[dbo].[SCCPARAMETROSCOSTO] 
							  ON [SCGCLASIFICADORDECUENTAS].ClcuIDCuenta = [SCCPARAMETROSCOSTO].ClcuIDCuenta
							  WHERE ClCuActiva = 0
                              ORDER BY [ClCuCuenta], [ClCuSubcuenta], [ClCuSubControl], [ClCuAnalisis]"""

        # Esta query obtiene los nomencladores de moneda de cada cuenta.
        queryMon = f"""SELECT CAST([NomCuCuenta] AS varchar)  AS cuentaId,
                             CAST([NomCuSubCuenta] AS varchar) AS subcuentaId,
                             [MonSiglas] as currency
                        FROM [{name}].[dbo].[SCGCTASNOMENCCTAS] AS NOMENCTAS
                        RIGHT JOIN [{name}].[dbo].[SMGNOMMONEDAS] AS NOMMONEDAS ON NOMENCTAS.NomCuSubControl = CAST(NOMMONEDAS.MonCodigo AS varchar)
                    """
        queryInv = f""" SELECT CAST(Cuentas.ClCuCuenta AS varchar) AS cuentaId,
                              CAST(Cuentas.ClCuSubCuenta AS varchar) AS subcuentaId,
                              Cuentas.ClCuSubControl AS subcontrol,
                              Cuentas.ClCuAnalisis AS analisis   
                        FROM [{name}].[dbo].[SCGCLASIFICADORDECUENTAS] AS Cuentas INNER JOIN [{name}].[dbo].[SIVCTASCONFIG] AS Config ON Cuentas.ClcuIDCuenta=Config.ClcuIDCuenta
                        WHERE Config.CtaCGInvActiva = ''"""

        #Creo el DataFrame para obtener la tabla con el clasificador de cuentas
        df = runSQLQuery(queryClas, conn)        
        #Creo el DataFrame con las nominaciones de todas las cuentas
        dfMon = runSQLQuery(queryMon, conn)
       
        #Ajusto la tabla del clasificador de cuentas
        #Aplico la conversion en el campo expense element; si es 0 se queda en 0; pero si es 2 o 3 se convierte en 1
        df["cost_concepto"] = [int(row["cost_concepto"]) in [1, 2, 3, 4, 10, 11, 12] if not pd.isna(row["cost_concepto"]) else "" for i, row in df.iterrows()]
        
        df.insert(1, "expense_element", '')
        df["expense_element"] = [int(row["expense_element_num"])==2 or int(row["expense_element_num"])==3 for i, row in df.iterrows()]
        df["expense_element"] = [row["cost_concepto"] if int(row["subcuentaId"])==0 and int(row["subcontrol"])==0 and int(row["analisis"])==0 else row["expense_element"] for i, row in df.iterrows()] #

        df = df.replace({'expense_element':{True:1, False:0}})

        df.insert(2, "expense_subelement", "")
        df["expense_subelement"] = [row["subcontrol"] if int(row["expense_element_num"])==3 else row["subcuentaId"] if int(row["expense_element_num"])==2 else "" for i, row in df.iterrows()]
        #Ajusto la tabla de las monedas
        #Las cuentas que estan en CUC pasan hacer en CUP
        dfMon = dfMon.replace({'currency':{'CUC':'CUP'}})
        #Elimino de las tabla las cuentas que no tienen monedas porque son padres
        dfMon = dfMon[dfMon['cuentaId'].notna()]
        #Elimino las filas duplicadas generadas durante la conversion
        dfMon.drop_duplicates(inplace= True)

        #Cargo la tabla con las cuentas de tipo inventario
        dfInv = runSQLQuery(queryInv, conn)
        listInv = [f'{row['cuentaId']}{row['subcuentaId'] if int(row['subcuentaId'])!=0 else ""}{row["subcontrol"] if int(row["subcontrol"])!=0 else ""}{row["analisis"] if int(row["analisis"])!=0 else ""}' for i, row in dfInv.iterrows()]

        #Merge sobre ambas tablas
        df = dfMon.merge(df, on=['cuentaId', 'subcuentaId'], how='right')

        df.insert(1,"account_number","")
        df["account_number"] = [f'{row['cuentaId']}{row['subcuentaId'] if int(row['subcuentaId'])!=0 else ""}{row["subcontrol"] if int(row["subcontrol"])!=0 else ""}{row["analisis"] if int(row["analisis"])!=0 else ""}' for i, row in df.iterrows()]

        #Inserto el tipo de cuenta de cada cuenta segun el excel cuentas
        dfType = pd.read_excel(os.path.join(os.getcwd(), "db/cuentas.xlsx"))

        dfType["Rangos"] = dfType["Rangos"].astype(str)

        dictType = {tuple(str(row["Rangos"]).split('-')): row["Tipo"] for i, row in dfType.iterrows()}

        df.insert(1,'account_nature', '')
        df["account_nature"] = ["Creditor" if int(row["nature"]) == 0 else "Debtor" for i, row in df.iterrows()]

        df.insert(1,'account_type','')
        emptyType= ["Current Asset", "Current Liability", "Direct Expense", "Indirect Expense"]
        for i in range(0, len(df)):
               codigo = int(df.at[i,"cuentaId"])
               for key, value in dictType.items():                    
                    if len(key)>1: 
                        if codigo >= int(key[0]) and codigo < int(key[1]):
                            #Si la cuenta es memorandum y se encuentra entre las cuentas de inventario activas se pone como tipo Stock
                            if int(key[0]) == 1 and int(key[1])==99 and df.at[i, "account_number"] in listInv:
                                df.at[i,'account_type']="Stock"
                            else: #De lo contrario se considera como los casos generales
                                df.at[i,'account_type'] = "" if str(value) in emptyType and df.at[i,'is_group'] == 1 else str(value)
                            break
                    else:
                         if int(key[0]) == codigo:
                            df.at[i,'account_type'] =  "" if str(value) in emptyType and df.at[i,'is_group'] == 1 else str(value)
                            break                      
        
        df.drop(["ID", "expense_element_num", "nature", "cost_concepto"], axis=1, inplace=True)#

        #Creo el JSON
        result = OrderedDict()
        result["doctype"] = "Account"
        for col in [coln for coln in df.columns]:
            df[col] = df[col].astype(str)
        result["data"] =  df.to_dict(orient="records")

        return result


def getExpenseElement(conn:Connection, name:str):
        """
        Este metodo retorna los valores de la tabla SCGELEMENTODEGASTO
        """
        
        #Esta es la query para obtener los subelementos de gastos
        queryChilds = f"""SELECT [SubelCodigo] AS number
                        ,[SubelDescrip] AS title
                        ,[EGastoDescripcion] AS old_parent
                        ,[EGastoDescripcion] AS parent_expense_element
                        ,[EGastoCodigoDesde] AS lft
                        ,[EGastoCodigoHasta] AS rgt
                        FROM [{name}].[dbo].[SCGSUBELEMENTO]
                        INNER JOIN [{name}].[dbo].[SCGELEMENTODEGASTO]
                        ON SCGSUBELEMENTO.[EGastoID] = SCGELEMENTODEGASTO.[EGastoID] WHERE [SubelActivo] = ''"""
        #Obtengo el Dataframe de los elementos de gastos
        dfChilds= runSQLQuery(queryChilds, conn)
        dfChilds.insert(0,"is_group", 0)

        #Inserto el tipo de cuenta de cada cuenta segun el excel cuentas
        dfDescrip = pd.read_excel(os.path.join(os.getcwd(), "db/subelementos.xlsx"))
        dictDescrip = {(int(row["EGastoCodigoDesde"]), int(row["EGastoCodigoHasta"])): str(row["EGastoDescripcion"]) for i, row in dfDescrip.iterrows()}

        dfChilds["old_parent"] = [dictDescrip[(int(row["lft"]), int(row["rgt"]))] if (int(row["lft"]), int(row["rgt"])) in dictDescrip.keys() else "" for i,row in dfChilds.iterrows()]
        dfChilds["parent_expense_element"] = [row["old_parent"] for i,row in dfChilds.iterrows()]
                
        #Creo el diccionario para el Doctype
        result = OrderedDict()
        result["doctype"] = "Expense Element"        
        result["data"] =  dfChilds.to_dict(orient="records")
        return result


def getJournalEntry(conn: Connection, name: str):
    """
    Retorna un diccionario con la estructura JSON compatible con ERPNext para Journal Entry.
    """
    queryJentry = f"""
        SELECT SCGCLASIFICADORDECUENTAS.ClcuIDCuenta, SCGCLASIFICADORDECUENTAS.ClCuCuenta, 
               SCGCLASIFICADORDECUENTAS.ClCuSubcuenta, SCGCLASIFICADORDECUENTAS.ClCuSubControl, 
               SCGCLASIFICADORDECUENTAS.ClCuAnalisis, SCGCLASIFICADORDECUENTAS.ClCuDescripcion, 
               SCGCLASIFICADORDECUENTAS.ClCuDeudora, SCGMAYORCONTABILIDAD.MayorCAnoOperacion, 
               SCGMAYORCONTABILIDAD.MayorCSaldoAcumulado 
        FROM [{name}].[dbo].[SCGCLASIFICADORDECUENTAS] SCGCLASIFICADORDECUENTAS
        INNER JOIN [{name}].[dbo].[SCGMAYORCONTABILIDAD] SCGMAYORCONTABILIDAD 
            ON SCGCLASIFICADORDECUENTAS.ClcuIDCuenta = SCGMAYORCONTABILIDAD.ClcuIDCuenta
        WHERE SCGCLASIFICADORDECUENTAS.ClCuActiva = 0 
          AND SCGCLASIFICADORDECUENTAS.ClCuUltimoNivel = 1 
          AND SCGMAYORCONTABILIDAD.MayorCSaldoAcumulado <> 0 
          AND SCGMAYORCONTABILIDAD.MayorCAnoOperacion = 2025
        ORDER BY SCGCLASIFICADORDECUENTAS.ClCuCuenta, 
                 SCGCLASIFICADORDECUENTAS.ClCuSubcuenta, 
                 SCGCLASIFICADORDECUENTAS.ClCuSubControl, 
                 SCGCLASIFICADORDECUENTAS.ClCuAnalisis
    """

    # Ejecutar la consulta
    dfJentry = runSQLQuery(queryJentry, conn)

    # Convertir el DataFrame a una lista de diccionarios (rows)
    rows = dfJentry.to_dict(orient="records")

    # Construir la estructura ERPNext: transformamos cada row en una entry en "accounts"
    accounts = []
    for row in rows:
        # Obtener los datos de la cuenta
        cuenta = str(row["ClCuCuenta"]) if pd.notna(row["ClCuCuenta"]) else ""
        subcuenta = str(row["ClCuSubcuenta"]) if pd.notna(row["ClCuSubcuenta"]) and row["ClCuSubcuenta"] != 0 else ""
        subcontrol = str(row["ClCuSubControl"]) if pd.notna(row["ClCuSubControl"]) and row["ClCuSubControl"] != 0 else ""
        analisis = str(row["ClCuAnalisis"]) if pd.notna(row["ClCuAnalisis"]) and row["ClCuAnalisis"] != 0 else ""

        # Construir la cuenta concatenando los campos no vacíos
        componentes_cuenta = [cuenta]
        if subcuenta:
            componentes_cuenta.append(subcuenta)
        if subcontrol:
            componentes_cuenta.append(subcontrol)
        if analisis:
            componentes_cuenta.append(analisis)

        # Unir los campos llenos de la cuenta en un solo valor de tipo string
        cuenta_completa = "".join(componentes_cuenta)

        # Obtener el saldo y naturaleza de la cuenta
        saldo = row["MayorCSaldoAcumulado"]
        es_deudora = row["ClCuDeudora"]  # 1 = Deudora (débito), 0 = Acreedora (crédito)

        # Determinar si el saldo es crédito o débito basado en ClCuDeudora
        if es_deudora == 1:  # Cuenta de naturaleza deudora
            # Saldo: positivo (activo)
            debit = float(abs(saldo)) if saldo >= 0 else 0
            credit = float(abs(saldo)) if saldo < 0 else 0
        else:  # Cuenta de naturaleza acreedora
            # Saldo: negativo (pasivo)
            credit = float(abs(saldo)) if saldo <= 0 else 0
            debit = float(abs(saldo)) if saldo > 0 else 0
        #conformando la estructura de los hijos
        accounts.append({
            "account": cuenta_completa,
            "debit_in_account_currency": float(debit),
            "credit_in_account_currency": float(credit)
        })

    # Resultado final con el formato ERPNext
    result = OrderedDict()
    result["doctype"] = "Journal Entry"
    result["data"] = OrderedDict()
    result["data"]["voucher_type"] = "Opening Entry"
    result["data"]["naming_series"] = "ACC-JV-.YYYY.-"
    result["data"]["accounts"] = accounts
    result["data"]["is_opening"] = "Yes"

    return result

