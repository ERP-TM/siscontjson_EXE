from typing import List, Dict

# from db.database import DatabaseManager
from datetime import datetime
from dateutil.relativedelta import relativedelta
from db.db_connection import runSQLQuery, createJSON
from db.db_connection import Connection
from collections import OrderedDict
import logging
import pandas as pd



    
def getSAFAperturaCSV(conn: Connection, name:str, siglas:str):
        
        query=f"""SELECT aft.[NomGrupCodigo] AS codeGroup
                    ,aft.[SubGrupoCodigo] AS codeSubGroup
                    ,aft.[AFDescripcion] AS descrip
                    ,aft.[AFTasaDepreciacion] AS tasa
                    ,aft.[AFFechaAlta] AS purchase_date
                    ,aft.[AFValorMN] AS gross_purchase_account                    
                    ,aft.[AFDeprecAcumMN] AS opening_accumulated_depreciation
                    ,aft.[NivelCodigoAF] AS codLocation 
                    ,aft.[AFNumInv] AS id
                    ,aft.[AFFechaApertura]
                    ,aft.[AFFechaNoDeprecia]
                    ,aft.[AFFechaDepreTotal]
                    ,aft.[AFDeprecApertura]	     
                    ,SubGroup.[NomSubgDescripcion] AS nameSubGroup                
                    ,SubGroup.[NomSubgTipoDepreciacion] AS tipo_depresiacion
	            ,loc.NivelCodigo AS NivelCodigo
		    ,loc.NivelDescrip AS NivelDescrip
		    ,centro.OCostCodigo AS centro_code
                    ,centro.OCostDescrip AS centro_descrip
		    ,areas.AreaDescrip AS area
		    ,subareas.SareaDescrip AS subarea
		    ,item_cost.SafSubElementoCodigo AS expense_code
		    ,item_cost.title AS expense_descrip
                    FROM [{name}].[dbo].[SAFAPERTURA] AS aft 
		    INNER JOIN [{name}].[dbo].[SAFSubgruposAFT] AS SubGroup 
                    ON aft.SubGrupoCodigo = SubGroup.NomSubgCodigo AND aft.NomGrupCodigo = SubGroup.NomGrupCodigo
		    LEFT JOIN [{name}].[dbo].[SAFNIVELRESPAREASUBAREA] as loc
		    ON aft.NivelCodigoAF = loc.NivelCodigo					
		    LEFT JOIN (SELECT  elemCosto.AFAreaCodigo AS AFAreaCodigo, elemCosto.AFSareaCodigo AS AFSareaCodigo, elemCosto.OCostCodigo AS OCostCodigo, elemCosto.AFAsocActiva, nameCosto.OCostDescrip AS OCostDescrip
                                FROM [{name}].[dbo].[SAFASOCAREAOBJCTOSUBELEM] AS elemCosto
                                INNER JOIN [{name}].[dbo].[SCCOBJCOSTO] AS nameCosto
                                ON elemCosto.OCostCodigo = nameCosto.OCostCodigo) as centro
		    ON ((aft.AreaCodigo = centro.AFAreaCodigo AND aft.SareaCodigo = centro.AFSareaCodigo) OR (aft.AreaCodigo = centro.AFAreaCodigo AND aft.SareaCodigo = NULL AND centro.AFSareaCodigo = 0)) and centro.AFAsocActiva = ''					
		    LEFT JOIN [{name}].[dbo].[SMGAREASUBAREA] as areas
                    ON aft.[AreaCodigo] = areas.AreaCodigo
                    LEFT JOIN [{name}].[dbo].[SMGAREASUBAREA1] subareas
                    ON aft.[AreaCodigo] = subareas.AreaCodigo AND aft.SareaCodigo = subareas.SareaCodigo
		    LEFT JOIN (SELECT [SafNumInv],[SafSubElementoCodigo],title
                                FROM [{name}].[dbo].[SAFSUBMAYORDEPRE]
                                INNER JOIN (SELECT [SubelCodigo] AS number
                                        ,[SubelDescrip] AS title                        
                                        FROM [{name}].[dbo].[SCGSUBELEMENTO]
                                        INNER JOIN [{name}].[dbo].[SCGELEMENTODEGASTO]
                                        ON SCGSUBELEMENTO.[EGastoID] = SCGELEMENTODEGASTO.[EGastoID] WHERE [SubelActivo] = '') AS subelemnt
                                ON [SafSubElementoCodigo] = subelemnt.number
                                WHERE [SafAnoOper] = (SELECT TOP (1) [SafAnoOper] FROM [{name}].[dbo].[SAFSUBMAYORDEPRE] ORDER BY [SafAnoOper] DESC)) AS item_cost
                    ON aft.[AFNumInv] = item_cost.SafNumInv
		    WHERE aft.AFActivo = '' """

        query2 = f"""SELECT [AFNumInv] as id
                        ,[AFNumComp]
                        ,[DescripcionComp]
                        ,[CantidadComp]
                        ,[ValorMLCComp]
                        ,[ValorMNComp]
                        ,[DepAcumMNComp]
                        ,[DepAcumMLCComp]
                        ,[AFNumInvCompConversion]
                        ,[UnificadoComp]
                        ,[AFAper1CRC]
                        ,[ValorMEXComp]
                        FROM [{name}].[dbo].[SAFAPERTURA1]"""
        
        queryEntity = f"SELECT [EntidNomb] AS Company FROM [{name}].[dbo].[SMAENTIDAD]"
                
        df = runSQLQuery(query, conn)

        df1 = runSQLQuery(query2, conn)     

        dfEntity = runSQLQuery(queryEntity, conn)
        
        #Inserto el codigo del activo fijo
        df.insert(0, "Identificador", "")
        df["Identificador"] = [row['id'] for index, row in df.iterrows()] 
        
        df.insert(1, "Empresa", "")
        df["Empresa"] = [dfEntity['Company'][0] for i in range(0,len(df))] #dfEntity['Company'][0]
        
        df.insert(2, "Código de artículo", "")
        df["Código de artículo"]=[f'9999{row['codeGroup']}{row['codeSubGroup']}' for index, row in df.iterrows()]
        
        df.insert(3, "Nombre de Activo", "")
        df["Nombre de Activo"] = [row["descrip"] for index, row in df.iterrows()]
        
        df.insert(4, "Ubicación", "")
        df["Ubicación"] = [row['NivelDescrip'] for index, row in df.iterrows()]
        
        df.insert(5,"Categoría de Activos Fijos","")
        df["Categoría de Activos Fijos"] =  [f'{row['codeGroup']}{row['codeSubGroup']} {row['nameSubGroup']}' for index, row in df.iterrows()]
        
        df.insert(6,"Nombre del Producto", "")
        df["Nombre del Producto"]= [f'Apertura {row['codeGroup']}{row['codeSubGroup']}' for index, row in df.iterrows()]
        
        df.insert(7,"Total Asset Cost","")
        df["Total Asset Cost"]= [row["gross_purchase_account"] for index, row in df.iterrows()]
        
        df.insert(8,"Número total de depreciaciones", "")
        df["Número total de depreciaciones"] = [int((100/float(row["tasa"])) * 12) for index, row in df.iterrows()]
        
        df.insert(9, "Método de depreciación", "")
        df["Método de depreciación"] = ["Straight Line" if row["tipo_depresiacion"] == 1 else "Manual" for index, row in df.iterrows()]
        
        df.insert(10, "Propietario del activo", "")
        df["Propietario del activo"] = ["Company" for i in range(0,len(df))] 
        
        df.insert(11, "Compañia Dueña del Activo", "")
        df["Compañia Dueña del Activo"] = [row["Empresa"] for index, row in df.iterrows()]
       
        df.insert(12, "Es Activo Existente", "")
        df["Es Activo Existente"] = [1 for i in range(0, len(df))]

        df.insert(13, "Is Composite Asset", "")
        df["Is Composite Asset"] = [1 if row["id"] in df1["id"] else 0 for index, row in df.iterrows()]
        
        df.insert(14, "Proveedor", "")        

        df.insert(15, "Cliente", "")

        df.insert(16, "Imagen", "")

        df.insert(17, "Entrada de diario para desguace", "")

        df.insert(18, "Secuencias e identificadores", "")

        df.insert(19, "Dividido de, separado de", "") 

        df.insert(20, "Custodio", "")        
        
        df.insert(21, "Departamento", "")        
        df["Departamento"] = [f"{row["subarea"]} - {siglas}" if not row["subarea"] is None else f"{row["area"]} - {siglas}" for index, row in df.iterrows()]

        df.insert(22, "Fecha de eliminación", "")

        df.insert(23, "Centro de Costo", "")
        df["Centro de Costo"] = [f"{int(row["centro_code"])} - {row["centro_descrip"]} - {siglas}" if not row["centro_descrip"] is None else ''  for index, row in df.iterrows()]
        
        df.insert(24, "Elemento de Gastos", "")
        df["Elemento de Gastos"] = [f"{int(row["expense_code"])} - {row["expense_descrip"]}" if not row["expense_descrip"] is None else '' for index, row in df.iterrows()]
      
        df.insert(25, "Fecha disponible para usar", "") 
        df["Fecha disponible para usar"] = [datetime.strptime(str(row["purchase_date"]).split('.')[0], "%Y-%m-%d %H:%M:%S") + relativedelta(months=1) for index, row in df.iterrows()]       
        
        df.insert(26, "Additional Asset Cost", "")
        
        df.insert(27, "Net Purchase Amount", "")
        df["Net Purchase Amount"]=[row["gross_purchase_account"] for index, row in df.iterrows()]
        
        df.insert(28, "Fecha de compra", "")
        df["Fecha de compra"] = [row["purchase_date"] for index, row in df.iterrows()]
        
        df.insert(29, "Apertura de la depreciación acumulada", "")
        df["Apertura de la depreciación acumulada"] = [row["opening_accumulated_depreciation"] for index, row in df.iterrows()]
              
        # Formula con Loipa
        df.insert(30, "Opening Number of Booked Depreciations", "")
        
        df.insert(31, "Is Fully Depreciated", "")
        df["Is Fully Depreciated"] = [1 if int(row["gross_purchase_account"])==int(row["opening_accumulated_depreciation"]) else 0 for index, row in df.iterrows()]
               
        df["Opening Number of Booked Depreciations"] = [int(float(row["gross_purchase_account"])*float(row["tasa"])/12/100) if int(row["gross_purchase_account"])!=int(row["opening_accumulated_depreciation"]) else "" for index, row in df.iterrows()]
                
        df.insert(32, "Valor después de Depreciación", "")
        df["Valor después de Depreciación"] = [0 for index, row in df.iterrows()]

        df.insert(33, "Cantidad de activos fijos", "")
        df["Cantidad de activos fijos"] = [1 for i in range(0, len(df))]        
                      
        df.insert(34, "Calcular Depreciación", "")
        df["Calcular Depreciación"] = [ 0 if float(row['gross_purchase_account'])== float(row['opening_accumulated_depreciation']) else 1 for index, row in df.iterrows()]        
        
        df.insert(35, "Frecuencia de Depreciación (Meses)", "")
        df["Frecuencia de Depreciación (Meses)"] = [0 if row['gross_purchase_account']== row['opening_accumulated_depreciation'] else 1 for index, row in df.iterrows()]
                        
        df.insert(36, "Siguiente Fecha de Depreciación", "")

        df.insert(37, "Número de Póliza", "")

        df.insert(38, "Asegurador", "")

        df.insert(39, "Valor Asegurado", "")

        df.insert(40, "Fecha de inicio del seguro", "")

        df.insert(41, "Fecha de Finalización del Seguro", "")

        df.insert(42, "Seguro a Todo Riesgo", "")

        df.insert(43, "Requiere Mantenimiento", "")       
       
        df.insert(44, "Estado", "")
        df["Estado"] = ["Fully Depreciated" if int(row["Calcular Depreciación"])==0 else "Partially Depreciated" for index, row in df.iterrows()]
                 
        df.insert(45, "Activo Fijo Reservado", "")

        df.insert(46, "Monto de la compra", "")

        df.insert(47, "Libro de Finanzas Predeterminado", "")

        df.insert(48, "Estado de registro de entrada de depreciación", "")

        df.insert(49, "Modificado Desde", "")

        df.insert(50, "Identificador (Libros de Finanzas)", "")
        df["Identificador (Libros de Finanzas)"] = [row["Categoría de Activos Fijos"] for index, row in df.iterrows()]
        
        df.insert(51, "Frecuencia de Depreciación (Meses) (Libros de Finanzas)", "")
        df["Frecuencia de Depreciación (Meses) (Libros de Finanzas)"] = [1 if int(row["gross_purchase_account"])>int(row["opening_accumulated_depreciation"]) else 0 for index, row in df.iterrows()]
        
        df.insert(52, "Número total de amortizaciones (Libros de Finanzas)", "")
        df["Número total de amortizaciones (Libros de Finanzas)"] = [row["Número total de depreciaciones"] if row["Is Fully Depreciated"]==0 else '' for index, row in df.iterrows()]

        df.insert(53, "Método de depreciación (Libros de Finanzas)", "")
        df["Método de depreciación (Libros de Finanzas)"]=[row["Método de depreciación"] if row["Is Fully Depreciated"]==0 else '' for index, row in df.iterrows()]
                
        df.insert(54, "Depreciate based on daily pro-rata (Libros de Finanzas)", "")

        df.insert(55, "Depreciate based on shifts (Libros de Finanzas)", "")
        
        df.insert(56, "Fecha de contabilización de la depreciación (Libros de Finanzas)", "")
        df["Fecha de contabilización de la depreciación (Libros de Finanzas)"] = [datetime(datetime.today().year, datetime.today().month, 28) if row["Is Fully Depreciated"]==0 else '' for index, row in df.iterrows()]
                        
        df.insert(57, "Libro de finanzas (Libros de Finanzas)", "")

        df.insert(58, "Salvage Value Percentage (Libros de Finanzas)", "")

        df.insert(59, "Tasa de depreciación (Libros de Finanzas)", "")

        df.insert(60, "Total Number of Booked Depreciations  (Libros de Finanzas)", "")       
        
        df.insert(61, "Valor después de Depreciación (Libros de Finanzas)", "")
        
        df.insert(62, "Valor esperado después de la Vida Útil (Libros de Finanzas)", "")         
        
        df.drop(["codeGroup", "codeSubGroup", "descrip", "tasa", "centro_code", "centro_descrip", "tipo_depresiacion",
                 "purchase_date", "gross_purchase_account", "area", "subarea", "expense_code", "expense_descrip",
                 "opening_accumulated_depreciation", "codLocation", "id",
                 "nameSubGroup", "AFFechaApertura", "AFFechaNoDeprecia", "AFFechaDepreTotal",
                 "AFDeprecApertura", "NivelCodigo", "NivelDescrip"],  axis=1, inplace=True)

        return df

def getCategoryAF(conn: Connection, name:str):
        """
        Este metodo retorna las categorias de activos fijos obtenidos desde los Grupos y Subgrupos de SISCONT5
        """
                
        queryChilds = f"""SELECT SubGroup.NomGrupCodigo AS codeGroup
                          ,[NomSubgCodigo] AS codeSubGroup
                          ,CONCAT(SubGroup.NomGrupCodigo,[NomSubgCodigo]) AS erpcode
                          ,[NomgrupDescripcion] AS titleGroup                         
                          ,[NomSubgDescripcion] AS title
                          ,[NomSubgTasaEmpresa] AS tasa                         
                          ,[NomSubgTipoDepreciacion] AS tipo_depresiacion
                          FROM [{name}].[dbo].[SAFSubgruposAFT] AS SubGroup INNER JOIN [{name}].[dbo].[SAFGruposAFT] AS GGroup 
                          ON SubGroup.NomGrupCodigo = GGroup.NomGrupCodigo"""
        
        queryDeprec=f"""SELECT CONCAT(SubGroup.NomGrupCodigo, SubGroup.NomSubgCodigo) AS erpcode, 
                                (SELECT TOP (1) CONCAT([ClCuCuenta],'-', [ClCuSubcuenta], '-', [ClCuSubControl], '-', [ClCuAnalisis])     
                                FROM [{name}].[dbo].[SAFAPERTURA] AS AF INNER JOIN [{name}].[dbo].[SCGCLASIFICADORDECUENTAS] AS CTAS
                                ON AF.ClCuIdCuentaDeprec = CTAS.ClcuIDCuenta 
                                WHERE AF.NomGrupCodigo= SubGroup.NomGrupCodigo AND AF.SubGrupoCodigo=SubGroup.NomSubgCodigo AND AF.AFActivo = '') AS CTADEPREC
                        FROM [{name}].[dbo].[SAFSUBGRUPOSAFT] AS SubGroup
                        """
        queryAFT = f"""SELECT CONCAT(SubGroup.NomGrupCodigo, SubGroup.NomSubgCodigo) AS erpcode, 
                                (SELECT TOP (1) CONCAT([ClCuCuenta],'-', [ClCuSubcuenta], '-', [ClCuSubControl], '-', [ClCuAnalisis])        
                                FROM [{name}].[dbo].[SAFAPERTURA] AS AF INNER JOIN [{name}].[dbo].[SCGCLASIFICADORDECUENTAS] AS CTAS
                                ON AF.ClCuIdCuentaAF = CTAS.ClcuIDCuenta 
                                WHERE AF.NomGrupCodigo= SubGroup.NomGrupCodigo AND AF.SubGrupoCodigo=SubGroup.NomSubgCodigo AND AF.AFActivo = '') AS CTAAFT
                        FROM [{name}].[dbo].[SAFSUBGRUPOSAFT] AS SubGroup
                        """
        
        
        result = OrderedDict()
        result["doctype"] = "Asset Category"        
        
        df= runSQLQuery(queryChilds, conn)

        #Inserto la columna number en el Dataframe
        df.insert(0, "asset_category_name", "")
        #Genero los numeros de los subelementos
        df["asset_category_name"] = [f'{row['codeGroup']}{row['codeSubGroup']} {row['title']}' for index, row in df.iterrows()]
        
        df.insert(1, "finance_books", "")
        df["finance_books"] = [[{ "finance_book": f'{row['codeGroup']}{row['codeSubGroup']} {row['title']}',
                                 "depreciation_method": f'{"Straight Line" if row["tipo_depresiacion"]==1 else "Manual"}',
                                   "total_number_of_depreciations": int(1 if row["tipo_depresiacion"]==2 else (100/row["tasa"] if row['tasa']>0 else 0 )* 12), #Esta version le pone 1 cuando la depresiacion es Manual
                                   "frequency_of_depreciation" : 1,
                                   "depreciation_start_date": f'{datetime(datetime.today().year, 2, 28,0,0,0).date()}' }] for index, row in df.iterrows()]
       
        #Inserto las cuentas asociadas a esta categoria
        dfAFT=runSQLQuery(queryAFT, conn)
        dfAFT.dropna(subset=['CTAAFT'], inplace=True)
        dfDeprec=runSQLQuery(queryDeprec, conn)
        dfDeprec.dropna(subset=['CTADEPREC'], inplace=True)

        
        dictCTAS_AFT = {f"{int(row["erpcode"])}": int(f"""{str(row["CTAAFT"]).split('-')[0]}{
                                                           str(row["CTAAFT"]).split('-')[1] if int(str(row["CTAAFT"]).split('-')[1]) != 0 else ""}{
                                                           str(row["CTAAFT"]).split('-')[2] if int(str(row["CTAAFT"]).split('-')[2]) != 0 else ""}{
                                                           str(row["CTAAFT"]).split('-')[3] if int(str(row["CTAAFT"]).split('-')[3]) != 0 else ""}""") 
                                                           for i, row in dfAFT.iterrows()}
        print("OK")
        
        dictCTAS_DEPREC = {f"{int(row["erpcode"])}": int(f"""{str(row["CTADEPREC"]).split('-')[0]}{
                                                           str(row["CTADEPREC"]).split('-')[1] if int(str(row["CTADEPREC"]).split('-')[1]) != 0 else ""}{
                                                           str(row["CTADEPREC"]).split('-')[2] if int(str(row["CTADEPREC"]).split('-')[2]) != 0 else ""}{
                                                           str(row["CTADEPREC"]).split('-')[3] if int(str(row["CTADEPREC"]).split('-')[3]) != 0 else ""}""") 
                                                           for i, row in dfDeprec.iterrows()}
        
        #Elimino las categorias que no tienen elementos y por lo tanto no tienen cuentas fijas o depresiacion
        df=df[df.apply(lambda row: str(row['erpcode']) in dictCTAS_AFT.keys(), axis=1)]

        
        df.insert(2, "accounts", "")
        df["accounts"] = [[{"fixed_asset_account": dictCTAS_AFT.get(f'{row['erpcode']}', 0), 
                            "accumulated_depreciation_account": dictCTAS_DEPREC.get(f'{row['erpcode']}', 0)}] for index, row in df.iterrows()]
        
        
        #Elimino las columnas code_init y code_last
        df.drop(['codeGroup', 'codeSubGroup', 'title', 'titleGroup', 'tasa', 'tipo_depresiacion', 'erpcode'], axis=1, inplace=True)

        result["data"] = df.to_dict(orient="records")
            
        return result
 
    
def getFinanceBook(conn: Connection, name:str):
        """
        Este metodo exporta los libros de contabilidad necesarios para los activos fijos
        y son creados a partir de los grupos de Siscont
        """
        query = f"""SELECT [NomGrupCodigo] AS CodeGroup
                                ,[NomSubgCodigo] AS CodeSubGroup
                                ,[NomSubgDescripcion] AS Description
                                FROM [{name}].[dbo].[SAFSubgruposAFT]"""
        
        df = runSQLQuery(query, conn)

        #Inserto la columna number en el Dataframe
        df.insert(0, "finance_book_name", "")
        #Genero los numeros de los subelementos
        df["finance_book_name"] = [f'{row['CodeGroup']}{row['CodeSubGroup'] if int(row['CodeSubGroup']) != 0 else ""} {row["Description"]}' for index, row in df.iterrows()]
        #Elimino las columnas code_init y code_last
        df.drop(['CodeGroup', 'CodeSubGroup', 'Description'], axis=1, inplace=True)

        result = OrderedDict()      
        result["doctype"] = "Finance Book"        
        result["data"] =  df.to_dict(orient="records")

        return result
    
def getDepartment(conn: Connection, name:str):
        
        query=f"""SELECT [AreaCodigo] AS codeArea
                ,[AreaDescrip] AS nameArea            
                ,[AreaDesactivada] AS desactivada
                FROM [{name}].[dbo].[SMGAREASUBAREA]"""
        
        querySub=f"""
                SELECT Area.[AreaCodigo] AS codeArea
                    ,Area.[AreaDescrip] AS nameArea
                    ,SubArea.SareaCodigo AS codeSubArea
                    ,SubArea.SareaDescrip AS nameSubArea
                    ,SubArea.[SAreaDesactivada] AS desactivada
                FROM [{name}].[dbo].[SMGAREASUBAREA] AS Area INNER JOIN [{name}].[dbo].[SMGAREASUBAREA1] AS SubArea ON Area.AreaCodigo=SubArea.AreaCodigo
                """

        df = runSQLQuery(query, conn)

        #Inserto la columna number en el Dataframe
        df.insert(0, "department_name", "")
        #Genero los numeros de los subelementos
        df["department_name"] = [f'{row['codeArea']}-{row['nameArea']}' for index, row in df.iterrows()]
        #Elimino las columnas code_init y code_last
        df.drop(['codeArea', 'nameArea'], axis=1, inplace=True)
                
        result={"doctype": "Department"}        
        result["data"] =  df.to_dict(orient="records")

        df = runSQLQuery(querySub, conn)
        #Inserto la columna number en el Dataframe
        df.insert(0, "department_name", "")
        #Genero los numeros de los subelementos
        df["department_name"] = [f'{row['codeSubArea']}-{row['nameSubArea']}' for index, row in df.iterrows()]
        df.insert(1, "parent_department", "")
        #Genero los numeros de los subelementos
        df["parent_department"] = [f'{row['codeArea']}-{row['nameArea']}' for index, row in df.iterrows()]
        #Elimino las columnas code_init y code_last
        df.drop(['codeArea', 'nameArea', 'codeSubArea', 'nameSubArea'], axis=1, inplace=True)

        result["data"].append(df.to_dict(orient="records"))

        return result

def getLocation(conn: Connection, name:str):
        query = f"""SELECT [NivelDescrip] AS location_name
                           FROM [{name}].[dbo].[SAFNivelRespAreaSubarea]"""

        return createJSON(query, conn, doctype="Location")


def getSAFConfiguracionGeneral(conn: Connection):
        query= """SELECT [AFCGId]
                          ,[AFCGMesUltimaDepreciacion]
                          ,[AFCGAnoUltimaDepreciacion]
                          ,[AFCGUI]
                          ,[AFCGFechaModif]
                          ,[AFCGNivelResp]
                          ,[AFFechacierreApertura]
                          ,[AFNumeroDocumentoAutomatico]
                          ,[AFCGDeprecia]
                          FROM [{name}].[dbo].[SAFConfiguracionGeneral]
                          """
        return createJSON(query,conn, doctype="Asset")
    

def getSAFConfiguraCtas(conn: Connection):
        query="""SELECT [AFCuentas]
                        ,[ClCuIdCuenta]
                        ,[TipoCuenta]
                        ,[AFFlagClaveOcioso]
                        ,[AFAnoActiva]
                        ,[AFMesActica]
                        ,[AFRecalculado]
                        FROM [{name}].[dbo].[SAFConfiguraCtas] """
        
        return createJSON(query,conn, doctype="Asset")
    
def getSAFTiposOperacion(conn: Connection):
        query = """SELECT [IdInternoTipoOperacion]
                          ,[NClMACodigoTipoOperacion]
                          ,[NClMADescripcionTipoOperacion]
                          FROM [{name}].[dbo].[SAFTIPOSOPERACION]"""
        
        return createJSON(query,conn, doctype="Asset")
    
def getSAFNomClavOperacion(conn: Connection):
        query = """SELECT [NCIMACodigoTipoOperacion]
                          ,[NCIMASubCodigoTipoOperacion]
                          ,[NCIMADescripcionClaveOperacion]
                          ,[NCIMAActivo]
                          ,[NCIMAUserIDClaveOperacion]
                          ,[NCIMAFechaModifClaveOperacion]
                          FROM [{name}].[dbo].[SAFNomClavOperacion]"""
        
        return createJSON(query,conn, doctype="Asset")
    
def getSAFRelacionClaveTratamiento(conn: Connection):
        query="""SELECT [NCIMACodigoTipoOperacion]
                        ,[NClMASubCodigoTipoOperacion]
                        ,[TratamientoId]
                        FROM [{name}].[dbo].[SAFRelacionClaveTratamiento]"""
        
        return createJSON(query,conn, doctype="Asset")

    
def getSAFAsocAreaObjCtoSubelem(conn: Connection):
        query = """SELECT [AFAsocId]
                           ,[AFAreacodigo]
                           ,[AFSareaCodigo]
                           ,[OCostcodigo]
                           ,[CICuIsCuenta]
                           ,[SubelId]
                           ,[AFAsoUI]
                           ,[AFAsoFechaModif]
                           ,[AFAsocActiva]
                           ,[AFAsocDeprecio]
                           FROM [{name}].[dbo].[SAFAsocAreaObjCtoSubelem]"""
        
        return createJSON(query,conn, doctype="Asset")
    
def getSAFDocMovClienteFactura(conn: Connection):
        query="""SELECT [DocMovAFNro]
                        ,[NCIMACodigoTipoOperacion]
                        ,[Id-compra]
                        ,[DocAnoOper]
                        ,[CliCodigo]
                        ,[DocNumFactura]
                        ,[DocFechafactura]
                        FROM [{name}].[dbo].[SAFDocMovClienteFactura]"""
        
        return createJSON(query,conn, doctype="Asset")
    
def getSAFDocumentoMovimiento(conn: Connection):
        query="""SELECT [DocMovAFNro]
                        ,[NClMACodigoTipoOperacion]
                        ,[DocAnoOper]
                        ,[NClMASubCodigoTipoOperacion]
                        ,[DocMes]
                        ,[DocEstado]
                        ,[DocActContabiliza]
                        ,[DocContabilizado]
                        ,[BajaDocMovAF]
                        ,[DocConComprob]
                        ,[DocMovAFFecha]
                        ,[DocMovFechaAvaluo]
                        ,[DocValorMLC]
                        ,[DocValorMN]
                        ,[DocValorTotal]
                        ,[DocDeprecMLC]
                        ,[DocDeprecMN]
                        ,[DocTasaMoneda]
                        ,[DocCodMoneda]
                        ,[DocValorMEX]
                        ,[DocNoTransaccion]
                        ,[DocUBMCOperac]
                        ,[DocMovCRC]
                        ,[SRHPersonasId]
                        ,[SRHPersDireccionOficial]
                        ,[SRHPersonasDireccionFecha]
                        ,[DocDatosInteres]
                        ,[DocFechaPrestamo]
                        ,[DocFechaPrestamoRegreso]
                        FROM [{name}].[dbo].[SAFDocumentoMovimiento]"""
        
        return createJSON(query,conn, doctype="Asset")
    
def getSAFDocMovAltaBaja(conn: Connection):
        query = """SELECT [DocMovAFNro]
                          ,[NClMACodigoTipoOperacion]
                          ,[DocAnoOper]
                          ,[ConsAltaBaja]
                          ,[AFNumInv]
                          ,[AFFechaConfirm]
                          ,[AFConfirm]
                          ,[AFDeprecAcumConfirm]
                          ,[AFValorMNac]
                          ,[AFValorMLConver]
                          ,[AFValorMEXac]
                          ,[AFDeprecMN]
                          ,[AFDeprecMLC]
                          FROM [{name}].[dbo].[SAFDocMovAltaBaja]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFDocMovActualizaSC(conn: Connection):
        query = """SELECT [SafActSCNumInv]
                          ,[DocMovAFNro]
                          ,[SAFActSCAnoOper]
                          ,[SAFActSCMesOper]
                          ,[SAFActSCIdCuentaAF]
                          ,[SAFActSCIdCuentaAFAntes]
                          ,[SAFActSCIdCuentaDeprec]
                          ,[SAFActSCIdCuentaDeprecAntes]
                          ,[SAFActSCValorMEX]
                          ,[SAFActSCValorMEXAntes]
                          ,[SAFActSCValorMN]
                          ,[SAFActSCValorMNAntes]
                          ,[SAFActSCValorMLC]
                          ,[SAFActSCValorMLCAntes]
                          ,[SAFActSCDeprecMN]
                          ,[SAFActSCDeprecMNAntes]
                          ,[SAFActSCDeprecMLC]
                          ,[SAFActSCDeprecMLCAntes]
                          ,[SAFActSCSubTipoMov]
                          FROM [{name}].[dbo].[SAFDocMovActualizaSC]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFDocMovTrasladoAreaSubANivelR(conn: Connection):
        
        query = """SELECT [DocMovAFNro]
                          ,[NClMACodigoTipoOperacion]
                          ,[DocAnoOper]
                          ,[ConsTraslado]
                          ,[AFNumInv]
                          ,[AreaOrigen]
                          ,[AreaDestino]
                          ,[SubAreaOrigen]
                          ,[SubAreaDestino]
                          ,[NivelResponOrigen]
                          ,[NivelResponDestino]
                          ,[ObjcostoOrigen]
                          ,[ObjCostoDestino]
                          ,[TraslDeprecio]
                          ,[IdcuentaAFOrigen]
                          ,[IdCuentaAFDestino]
                          ,[TraslValorAF]
                          FROM [{name}].[dbo].[SAFDocMovTrasladoAreaSubANivelR]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFDocMovTrasladoReparAlquiler(conn: Connection):
        
        query = """SELECT [DocMovAFNro]
                          ,[NClMACodigoTipoOperacion]
                          ,[DocAnoOper]
                          ,[ConsRepAlq]
                          ,[AFNumInv]
                          ,[FechaTraslado]
                          ,[TrabajadorPrestamo]
                          FROM [{name}].[dbo].[SAFDocMovTrasladoReparAlquiler]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFPartidaDocuMovi(conn: Connection):
        
        query = """SELECT [SafPartNumIv]
                          ,[DocMovAFNro]
                          ,[NClMACodigoTipoOperacion]
                          ,[SafPartAnoOper]
                          ,[SafPartValorFinal]
                          ,[SafPartMesOper]
                          ,[SafPartValorIni]
                          ,[SafPartDepreIni]
                          ,[SafPartDepreFinal]
                          ,[SafPartTasaDepre]
                          ,[SafPartTasaDepreAntes]
                          ,[SafPartTasaDepreUni]
                          ,[SafPartTasaDepreUniAntes]
                          ,[SafPartGrupo]
                          ,[SafPartGrupoAntes]
                          ,[SafPartSubGrupo]
                          ,[SafPartSubGrupoAntes]
                          ,[SafPartDesc]
                          ,[SafPartDescAntes]
                          FROM [{name}].[dbo].[SAFPartidaDocuMovi]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFContabilizacion(conn: Connection):
        
        query = """SELECT [Contad]
                          ,[DocMovAFNro]
                          ,[ContIdComp]
                          ,[ContAnoOp]
                          ,[ContTipoTrat]
                          ,[ContTipoMov]
                          ,[ContClaveOperacion]
                          ,[ContTipoContab]
                          ,[ContActivo]
                          ,[ContUI]
                          ,[ContFechaModif]
                          ,[ContIdCompPatrimonial]
                          FROM [{name}].[dbo].[SAFContabilizacion]"""
        
        return createJSON(query, conn, doctype="Asset")
    

def getSAFContabilizacion1(conn: Connection):
        
        query = """SELECT [Contad]
                          ,[ContPartId]
                          ,[ClcuIDCuenta]
                          ,[ContPartGasto]
                          ,[ContPartPropia]
                          ,[ContPartImp]
                          ,[ContPartNat]
                          ,[OCostCodigo]
                          ,[OCostCentroB]
                          ,[ContPartUI]
                          ,[ContPartFechModif]
                          FROM [{name}].[dbo].[SAFContabilizacion1]"""
        
        return createJSON(query, conn, doctype="Asset")

def getSAFGruposAFT(conn: Connection):
        
        query = """SELECT [NomGrupCodigo]
                          ,[NomgrupDescripcion]
                          ,[NomGrupActivo]
                          ,[NomGrupAgrupacion]
                          ,[NomGrupDeprecia]
                          ,[NomGrupTasaEmpresa]
                          ,[NomGrupTasaUp]
                          ,[NomGrupTipoDepreciacion]
                          ,[NomGrupUsaSubgrupo]
                          FROM [{name}].[dbo].[SAFGruposAFT]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFSubgruposAFT(conn: Connection):
        
        query = """SELECT [NomGrupCodigo]
                          ,[NomSubgCodigo]
                          ,[NomSubgActivo]
                          ,[NomSubgDeprecia]
                          ,[NomSubgDescripcion]
                          ,[NomSubgTasaEmpresa]
                          ,[NomSubgTasaUP]
                          ,[NomSubgTipoDepreciacion]
                          FROM [{name}].[dbo].[SAFSubgruposAFT]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFSubmayorDepre(conn: Connection):
        
        query = """SELECT [SafNumInv]
                           ,[SafAnoOper]
                           ,[SafFechaActual]
                           ,[SafTipoMetodo]
                           ,[SafDepreInicial]
                           ,[SafDepreAcumulada]
                           ,[SafMesDepre1]
                           ,[SafMesDepre2]
                           ,[SafMesDepre3]
                           ,[SafMesDepre4]
                           ,[SafMesDepre5]
                           ,[SafMesDepre6]
                           ,[SafMesDepre7]
                           ,[SafMesDepre8]
                           ,[SafMesDepre9]
                           ,[SafMesDepre10]
                           ,[SafMesDepre11]
                           ,[SafMesDepre12]
                           ,[SafTasaMesDepre1]
                           ,[SafTasaMesDepre2]
                           ,[SafTasaMesDepre3]
                           ,[SafTasaMesDepre4]
                           ,[SafTasaMesDepre5]
                           ,[SafTasaMesDepre6]
                           ,[SafTasaMesDepre7]
                           ,[SafTasaMesDepre8]
                           ,[SafTasaMesDepre9]
                           ,[SafTasaMesDepre10]
                           ,[SafTasaMesDepre11]
                           ,[SafTasaMesDepre12]
                           ,[SafIdUsuario]
                           ,[SafFechaModif]
                           ,[SafAreaCodigo]
                           ,[SafSubAreaCodigo]
                           ,[SafObjetoCosto]
                           ,[SafClCuIdCuentaGasto]
                           ,[SafClCuIdCuentaDeprec]
                           ,[SafSubElementoCodigo]
                           ,[SafSubDepreCRC]
                           FROM [{name}].[dbo].[SAFSubmayorDepre]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFSubTasaMayor(conn: Connection):
        
        query = """SELECT [SafTasaNumInv]
                          ,[SafTasaAnoOper]
                          ,[SafTasaTipoMetodo]
                          ,[SafTasaAcumulado]
                          ,[SafTasaInicial]
                          ,[SafTasaFechaActual]
                          ,[SafTasaFechaModif]
                          ,[SafTasaIdUsuario]
                          ,[SafMesDepre1TasaMayor]
                          ,[SafMesDepre2TasaMayor]
                          ,[SafMesDepre3TasaMayor]
                          ,[SafMesDepre4TasaMayor]
                          ,[SafMesDepre5TasaMayor]
                          ,[SafMesDepre6TasaMayor]
                          ,[SafMesDepre7TasaMayor]
                          ,[SafMesDepre8TasaMayor]
                          ,[SafMesDepre9TasaMayor]
                          ,[SafMesDepre10TasaMayor]
                          ,[SafMesDepre11TasaMayor]
                          ,[SafMesDepre12TasaMayor]
                          ,[SafTasaArea]
                          ,[SafTasasubarea]
                          ,[SafTasaObjetoCosto]
                          ,[SafTasaIdCuentaGasto]
                          ,[SafTasaIdCuentaDepre]
                          ,[SafTasaSubelCodigo]
                          FROM [{name}].[dbo].[SAFSubTasaMayor]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFContabilidadDepreciacion(conn: Connection):
        
        query = """SELECT [ContabDepreId]
                          ,[ContabDepreTipoCompro]
                          ,[ContabDepreIdComp]
                          ,[ContabDepreMesOper]
                          ,[ContabDepreAnoOper]
                          ,[ContabDepreTerminado]
                          ,[ContabDepreActivo]
                          ,[ContabDepreUI]
                          ,[ContabDepreFechaMod]
                          FROM [{name}].[dbo].[SAFContabilidadDepreciacion]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFContabilidadDepreciacion1(conn: Connection):
        
        query = """SELECT [ContabDepreId]
                          ,[ContDeprecId]
                          ,[ClcuIDCuenta]
                          ,[ContDeprecPartId]
                          ,[ContDeprecGasto]
                          ,[ContDeprecImporte]
                          ,[ContDeprecNaturaleza]
                          ,[ContDeprecCeBe]
                          ,[OCostcodigo]
                          ,[ContDeprecPropia]
                          ,[ContDeprecUI]
                          ,[ContDeprecFechaMod]
                          FROM [{name}].[dbo].[SAFContabilidadDepreciacion1]"""
        
        return createJSON(query, conn, doctype="Asset")

def getSAFSaldosCuentas(conn: Connection):
        
        query = """SELECT [AFSaldoId]
                          ,[ClcuIDCuenta]
                          ,[AFSaldoInicial]
                          ,[AFSaldoEnero]
                          ,[AFSaldofebrero]
                          ,[AFSaldomarzo]
                          ,[AFSaldoAbril]
                          ,[AFSaldoMayo]
                          ,[AFSaldoJunio]
                          ,[AFSaldoJulio]
                          ,[AFSaldoAgosto]
                          ,[AFSaldoseptiembre]
                          ,[AFSaldoOctubre]
                          ,[AFSaldoNoviembre]
                          ,[AFSaldoDiciembre]
                          ,[AFSaldoUI]
                          ,[AFSaldoFechaModif]
                          ,[AFSaldoAnio]
                          FROM [{name}].[dbo].[SAFSaldosCuentas]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFSEGCHK(conn: Connection):
        
        query = """SELECT [AFEntiId]
                          ,[AFTabla0]
                          ,[AFTabla1]
                          ,[AFTabla2]
                          ,[AFTabla3]
                          ,[AFTabla4]
                          ,[AFTabla5]
                          ,[AFTabla6]
                          ,[AFTabla7]
                          ,[AFTabla8]
                          ,[AFTabla9]
                          FROM [{name}].[dbo].[SAFSEGCHK]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFSaldoInicial(conn: Connection):
        
        query = """SELECT [SIAfNumInv]
                          ,[SIAnoOperacion]
                          ,[SIIdcuentaAF]
                          ,[SIIdcuentaDep]
                          ,[SIValorAFMN]
                          ,[SIValorAFMLC]
                          ,[SIValorDepTotal]
                          FROM [{name}].[dbo].[SAFSaldoInicial]"""

        return createJSON(query, conn, doctype="Asset")
    
def getSAFRecalculo(conn: Connection):
        
        query = """SELECT [RecalId]
                          ,[ClCuIdcuenta]
                          ,[AFNumInv]
                          ,[RecalAnio]
                          ,[RecalMes]
                          ,[RecalTasa]
                          ,[RecalCoeficiente]
                          ,[RecalPorciento]
                          ,[RecalVariacion]
                          ,[RecalTipo]
                          ,[RecalAFValorAnterior]
                          ,[RecalAFValorNoRecalculado]
                          ,[RecalAFValorRecalculado]
                          ,[RecalAFVariacion]
                          ,[RecalAFValorFinal]
                          ,[RecalAFValorDepAnt]
                          ,[RecalAFValorDepNoRecal]
                          ,[RecalAFValorDepRecal]
                          ,[RecalAFValorDepVar]
                          ,[RecalAFValorDeprec]
                          FROM [{name}].[dbo].[SAFRecalculo]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFCuentasTemporal(conn: Connection):
        
        query = """SELECT [clcuidCuentaTmp]
                          ,[clCuCuentaTmp]
                          ,[clCuSubcuentaTmp]
                          ,[clCuSubcontrolTmp]
                          ,[clCuAnalisisTmp]
                          ,[DescripcionCuentaTmp]
                          FROM [{name}].[dbo].[SAFCuentasTemporal]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFTrnActivosFijosTemporales(conn: Connection):
        
        query = """SELECT [AFTemporalNumInv]
                          ,[AFNumInvTMP]
                          FROM [{name}].[dbo].[SAFTrnActivosFijosTemporales]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFTrnComponenteTemporales(conn: Connection):
        
        query = """SELECT [AFNumInvTMP]
                           ,[AFNumCompTemp]
                           ,[DescripcionCompTMP]
                           ,[CantidadCompTMP]
                           ,[ValorMLCCompTmp]
                           ,[ValorMnComptmp]
                           ,[ValortotalCompTMP]
                           ,[DepAcumMLCCompTMP]
                           ,[DepAcumMNCompTMP]
                           ,[DepAcumTotalCompTMP]
                           ,[AFNumImvConversion]
                           ,[UnificadoTMP]
                           ,[ValorMEXCompTmp]
                           FROM [{name}].[dbo].[SAFTrnComponenteTemporales]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFAFComponentesTemporal(conn: Connection):
        
        query = """SELECT [NumInvTmp]
                          ,[DocMovAFNroTMP]
                          ,[AFValorMNTMP]
                          ,[AFValorMLCTMP]
                          ,[AFDeprecMNTMP]
                          ,[AFDeprecMLCTMP]
                          ,[AFValorTotalTMP]
                          ,[AFDeprecTotalTMP]
                          FROM [{name}].[dbo].[SAFAFComponentesTemporal]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFTrnGrupoSubgrupoTemporal(conn: Connection):
        
        query = """SELECT [NomGrupCodigoTmp]
                          ,[NomSubgCodigoTemp]
                          ,[DescripcionGrupoSubgrupo]
                          FROM [{name}].[dbo].[SAFTrnGrupoSubgrupoTemporal]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFCompActualizaSC(conn: Connection):
        
        query = """SELECT [AFNumcomp]
                          ,[SafPartNumIv]
                          ,[DocMovAFNro]
                          ,[NClMACodigoTipoOperacion]
                          ,[CantidadCompAntes]
                          ,[CantidadCompfinal]
                          ,[ValorMNCompAntes]
                          ,[ValorMNCompFinal]
                          ,[ValorMLCCompAntes]
                          ,[ValorMLCCompfinal]
                          ,[ValorMEXCompAntes]
                          ,[ValorMEXCompFinal]
                          ,[DescripcionCompBaja]
                          ,[AfNumInvConversionBaja]
                          ,[UnificadoCompBaja]
                          ,[DeprecAcumMLCAntes]
                          ,[DeprecAcumMNAntes]
                          ,[DeprecAcumTotalAntes]
                          FROM [{name}].[dbo].[SAFTEAFCompRechazado]"""
        
        return createJSON(query, conn, doctype="Asset")
    
def getSAFConfigPartidasGub(conn: Connection):
        
        query = """SELECT [ConfPGId]
                          ,[ConfPGUI]
                          ,[ConfPGFechaModif]
                          ,[PartGCodigo]
                          FROM [{name}].[dbo].[SAFConfigPartidasGub]"""
        
        return createJSON(query, conn, doctype="Asset")
    

def getSAFRelacAreaGub(conn: Connection):
        
        query = """SELECT [AreaCodigo]
                          ,[ClcuIDCuenta]
                          ,[RelacCuenta]
                          ,[RelacSubcuenta]
                          ,[RelacSubctrol]
                          ,[RelacUI]
                          ,[RelacActivo]
                          ,[RelacFechaModif]
                          FROM [{name}].[dbo].[SAFRelacAreaGub]"""
        
        return createJSON(query, conn, doctype="Asset")


    