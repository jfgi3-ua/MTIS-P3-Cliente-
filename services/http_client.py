"""Cliente HTTP reutilizable para centralizar llamadas externas.

Este módulo encapsula el uso de `requests` para que la aplicación tenga un
punto único desde el que lanzar peticiones HTTP. Así, si en el futuro se desea
modificar timeouts, trazas, cabeceras comunes o gestión de errores, bastará con
hacerlo aquí y no en cada pestaña de la interfaz.
"""

from __future__ import annotations

from typing import Any

import requests


class HttpClient:
    """Fachada estática muy ligera sobre la librería `requests`.

    Se ha optado por métodos estáticos porque, de momento, el cliente no necesita
    mantener estado interno (sesiones, tokens renovables, cookies, etc.).
    Si más adelante el proyecto creciera, podría evolucionarse a una clase con
    instancia y configuración inyectable.
    """

    @staticmethod
    def get(
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None
    ) -> requests.Response:
        """Lanzar una petición GET y devolver el objeto Response completo.

        Se devuelve `Response` en lugar de solo el cuerpo para conservar acceso a:
        - código de estado HTTP
        - cabeceras
        - texto o JSON de respuesta
        - información útil para depuración
        """
        return requests.get(url, headers=headers, params=params, timeout=15)

    @staticmethod
    def post(
        url: str,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
        data: str | None = None
    ) -> requests.Response:
        """Lanzar una petición POST.

        Se soportan dos modos de envío para cubrir los dos casos más habituales:
        - `json_data`: para servicios REST que esperan JSON.
        - `data`: para enviar texto plano, XML o SOAP Envelope serializado.
        """
        return requests.post(url, headers=headers, json=json_data, data=data, timeout=15)

    @staticmethod
    def put(
        url: str,
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None
    ) -> requests.Response:
        """Lanzar una petición PUT, usada normalmente para actualizaciones completas."""
        return requests.put(url, headers=headers, json=json_data, timeout=15)

    @staticmethod
    def delete(url: str, headers: dict[str, str] | None = None) -> requests.Response:
        """Lanzar una petición DELETE para eliminar recursos remotos."""
        return requests.delete(url, headers=headers, timeout=15)
