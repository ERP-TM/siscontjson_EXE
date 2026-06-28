"""
Constantes compartidas para clasificación de clientes/proveedores.

IMPORTANTE: estas listas deben mantenerse sincronizadas entre los queries
de Customer, Supplier y Bank Account. Si agregas o quitas una categoría,
hazlo aquí — los tres queries la heredan automáticamente.
"""

# ── Categorías ─────────────────────────────────────────────────────────────

# Categorías que se exportan como Customer
CUSTOMER_CATEGORIES = ["C", "CP", "L", "LP", "LR", "A", "CR"]

# Categorías que se exportan como Supplier
SUPPLIER_CATEGORIES = ["P", "CP", "R", "CR", "LR", "A", "LP"]


def sql_in_clause(categories: list[str]) -> str:
    """
    Convierte una lista de categorías en el formato listo para usar
    dentro de un IN (...) de SQL Server.

    Ejemplo:
        sql_in_clause(['C', 'CP']) -> "'C', 'CP'"
    """
    return ", ".join(f"'{c}'" for c in categories)


# ── Fechas ─────────────────────────────────────────────────────────────────

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}