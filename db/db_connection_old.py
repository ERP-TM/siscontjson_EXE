# db/db_connection.py
# Conexión a la base de datos SQL Server usando SQLAlchemy + pyodbc

import json
from contextlib import contextmanager
from os import makedirs, path
from typing import Any, Dict, List

import pandas as pd
from sqlalchemy import create_engine, URL, Connection, text
from sqlalchemy.engine import Engine

from config import get_settings
from db.db_manager import ConexionParams
from utils.serializations import is_serializable, serialize_value

settings = get_settings()


def create_engine_from_params(params: ConexionParams) -> Engine:
    """
    Crea un engine de SQLAlchemy usando pyodbc

    Args:
        params: Puede ser ConexionParams o dict con los parámetros de conexión
        Si se provee instance_name, usa SERVER=host\\instance (SQL Browser resuelve el puerto)
        Si no, usa SERVER=host,puerto

    Returns:
        Engine de SQLAlchemy configurado
    """
    # 🔍 DEBUG TEMPORAL - AGREGAR ESTO
    # print("=" * 70)
    # print("🔍 DEBUG create_engine_from_params")
    # print(f"   Tipo recibido: {type(params)}")
    
    # Si recibimos un dict, convertirlo a ConexionParams
    if isinstance(params, dict):
        # print(f"   ⚠️  Convertiendo dict a ConexionParams")
        # print(f"   Dict recibido: {params}")
        params = ConexionParams(**params)
    
    # print(f"   Host: {params.host}")
    # print(f"   Database: {params.database}")
    # print(f"   Instance: {params.instance_name}")
    
    # Determinar el SERVER según si hay instancia nombrada o no
    if params.instance_name:
        server = f"{params.host}\\{params.instance_name}"
        # print(f"   ✅ SERVER con instancia: {server}")
    else:
        server = f"{params.host},{settings.SQL_PORT}"
        # print(f"   ✅ SERVER sin instancia: {server}")
    
    # Construir la cadena de conexión para pyodbc
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        # f"SERVER={params.host},{settings.SQL_PORT};"
        f"SERVER={server};"
        f"DATABASE={params.database};"
        f"UID={settings.SQL_USER};"
        f"PWD={params.password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"Timeout=5;"
    )

    # Crear URL de SQLAlchemy con pyodbc
    url_object = URL.create(
        'mssql+pyodbc',
        query={"odbc_connect": connection_string}
    )

    try:
        # Crear el motor de SQLAlchemy
        engine = create_engine(url_object)
        return engine
    except Exception as e:
        error_msg = str(e)
        # Mapeo de errores comunes
        if "Cannot open database" in error_msg:
            raise Exception(
                "La base de datos especificada no existe o no se puede acceder.")
        elif "Login failed for user" in error_msg:
            raise Exception(
                "Error de autenticación: usuario o contraseña incorrectos.")
        elif "Unable to connect" in error_msg or "connection" in error_msg.lower():
            raise Exception(
                "No se puede conectar al servidor. Verifique la IP y el puerto.")
        else:
            raise Exception(
                f"Error de conexión a la base de datos: {error_msg}")


@contextmanager
def get_db_connection(params: ConexionParams):
    """
    Context manager para obtener una conexión de SQLAlchemy

    Args:
        params: Parámetros de conexión
        Puede ser ConexionParams o dict con los parámetros de conexión

    Yields:
        Connection de SQLAlchemy

    Example:
        with get_db_connection(params) as conn:
            result = conn.execute(text("SELECT 1"))
    """
    
    # 🔑 CLAVE: Si recibimos un dict, convertirlo a ConexionParams
    if isinstance(params, dict):
        params = ConexionParams(**params)
        
    engine = create_engine_from_params(params)
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
        engine.dispose()


def create_db_managerAlchemy(params: ConexionParams) -> Connection:
    """
    Crea una conexión de SQLAlchemy usando pyodbc
    Este metodo mantiene compatibilidad con el código existente de las APIs

    Args:
        params: Parámetros de conexión
        Puede ser ConexionParams o dict con los parámetros de conexión

    Returns:
        Connection de SQLAlchemy
    """
    # 🔑 CLAVE: Si recibimos un dict, convertirlo a ConexionParams
    if isinstance(params, dict):
        params = ConexionParams(**params)
        
    engine = create_engine_from_params(params)
    return engine.connect()


def test_connection(params: ConexionParams) -> bool:
    """
    Prueba la conexión a la base de datos

    Args:
        params: Puede ser ConexionParams o dict con los parámetros de conexión

    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        # 🔑 CLAVE: Si recibimos un dict, convertirlo a ConexionParams
        if isinstance(params, dict):
            params = ConexionParams(**params)
            
        with get_db_connection(params) as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            return row is not None and row[0] == 1
    except Exception:
        return False


def runSQLQuery(query: str, connection: Connection) -> pd.DataFrame:
    """
    Ejecuta una query SQL y retorna el resultado como DataFrame de pandas

    Args:
        query: Query SQL a ejecutar
        connection: Conexión de SQLAlchemy

    Returns:
        DataFrame con los resultados
    """
    try:
        df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        raise e


def createJSON(query: str, connection: Connection, doctype: str) -> dict:
    """
    Crea un JSON a partir de una query SQL

    Args:
        query: Query SQL a ejecutar
        connection: Conexión de SQLAlchemy
        doctype: Tipo de documento

    Returns:
        Diccionario con el doctype y los datos
    """
    df = runSQLQuery(query, connection)
    df = changeFormatToString(df)
    records = df.to_dict(orient="records")

    result = {"doctype": doctype}
    result["data"] = records

    return result


def changeFormatToString(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte todas las columnas del DataFrame a string

    Args:
        df: DataFrame a convertir

    Returns:
        DataFrame con columnas convertidas a string
    """
    # Convierto las columnas datetime en string
    for col in df.columns:
        df[col] = df[col].astype(str)

    return df
