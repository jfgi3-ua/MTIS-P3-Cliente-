"""Funciones auxiliares de formateo para la interfaz.

Este módulo concentra utilidades de presentación reutilizables entre pestañas.
Su objetivo es que todas las salidas visuales del cliente sigan un formato
homogéneo, algo especialmente útil de cara a una evaluación donde interesa que
las respuestas sean rápidas de leer y comparar.
"""

from __future__ import annotations

from datetime import datetime
import json
from xml.dom import minidom


def current_timestamp_text() -> str:
    """Devolver la fecha y hora actual en un formato legible para la UI."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def _looks_like_xml(text: str) -> bool:
    """Determinar heurísticamente si una cadena parece XML.

    No es una validación formal; solo evita intentar parsear como XML textos que
    claramente no lo son.
    """
    stripped = text.lstrip()
    return stripped.startswith("<") and stripped.endswith(">")


def pretty_format_payload(body: str) -> str:
    """Intentar formatear automáticamente JSON o XML.

    Estrategia:
    1. Si el cuerpo está vacío, se devuelve un literal explicativo.
    2. Si es JSON válido, se sangra con indentación legible.
    3. Si parece XML y se puede parsear, se aplica pretty-print XML.
    4. Si nada de lo anterior aplica, se devuelve el texto tal cual.
    """
    stripped_body = body.strip()

    if not stripped_body:
        return "<respuesta vacía>"

    try:
        parsed_json = json.loads(stripped_body)
        return json.dumps(parsed_json, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        pass

    if _looks_like_xml(stripped_body):
        try:
            parsed_xml = minidom.parseString(stripped_body.encode("utf-8"))
            pretty_xml = parsed_xml.toprettyxml(indent="  ")

            # minidom suele introducir líneas en blanco extra. Se filtran para
            # que el resultado final sea más compacto y profesional.
            return "\n".join(line for line in pretty_xml.splitlines() if line.strip())
        except Exception:
            pass

    return stripped_body


def build_response_report(
    operation: str,
    status_code: int,
    body: str,
    extra_lines: list[str] | None = None,
) -> str:
    """Construir un bloque homogéneo de salida para respuestas correctas o erróneas.

    El campo `Resultado` no depende de semántica funcional avanzada; se limita a
    clasificar la respuesta usando el código HTTP recibido.
    """
    result_text = "OK" if 200 <= status_code < 300 else "ERROR"

    lines = [
        f"Operación: {operation}",
        f"Fecha/hora: {current_timestamp_text()}",
        f"Resultado: {result_text}",
        f"HTTP: {status_code}",
    ]

    if extra_lines:
        lines.extend(extra_lines)

    lines.extend([
        "",
        "-" * 80,
        "",
        pretty_format_payload(body),
    ])

    return "\n".join(lines)


def build_validation_error_report(detail: str) -> str:
    """Construir un mensaje homogéneo para errores detectados en cliente."""
    return "\n".join([
        "Operación: VALIDACIÓN DE FORMULARIO",
        f"Fecha/hora: {current_timestamp_text()}",
        "Resultado: ERROR DE CLIENTE",
        "",
        detail,
    ])



def build_exception_report(
    operation: str,
    exception: Exception,
    extra_lines: list[str] | None = None,
) -> str:
    """Construir una salida homogénea para excepciones de red o ejecución.

    Este formato ayuda mucho cuando la petición ni siquiera alcanza una respuesta
    HTTP normal: timeouts, conexión rechazada, DNS, etc.
    """
    lines = [
        f"Operación: {operation}",
        f"Fecha/hora: {current_timestamp_text()}",
        "Resultado: EXCEPCIÓN DE CLIENTE",
    ]

    if extra_lines:
        lines.extend(extra_lines)

    lines.extend([
        "",
        "Detalle técnico:",
        str(exception),
    ])

    return "\n".join(lines)
