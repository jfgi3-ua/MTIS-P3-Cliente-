"""Servicios SOAP del cliente MTIS.

Este módulo encapsula toda la lógica necesaria para invocar el flujo SOAP de
Empleados publicado por Mule. Su responsabilidad principal es transformar una
acción de alto nivel del cliente (por ejemplo, "consultar empleado") en una
petición HTTP SOAP válida.

La interfaz gráfica NO debería construir XML SOAP directamente, porque esa
responsabilidad pertenece a la capa de servicios. De este modo, mantenemos una
separación clara entre:
- presentación (Tkinter)
- comunicación SOAP (este módulo)
"""

from __future__ import annotations

from typing import Any
from xml.sax.saxutils import escape

from config import SOAP_EMPLEADOS_URL, SOAP_WSKEY_DEFAULT
from services.http_client import HttpClient


# Namespace definido por el contrato WSDL del servicio Empleados.
SOAP_NAMESPACE = "http://www.example.org/Empleados/"

# Base de las cabeceras SOAPAction publicadas en el binding del WSDL.
SOAP_ACTION_BASE = "http://www.example.org/Empleados/"


def _xml_escape(value: Any) -> str:
    """Escapar texto para que sea seguro dentro de un XML.

    Ejemplo:
    - "&"  -> "&amp;"
    - "<"  -> "&lt;"
    - ">"  -> "&gt;"

    Esto evita romper el XML si el usuario introduce caracteres especiales
    en campos como nombre, email o contraseña.
    """
    return escape(str(value))


def _bool_to_soap(value: bool) -> str:
    """Convertir un booleano Python al formato textual esperado en SOAP."""
    return "true" if value else "false"


def _build_soap_headers(soap_action: str) -> dict[str, str]:
    """Construir las cabeceras HTTP necesarias para una llamada SOAP 1.1.

    Content-Type:
    - indica que el cuerpo enviado es XML SOAP

    SOAPAction:
    - identifica la operación concreta que se desea invocar en el servicio
    """
    return {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": soap_action,
    }


def _wrap_soap_envelope(operation_xml: str) -> str:
    """Envolver el XML de una operación dentro de un SOAP Envelope estándar.

    SOAP requiere que el mensaje viaje dentro de un Envelope. La operación
    concreta se inserta en el Body.
    """
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:emp="{SOAP_NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
        {operation_xml}
    </soapenv:Body>
</soapenv:Envelope>"""


def _build_employee_xml(employee_data: dict[str, Any]) -> str:
    """Construir el fragmento XML del empleado dentro del nodo <in>.

    Este fragmento se reutiliza tanto para:
    - nuevoEmpleado
    - modificarEmpleado

    La estructura se ajusta al tipo complejo Empleado definido en el WSDL.
    """
    return f"""
<in>
    <nifnie>{_xml_escape(employee_data["nifnie"])}</nifnie>
    <nombreApellidos>{_xml_escape(employee_data["nombreApellidos"])}</nombreApellidos>
    <email>{_xml_escape(employee_data["email"])}</email>
    <naf>{_xml_escape(employee_data["naf"])}</naf>
    <iban>{_xml_escape(employee_data["iban"])}</iban>
    <idNivel>{_xml_escape(employee_data["idNivel"])}</idNivel>
    <usuario>{_xml_escape(employee_data["usuario"])}</usuario>
    <password>{_xml_escape(employee_data["password"])}</password>
    <valido>{_bool_to_soap(bool(employee_data["valido"]))}</valido>
</in>
""".strip()


def _send_soap_request(soap_action: str, operation_xml: str) -> tuple[int, str]:
    """Enviar una petición SOAP al endpoint de Empleados.

    Flujo interno:
    1. Se construye el Envelope SOAP completo.
    2. Se generan las cabeceras HTTP adecuadas.
    3. Se realiza un POST al endpoint del flujo SOAP de Mule.
    4. Se devuelve el código HTTP y el cuerpo textual de la respuesta.

    La respuesta se devuelve como texto para que la capa de interfaz pueda:
    - mostrarla tal cual
    - formatearla visualmente
    - o incluso parsearla si necesita extraer datos
    """
    envelope = _wrap_soap_envelope(operation_xml)

    response = HttpClient.post(
        SOAP_EMPLEADOS_URL,
        headers=_build_soap_headers(soap_action),
        data=envelope,
    )

    return response.status_code, response.text


def nuevo_empleado(employee_data: dict[str, Any], wskey: str = SOAP_WSKEY_DEFAULT) -> tuple[int, str]:
    """Invocar la operación SOAP nuevoEmpleado."""
    operation_xml = f"""
<emp:nuevoEmpleado>
    <WSKey>{_xml_escape(wskey)}</WSKey>
    {_build_employee_xml(employee_data)}
</emp:nuevoEmpleado>
""".strip()

    return _send_soap_request(
        soap_action=f"{SOAP_ACTION_BASE}nuevoEmpleado",
        operation_xml=operation_xml,
    )


def consultar_empleado(nifnie: str, wskey: str = SOAP_WSKEY_DEFAULT) -> tuple[int, str]:
    """Invocar la operación SOAP consultarEmpleado usando el NIF/NIE como clave."""
    operation_xml = f"""
<emp:consultarEmpleado>
    <WSKey>{_xml_escape(wskey)}</WSKey>
    <in>{_xml_escape(nifnie)}</in>
</emp:consultarEmpleado>
""".strip()

    return _send_soap_request(
        soap_action=f"{SOAP_ACTION_BASE}consultarEmpleado",
        operation_xml=operation_xml,
    )


def consultar_todos_empleados(wskey: str = SOAP_WSKEY_DEFAULT) -> tuple[int, str]:
    """Invocar la operación SOAP consultarTodosEmpleados."""
    operation_xml = f"""
<emp:consultarTodosEmpleados>
    <WSKey>{_xml_escape(wskey)}</WSKey>
</emp:consultarTodosEmpleados>
""".strip()

    return _send_soap_request(
        soap_action=f"{SOAP_ACTION_BASE}consultarTodosEmpleados",
        operation_xml=operation_xml,
    )


def modificar_empleado(employee_data: dict[str, Any], wskey: str = SOAP_WSKEY_DEFAULT) -> tuple[int, str]:
    """Invocar la operación SOAP modificarEmpleado."""
    operation_xml = f"""
<emp:modificarEmpleado>
    <WSKey>{_xml_escape(wskey)}</WSKey>
    {_build_employee_xml(employee_data)}
</emp:modificarEmpleado>
""".strip()

    return _send_soap_request(
        soap_action=f"{SOAP_ACTION_BASE}modificarEmpleado",
        operation_xml=operation_xml,
    )


def borrar_empleado(nifnie: str, wskey: str = SOAP_WSKEY_DEFAULT) -> tuple[int, str]:
    """Invocar la operación SOAP borrarEmpleado usando el NIF/NIE."""
    operation_xml = f"""
<emp:borrarEmpleado>
    <WSKey>{_xml_escape(wskey)}</WSKey>
    <in>{_xml_escape(nifnie)}</in>
</emp:borrarEmpleado>
""".strip()

    return _send_soap_request(
        soap_action=f"{SOAP_ACTION_BASE}borrarEmpleado",
        operation_xml=operation_xml,
    )