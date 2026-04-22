"""Servicios de monitorización para la Office 3 de Mule.

Este módulo encapsula el acceso de solo lectura a la base de datos local usada
por la práctica. La consola gráfica de Office 3 necesita consultar:
- el estado persistido actual de la oficina (`estadoOficina`)
- las últimas acciones aplicadas por los listeners JMS (`accionesOficina`)
- los errores recientes de los flujos del apartado 5 (`erroresFlujos`)

La lectura se hace directamente desde MySQL porque el apartado 5 no expone un
endpoint HTTP específico para monitorización. Centralizar aquí toda la lógica de
acceso a datos evita mezclar SQL dentro de la interfaz Tkinter.
"""

from __future__ import annotations

from typing import Any

from config import (
    DB_HOST,
    DB_NAME,
    DB_OFFICE_ID,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
    OFFICE3_MONITOR_ACTION_LIMIT,
    OFFICE3_MONITOR_ERROR_LIMIT,
)


def _resolve_mysql_driver() -> tuple[str, Any]:
    """Localizar un driver MySQL disponible sin forzar una dependencia rígida.

    Estrategia de resolución:
    1. Se intenta usar `mysql-connector-python`, que es la opción recomendada.
    2. Si no existe, se intenta `PyMySQL` como alternativa compatible.
    3. Si tampoco existe, se lanza un error claro con la acción correctiva.

    Esta aproximación permite que la aplicación arranque aunque el usuario aún
    no haya instalado el conector. El error solo aparecerá al abrir/refrescar la
    consola de monitorización, que es justo el punto en el que realmente se necesita.
    """
    try:
        import mysql.connector  # type: ignore
        return "mysql-connector-python", mysql.connector
    except ModuleNotFoundError:
        pass

    try:
        import pymysql  # type: ignore
        return "PyMySQL", pymysql
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "No se ha encontrado un conector MySQL para Python. "
            "Instala 'mysql-connector-python' (recomendado) con: "
            "pip install mysql-connector-python"
        ) from exc


def _open_connection() -> tuple[Any, Any, str]:
    """Abrir una conexión MySQL y devolver conexión, cursor diccionario y driver.

    Se devuelve el cursor en modo diccionario para que el resto del código pueda
    trabajar con nombres de columna legibles (`fila['temperatura_actual']`) en
    lugar de índices posicionales (`fila[1]`). Esto hace el código de la consola
    mucho más comprensible para mantenimiento futuro.
    """
    driver_name, driver_module = _resolve_mysql_driver()

    if driver_name == "mysql-connector-python":
        connection = driver_module.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )
        cursor = connection.cursor(dictionary=True)
        return connection, cursor, driver_name

    connection = driver_module.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=driver_module.cursors.DictCursor,
        autocommit=True,
    )
    cursor = connection.cursor()
    return connection, cursor, driver_name


def _run_select(query: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    """Ejecutar una consulta SELECT y devolver una lista de filas diccionario."""
    connection, cursor, _driver_name = _open_connection()
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return list(rows or [])
    finally:
        try:
            cursor.close()
        finally:
            connection.close()


def fetch_office3_state(office_id: int = DB_OFFICE_ID) -> dict[str, Any]:
    """Recuperar el estado persistido actual de la Office 3.

    Se consulta la tabla `estadoOficina`, que en tu implementación Mule actúa
    como fuente de verdad del estado actual de temperatura, iluminación y modos
    activos de actuación.
    """
    query = """
        SELECT office_id,
               temperatura_actual,
               iluminacion_actual,
               hvac_mode,
               hvac_target,
               light_mode,
               light_target,
               ciclos_estables,
               indice_perturbacion,
               fecha_hora
        FROM estadoOficina
        WHERE office_id = %s
    """
    rows = _run_select(query, (office_id,))

    if not rows:
        raise RuntimeError(
            f"No existe estadoOficina para office_id={office_id}. "
            "Comprueba que la extensión de BD de la práctica 3 esté aplicada."
        )

    return rows[0]


def fetch_recent_office3_actions(limit: int = OFFICE3_MONITOR_ACTION_LIMIT) -> list[dict[str, Any]]:
    """Obtener el histórico reciente de acciones ejecutadas sobre la Office 3.

    La tabla `accionesOficina` registra los cambios aplicados por los listeners
    HVAC y LIGHT cuando llegan comandos desde ActiveMQ. Esta consulta filtra por
    topic de origen de office3 para no mezclar acciones de otras oficinas.
    """
    query = """
        SELECT fecha_hora,
               topic_origen,
               tipo_variable,
               accion_realizada,
               valor_anterior,
               valor_nuevo
        FROM accionesOficina
        WHERE topic_origen LIKE %s
        ORDER BY fecha_hora DESC, id DESC
        LIMIT %s
    """
    return _run_select(query, ("building.office3.%", limit))


def fetch_recent_office3_errors(limit: int = OFFICE3_MONITOR_ERROR_LIMIT) -> list[dict[str, Any]]:
    """Obtener errores recientes vinculados a los flujos del apartado 5.

    En `erroresFlujos` se registran errores de todos los apartados. Aquí se
    filtran los asociados a los flujos cuyo nombre empieza por `apartado5-`.
    """
    query = """
        SELECT fecha_hora,
               flujo,
               operacion,
               mensaje_error,
               detalle_error
        FROM erroresFlujos
        WHERE flujo LIKE %s
        ORDER BY fecha_hora DESC, id DESC
        LIMIT %s
    """
    return _run_select(query, ("apartado5-%", limit))


def fetch_office3_monitor_snapshot() -> dict[str, Any]:
    """Construir una instantánea completa para la consola de monitorización.

    Se agrupan en una única estructura los tres bloques de información que la UI
    necesita refrescar de forma coordinada:
    - estado actual de la oficina
    - acciones recientes
    - errores recientes
    - nombre del driver MySQL usado para la conexión
    """
    _connection, _cursor, driver_name = _open_connection()
    # La conexión anterior solo se usa para identificar el driver resuelto. Se
    # cierra inmediatamente para mantener el resto de funciones simples y sin
    # estado compartido entre consultas.
    try:
        pass
    finally:
        try:
            _cursor.close()
        finally:
            _connection.close()

    return {
        "driver": driver_name,
        "state": fetch_office3_state(),
        "actions": fetch_recent_office3_actions(),
        "errors": fetch_recent_office3_errors(),
    }
