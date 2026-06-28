import re
import unicodedata
import json
from typing import Any, Dict, List, Callable, Optional

# def clean_name_field(value: Any) -> str:
# if not isinstance(value, str) or not value:
#     return value

# # Eliminar solo caracteres de control invisibles, no caracteres de contenido
# cleaned = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", value)

# # Eliminar caracteres especiales que no corresponden a nombres
# # Reemplazandolos por espacio
# cleaned = re.sub(r"[<>|\\\"*?]", " ", cleaned)

# cleaned = re.sub(r"\s+", " ", cleaned)
# cleaned = cleaned.strip()

# return cleaned


def clean_name_field(value: Any) -> str:
    if not isinstance(value, str) or not value:
        # Nota: Si value no es str (ej. None o int), devolverlo directamente
        # podría romper tipados estrictos, pero mantenemos tu lógica original.
        return value

    # 1. Reemplazar tabs, saltos de línea y caracteres especiales molestos por un ESPACIO
    # Esto evita que "Juan\nPérez" se convierta en "JuanPérez"
    cleaned = re.sub(r"[<>|\\\"*?\t\n\r]", " ", value)

    # 2. Eliminar el resto de caracteres de control invisibles que queden
    cleaned = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", cleaned)

    # 3. Colapsar espacios múltiples (cualquier tipo de espacio) y quitar los de los extremos
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def clean_email_field(value: Any) -> Optional[str]:
    if not value or not isinstance(value, str):
        return None

    # Normalizar caracteres Unicode ocultos (convierte \xa0 y espacios raros en espacios normales)
    value = unicodedata.normalize("NFKC", value)
    value = value.strip()

    # Eliminar acentos y caracteres diacríticos (á→a, é→e, ü→u, ñ→n, etc.)
    # value = unicodedata.normalize("NFD", value)
    # value = "".join(c for c in value if unicodedata.category(c) != "Mn")

    # Normalización de errores comunes (coma por punto en el dominio)
    if "@" in value:
        parts = value.split("@")
        if len(parts) == 2:
            parts[1] = parts[1].replace(",", ".")
            value = "@".join(parts)

    # Extraemos la primera palabra o bloque que parezca un correo válido.
    # Esto captura 'el correo correcto' e ignora lo que venga después.
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w{2,}", value)

    if match:
        email_detectado = match.group(0).lower()

        # Rechazar si contiene caracteres no-ASCII (acentos, ñ, dirección, logística, etc.)
        if not email_detectado.isascii():
            return None

        # Asegurar un último chequeo estricto sobre lo que se extrajo
        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email_detectado):
            return email_detectado

    # No retorna nada por no cumplir con el formato correcto del correo
    return None


def clean_numeric_field(value: Any) -> str:
    """
    Limpia campos numéricos permitiendo solo dígitos.
    Útil para números de teléfono, cédulas, etc.
    """
    if not value or not isinstance(value, str):
        return value
    return re.sub(r"[^\d]", "", value)


def clean_alphanumeric_field(value: Any) -> str:
    """
    Limpia campos alfanuméricos permitiendo solo letras, números y espacios.
    Útil para códigos de empleado, números de cuenta, etc.
    """
    if not value or not isinstance(value, str):
        return value

    value = value.strip()
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", value)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def clean_text_field(value: Any) -> str:
    """
    Limpieza general para campos de texto.
    Elimina caracteres de control y normaliza espacios.
    """
    if not value or not isinstance(value, str):
        return value

    # Eliminar caracteres de control (tabs, saltos de línea múltiples, etc.)
    value = value.strip()
    cleaned = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", value)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def apply_field_cleaners(
    records: List[Dict[str, Any]], field_cleaners: Dict[str, Callable[[Any], Any]]
) -> List[Dict[str, Any]]:
    """
    Aplica funciones de limpieza a campos específicos en una lista de registros.

    :param records: Lista de diccionarios con los datos
    :param field_cleaners: Diccionario {nombre_campo: función_limpieza}
    :return: Lista de registros con datos limpios

    Ejemplo de uso:
        cleaners = {
            'first_name': clean_name_field,
            'email': clean_email_field,
            'phone': clean_numeric_field,
        }
        cleaned_records = apply_field_cleaners(records, cleaners)
    """
    if not isinstance(records, list):
        return records

    for record in records:
        for field_name, cleaner_func in field_cleaners.items():
            if field_name in record:
                record[field_name] = cleaner_func(record[field_name])

    return records


# Convierte un JSON a una Lista
def clean_json_to_list(value: Any) -> List:
    """
    Convierte un string JSON a lista.
    Útil para bank_accounts y represents_company.
    """
    if not value:
        return []
    try:
        # Si ya es una lista (por algún proceso previo), se retorna
        if isinstance(value, list):
            return value
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


def clean_address_custom(value: Any) -> str:
    """
    Específico para direcciones: debe ser menos restrictiva que el nombre.
    """
    if not value or not isinstance(value, str):
        return value

    # En direcciones, es mejor solo quitar caracteres de control y limpiar espacios
    # No uses re.sub con una lista de permitidos a menos que sea estrictamente necesario.
    cleaned = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", value)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def apply_field_cleaners(
    records: List[Dict[str, Any]], field_cleaners: Dict[str, Callable[[Any], Any]]
) -> List[Dict[str, Any]]:
    """
    Recorre una lista de diccionarios (filas de la DB) y aplica
    una función de limpieza específica a los campos indicados.
    """
    if not isinstance(records, list):
        return records

    for record in records:
        for field_name, cleaner_func in field_cleaners.items():
            if field_name in record:
                # Aplicamos la función (ej. clean_address_custom) al valor actual
                record[field_name] = cleaner_func(record[field_name])

    return records


def clean_website_field(value: Any) -> Optional[str]:
    if not value or not isinstance(value, str):
        return None

    # 1. Limpieza inicial: eliminamos espacios y convertimos a minúsculas
    value = value.strip().lower()

    # 2. Manejo de guiones extraños (como '---') o comas
    # Reemplazamos comas por puntos (error común similar al email)
    value = value.replace(",", ".")

    # Si el valor son solo guiones o símbolos, lo descartamos de inmediato
    if re.match(r"^[-\s]+$", value):
        return None

    # 3. Expresión Regular para Website
    # Explicación:
    # ^(https?:\/\/)? -> Opcional: http:// o https://
    # (www\.)?        -> Opcional: www.
    # [a-z0-9-]+       -> Nombre del dominio (letras, números y guiones)
    # (\.[a-z0-9-]+)* -> Otros subdominios opcionales (ej. .com, .org)
    # \.[a-z]{2,}      -> Extensión final obligatoria (mínimo 2 letras, ej. .cu, .net)
    # (\/.*)?          -> Opcional: rutas después del dominio (ej. /inicio)

    website_pattern = (
        r"^(https?:\/\/)?(www\.)?[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}(\/.*)?$"
    )

    match = re.match(website_pattern, value)

    if match:
        # Si es válido, lo devolvemos limpio
        return value

    return None


def clean_phone_field(value: Any) -> Optional[str]:
    """
    Limpia campos de número telefónico.
    - Permite '+' al inicio (código de país)
    - Ignora '(', ')', '-', '.', espacios entre números, sin perder los dígitos
    - Si aparece '/', ';' o ',', descarta todo lo que viene después
    - Si el primer bloque de dígitos ya tiene 7+ dígitos (número completo) y
      le sigue otro bloque separado por espacio, ese bloque se trata como
      extensión (ej. "72043072 150" -> "72043072-150")
    - Si aparece 'ext' seguido de números, los conserva unidos con '-'
    - Si 'ext' no tiene números después, se elimina junto con todo lo demás
    - Retorna None si no hay contenido numérico significativo
    """
    if not value or not isinstance(value, str):
        return None

    value = value.strip()

    # 1. Separar extensión explícita ('ext' seguido o no de números)
    ext_match = re.search(r"ext[^\d]*(\d+)?", value, re.IGNORECASE)
    extension = None
    if ext_match:
        extension = ext_match.group(1)
        value = value[: ext_match.start()]

    # 2. Cortar todo lo que venga después de ';', '/' o ','
    value = re.split(r"[;/,]", value)[0]

    # 3. Detectar '+' inicial (código de país) antes de limpiar
    has_plus = value.strip().startswith("+")

    # 4. Separar por espacios para detectar si el primer bloque ya es un
    #    número completo (7+ dígitos) y lo que sigue es una extensión implícita
    parts = value.split()
    if not extension and len(parts) > 1:
        first_block_digits = re.sub(r"\D", "", parts[0])
        if len(first_block_digits) >= 7:
            rest_digits = re.sub(r"\D", "", " ".join(parts[1:]))
            if rest_digits:
                extension = rest_digits
            value = parts[0]

    # 5. Quedarnos solo con los dígitos del valor base
    digits_only = re.sub(r"\D", "", value)

    if not digits_only or len(digits_only) < 5:
        return None

    result = ("+" if has_plus else "") + digits_only
    if extension:
        result = f"{result}-{extension}"

    return result


def clean_quotes_field(value: Any) -> str:
    """
    Reemplaza comillas dobles por comillas simples para evitar
    conflictos de escape al serializar a JSON.
    Útil para nombres de tiendas/empresas con apodos entre comillas.
    """
    if not isinstance(value, str) or not value:
        return value

    cleaned = value.replace('"', "'")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def clean_iban_field(value: Any) -> Optional[str]:
    """
    Limpieza y validación básica de campos IBAN.
    - Normaliza caracteres Unicode ocultos
    - Elimina espacios, guiones y separadores visuales
    - Descarta valores que sean solo guiones o símbolos (ej. '---')
    - Valida formato básico: 2 letras país + 2 dígitos + hasta 30 alfanuméricos
    - Retorna None si no cumple el formato
    """
    if not value or not isinstance(value, str):
        return None

    # Normalizar Unicode oculto (elimina \xa0, espacios raros, etc.)
    value = unicodedata.normalize("NFKC", value)
    value = value.strip()

    # Descartar valores que son solo guiones, espacios o símbolos
    if re.match(r"^[-\s\W]+$", value):
        return None

    # Eliminar separadores visuales típicos del IBAN (espacios y guiones)
    value = re.sub(r"[\s\-]", "", value)

    # Convertir a mayúsculas (estándar IBAN)
    value = value.upper()

    # Validar que sea solo ASCII alfanumérico (descarta acentos, símbolos raros)
    if not value.isascii() or not value.isalnum():
        return None

    # Validar formato básico: 2 letras + 2 dígitos + 11 a 30 alfanuméricos
    if not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$", value):
        return None

    return value
