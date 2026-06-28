# utils/discover_all_instances.py
"""
Descubrimiento de instancias SQL Server — tres niveles de fallback:

  Nivel 1 — UDP Browser (puerto 1434)
      El más rápido y preciso: SQL Server Browser devuelve todas las instancias
      con su nombre, puerto y versión en una sola respuesta UDP.
      Falla si: Browser está desactivado o el firewall bloquea UDP 1434.

  Nivel 2 — TCP 1433 (puerto estándar)
      Prueba directa al puerto por defecto. Si responde, asume instancia
      MSSQLSERVER y, si hay credenciales, obtiene @@SERVICENAME y @@VERSION.
      Falla si: la instancia está en un puerto dinámico o no estándar.

  Nivel 3 — Escaneo TCP en paralelo (puertos comunes conocidos)
      Escanea en paralelo un conjunto de puertos habituales de SQL Server
      (1433, 2433, 4022, variantes cercanas…).
      El rango dinámico de Windows (49152-65535) NO se escanea: en redes
      corporativas el firewall bloquea ese rango completo y el escaneo
      nunca termina con resultados útiles. Si la instancia usa un puerto
      dinámico, el administrador debe abrirlo o fijar un puerto estático.

Los tres niveles se intentan en orden; el primero que devuelve resultados
gana y se retorna de inmediato.

PUERTOS QUE DEBEN ESTAR ABIERTOS EN EL FIREWALL DEL SERVIDOR:
  - UDP 1434  — SQL Server Browser (descubrimiento de instancias)
  - TCP 1433  — Instancia por defecto (MSSQLSERVER)
  - TCP 2433  — Puerto alternativo habitual
  - TCP 4022  — SQL Server Service Broker
  - TCP 5022  — Always On Availability Groups
  Si la instancia usa un puerto personalizado, ese puerto TCP también
  debe estar abierto. Se recomienda fijar un puerto estático en lugar
  de depender del rango dinámico (49152-65535).
"""

import socket
import pyodbc
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------------------------------------------------------
# Puertos "conocidos" de SQL Server — único conjunto que se escanea.
# El rango dinámico (49152-65535) fue eliminado: en redes corporativas el
# firewall lo bloquea en su totalidad y el escaneo nunca devuelve resultados.
# Si la instancia objetivo usa un puerto dinámico, el administrador debe
# convertirlo a puerto estático en SQL Server Configuration Manager.
# ---------------------------------------------------------------------------
_SQL_COMMON_PORTS: list[int] = [
    1433,   # puerto estándar / instancia por defecto
    1434,   # SQL Server Browser TCP (raro pero posible)
    2433,   # alternativa habitual tras redirigir el 1433
    4022,   # SQL Server Service Broker
    5022,   # Always On Availability Group endpoint habitual
    1431, 1432, 1435, 1436, 1437, 1438, 1439, 1440, 14330,  # variantes cercanas
]

# Hilos concurrentes para el escaneo TCP de puertos comunes
_SCAN_WORKERS = 50


# ---------------------------------------------------------------------------
# Nivel 1: UDP Browser
# ---------------------------------------------------------------------------

def _udp_browser_discovery(host: str, timeout: float) -> list[dict]:
    """Intenta descubrir instancias vía UDP 1434 (SQL Server Browser)."""
    packet = b"\x03"          # SSRP: solicitud de lista de instancias
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    instances: list[dict] = []
    try:
        sock.sendto(packet, (host, 1434))
        data, _ = sock.recvfrom(16384)
        # Cabecera SSRP: 3 bytes (tipo 0x05 + longitud 2 bytes) → descartar
        if data and data[0] == 0x05:
            data = data[3:]
        response_text = data.decode("latin-1", errors="ignore")
        raw_instances = response_text.split(";;")
        for raw_inst in raw_instances:
            if not raw_inst or "InstanceName" not in raw_inst:
                continue
            parts = raw_inst.split(";")
            inst_data: dict[str, str] = {}
            for i in range(0, len(parts) - 1, 2):
                if parts[i] and i + 1 < len(parts):
                    inst_data[parts[i].lower()] = parts[i + 1]
            tcp_port = inst_data.get("tcp", "").strip()
            
            # MODIFICACIÓN CRÍTICA:
            # Si el puerto no es un número válido, NO agregues esta instancia aquí.
            # Al no agregarla, 'instances' quedará vacía y el script bajará 
            # automáticamente al Nivel 3 (Escaneo de puertos en paralelo).
            if not tcp_port.isdigit():
                continue
            
            instances.append({
                "instance_name": inst_data.get("instancename", "MSSQLSERVER"),
                "port": int(tcp_port) if tcp_port.isdigit() else 1433,
                "version": inst_data.get("version", "Desconocida"),
                "server_name": inst_data.get("servername", host),
            })
    except socket.timeout:
        pass
    except Exception:
        pass
    finally:
        sock.close()
    return instances


# ---------------------------------------------------------------------------
# Nivel 2 y 3 — auxiliares TCP
# ---------------------------------------------------------------------------

def _tcp_port_open(host: str, port: int, timeout: float) -> bool:
    """Devuelve True si el puerto TCP responde (conexión exitosa)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        sock.close()


def _odbc_probe(host: str, port: int, user: str, password: str, timeout: float) -> dict | None:
    """
    Intenta conectarse a host:port con credenciales ODBC.
    Si tiene éxito devuelve un dict con instance_name, port, version, server_name.
    Devuelve None si falla (puerto no es SQL Server o credenciales incorrectas).
    """
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={host},{port};"
        f"UID={user};PWD={password};"
        f"LoginTimeout={max(2, int(timeout))};"
        f"TrustServerCertificate=yes;"
    )
    try:
        with pyodbc.connect(conn_str, timeout=max(2, int(timeout))) as conn:
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
        pass
    return None


def _tcp_probe_instance(
    host: str,
    port: int,
    user: str | None,
    password: str | None,
    timeout: float,
) -> dict | None:
    """
    Verifica si hay un SQL Server en host:port.
    - Sin credenciales: sólo comprueba que el puerto TCP responde.
    - Con credenciales: hace la consulta ODBC para confirmar y obtener detalles.
    """
    if not user or not password:
        if _tcp_port_open(host, port, timeout):
            return {
                "instance_name": "MSSQLSERVER (Por defecto)",
                "port": port,
                "version": "Detectada (requiere login para ver detalles)",
                "server_name": host,
            }
        return None

    # Con credenciales: intento ODBC directo (incluye verificación de puerto)
    return _odbc_probe(host, port, user, password, timeout)


# ---------------------------------------------------------------------------
# Nivel 3: Escaneo TCP en paralelo (sólo puertos comunes conocidos)
# ---------------------------------------------------------------------------

def _scan_ports_parallel(
    host: str,
    user: str | None,
    password: str | None,
    timeout: float,
) -> list[dict]:
    """
    Escanea en paralelo únicamente los puertos conocidos de SQL Server.

    El rango dinámico de Windows (49152-65535) ha sido eliminado:
    en redes corporativas el firewall lo bloquea completamente y el escaneo
    tardaba varios segundos sin producir resultados útiles.

    Si la instancia usa un puerto dinámico, el administrador de red debe:
      a) Fijar un puerto estático en SQL Server Configuration Manager, O
      b) Abrir ese puerto específico en el firewall y añadirlo a
         _SQL_COMMON_PORTS en esta configuración.

    Devuelve la lista de instancias encontradas ordenadas por puerto.
    """
    found: list[dict] = []

    with ThreadPoolExecutor(max_workers=min(_SCAN_WORKERS, len(_SQL_COMMON_PORTS))) as ex:
        futures = {
            ex.submit(_tcp_probe_instance, host, port, user, password, timeout): port
            for port in _SQL_COMMON_PORTS
        }
        for fut in as_completed(futures):
            result = fut.result()
            if result:
                found.append(result)

    return sorted(found, key=lambda x: x["port"])


# ---------------------------------------------------------------------------
# Función pública principal
# ---------------------------------------------------------------------------

def discover_all_mssql_instances(
    host: str,
    timeout: float = 3.0,
    user: str | None = None,
    password: str | None = None,
) -> list[dict]:
    """
    Descubre instancias SQL Server en *host* usando tres niveles de fallback.

    Args:
        host:     IP o nombre del servidor.
        timeout:  Segundos de espera por intento de conexión.
        user:     Usuario SQL (opcional; mejora la calidad de los resultados).
        password: Contraseña SQL (opcional; ídem).

    Returns:
        Lista de dicts con claves: instance_name, port, version, server_name.
        Nunca devuelve lista vacía — lanza RuntimeError si no encuentra nada.

    Raises:
        RuntimeError: Si ningún nivel detectó instancias.
    """

    # ── Nivel 1: UDP Browser ───────────────────────────────────────────────
    instances = _udp_browser_discovery(host, timeout)
    if instances:
        return instances

    # ── Nivel 2: TCP puerto 1433 (estándar) ───────────────────────────────
    result = _tcp_probe_instance(host, 1433, user, password, timeout)
    if result:
        return [result]

    # ── Nivel 3: Escaneo TCP en paralelo ──────────────────────────────────
    instances = _scan_ports_parallel(host, user, password, timeout)
    if instances:
        return instances

    # Sin resultados en ningún nivel
    raise RuntimeError(
        f"No se encontraron instancias SQL Server en '{host}'.\n"
        "Verificar: SQL Server Browser, TCP/IP habilitado, firewall, "
        "y que el servicio SQL Server esté activo."
    )