# utils/discover_all_instances.py
import socket
import pyodbc

def _udp_browser_discovery(host: str, timeout: float) -> list[dict]:
    """Intenta descubrir instancias vía UDP 1434 (SQL Server Browser)."""
    packet = b"\x02"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    instances = []
    try:
        sock.sendto(packet, (host, 1434))
        data, _ = sock.recvfrom(16384)
        if data and data[0] == 0x05:
            data = data[3:]
        response_text = data.decode("latin-1", errors="ignore")
        raw_instances = response_text.split(";;")
        for raw_inst in raw_instances:
            if not raw_inst or "InstanceName" not in raw_inst:
                continue
            parts = raw_inst.split(";")
            inst_data = {}
            for i in range(0, len(parts) - 1, 2):
                if parts[i] and i + 1 < len(parts):
                    inst_data[parts[i].lower()] = parts[i + 1]
            instances.append({
                "instance_name": inst_data.get("instancename", "MSSQLSERVER"),
                "port": int(inst_data.get("tcp", 1433)),
                "version": inst_data.get("version", "Desconocida"),
                "server_name": inst_data.get("servername", host),
            })
    except socket.timeout:
        pass
    finally:
        sock.close()
    return instances


def _tcp_probe_instance(host: str, port: int, user: str | None, password: str | None,
                        timeout: float) -> dict | None:
    """Verifica una instancia TCP. Si hay credenciales obtiene @@SERVICENAME, si no, valida el puerto."""
    # Si no hay credenciales, hacemos un ping de socket básico para ver si el puerto 1433 responde
    if not user or not password:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            sock.close()
            return {
                "instance_name": "MSSQLSERVER (Por defecto)",
                "port": port,
                "version": "Detectada (Requiere Login)",
                "server_name": host,
            }
        except Exception:
            return None

    # Si hay credenciales, hacemos la consulta completa vía ODBC
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={host},{port};"
            f"UID={user};PWD={password};"
            f"LoginTimeout={int(timeout)};"  # <-- Corrección de Timeout nativo
            f"TrustServerCertificate=yes;"
        )
        with pyodbc.connect(conn_str, timeout=int(timeout)) as conn:
            row = conn.execute("SELECT @@SERVICENAME, @@VERSION").fetchone()
            if row:
                svc_name = (row[0] or "MSSQLSERVER").strip().upper()
                version_full = row[1] or "Desconocida"
                version = version_full.split("\n")[0].strip()
                return {
                    "instance_name": svc_name,
                    "port": port,
                    "version": version,
                    "server_name": host,
                }
    except Exception:
        return None


def discover_all_mssql_instances(
    host: str,
    timeout: float = 3.0,
    user: str | None = None,
    password: str | None = None,
) -> list[dict]:
    """
    Descubre instancias SQL Server:
    1. Intenta UDP Browser (sin credenciales).
    2. Fallback TCP: Si el UDP falla, prueba el puerto 1433 (con o sin credenciales).
    """
    # Nivel 1: UDP Browser
    instances = _udp_browser_discovery(host, timeout)
    if instances:
        return instances

    # Nivel 2: TCP fallback (ahora siempre se intenta)
    result = _tcp_probe_instance(host, 1433, user, password, timeout)
    if result:
        return [result]

    # Nada funcionó
    raise RuntimeError(
        f"No se encontraron instancias SQL Server en '{host}'."
    )