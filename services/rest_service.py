"""Funciones de alto nivel para invocar flujos REST de Mule.

La idea de este módulo es traducir acciones del cliente
("lanzar proceso NENV", "crear nivel", "borrar nivel") a llamadas HTTP reales.

Esto permite que la capa de interfaz trabaje con operaciones semánticas y no
tenga que preocuparse por:
- construir URLs manualmente
- decidir cabeceras
- preparar cuerpos JSON
- llamar directamente a requests

En otras palabras:
- la UI pide "haz esta operación"
- este módulo decide "cómo se llama por HTTP"
"""

from __future__ import annotations

from services.http_client import HttpClient
from config import (
    PROCESO_NENV_URL,
    PROCESO_NUNVTS_URL,
    REST_NIVELES_BASE_URL,
    REST_WSKEY_DEFAULT,
)


def _build_rest_headers(wskey: str = REST_WSKEY_DEFAULT) -> dict[str, str]:
    """Construir las cabeceras comunes de las llamadas REST.

    En tu práctica, los endpoints REST validan la cabecera WSKey. Centralizar
    su creación aquí evita duplicar este bloque en cada función y reduce el
    riesgo de inconsistencias futuras.

    Además, el parámetro `wskey` permite que el valor no quede rígidamente
    fijado a la constante por defecto. Esto resulta útil en el cliente cuando
    se desea probar manualmente una clave distinta, tal y como ya ocurre en la
    pestaña SOAP de Empleados.
    """
    return {
        "WSKey": wskey
    }


def lanzar_proceso_nenv(wskey: str = REST_WSKEY_DEFAULT) -> tuple[int, str]:
    """Invocar el flujo NENV y devolver código HTTP + cuerpo textual.

    Aunque esta operación no necesite un formulario de entrada, sí puede ser
    interesante variar la WSKey desde la interfaz para hacer pruebas de éxito
    y error de forma controlada.
    """
    response = HttpClient.get(
        PROCESO_NENV_URL,
        headers=_build_rest_headers(wskey)
    )
    return response.status_code, response.text


def lanzar_proceso_nunvts(email: str, wskey: str = REST_WSKEY_DEFAULT) -> tuple[int, str]:
    """Invocar el flujo NUNVTS enviando el email como query param.

    Requests serializa automáticamente el diccionario `params` como query
    string, generando una URL final del estilo:
    http://127.0.0.1:9094/procesoNUNVTS?email=destino@dominio
    """
    params = {
        "email": email
    }

    response = HttpClient.get(
        PROCESO_NUNVTS_URL,
        headers=_build_rest_headers(wskey),
        params=params
    )
    return response.status_code, response.text


def crear_nivel(nivel: int, descripcion: str, wskey: str = REST_WSKEY_DEFAULT) -> tuple[int, str]:
    """Crear un nuevo nivel mediante POST.

    Se envía un JSON con la estructura esperada por el flujo REST:
    {
        "nivel": 6,
        "descripcion": "Acceso especial"
    }
    """
    payload = {
        "nivel": nivel,
        "descripcion": descripcion
    }

    response = HttpClient.post(
        REST_NIVELES_BASE_URL,
        headers=_build_rest_headers(wskey),
        json_data=payload
    )
    return response.status_code, response.text


def consultar_nivel(nivel: int, wskey: str = REST_WSKEY_DEFAULT) -> tuple[int, str]:
    """Consultar un nivel concreto mediante GET sobre /niveles/{nivel}."""
    url = f"{REST_NIVELES_BASE_URL}/{nivel}"

    response = HttpClient.get(
        url,
        headers=_build_rest_headers(wskey)
    )
    return response.status_code, response.text


def modificar_nivel(nivel: int, descripcion: str, wskey: str = REST_WSKEY_DEFAULT) -> tuple[int, str]:
    """Modificar un nivel existente mediante PUT.

    El contrato REST exige coherencia entre:
    - el nivel indicado en la URL
    - el nivel incluido en el body JSON

    Por eso se usa el mismo valor `nivel` en ambos sitios.
    """
    url = f"{REST_NIVELES_BASE_URL}/{nivel}"

    payload = {
        "nivel": nivel,
        "descripcion": descripcion
    }

    response = HttpClient.put(
        url,
        headers=_build_rest_headers(wskey),
        json_data=payload
    )
    return response.status_code, response.text


def borrar_nivel(nivel: int, wskey: str = REST_WSKEY_DEFAULT) -> tuple[int, str]:
    """Eliminar un nivel existente mediante DELETE sobre /niveles/{nivel}."""
    url = f"{REST_NIVELES_BASE_URL}/{nivel}"

    response = HttpClient.delete(
        url,
        headers=_build_rest_headers(wskey)
    )
    return response.status_code, response.text
