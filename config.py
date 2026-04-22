"""Configuración centralizada del cliente MTIS.

Concentrar aquí URLs, puertos, claves por defecto, propiedades visuales y la
configuración del monitor de Office 3 evita que dichos valores queden dispersos
por la aplicación. Esto simplifica el mantenimiento, hace más fácil la defensa
la práctica y reduce errores cuando cambian endpoints, credenciales o estilos.
"""

# -----------------------------------------------------------------------------
# Endpoints de integración
# -----------------------------------------------------------------------------

# Endpoint HTTP del flujo SOAP publicado por Mule para el servicio Empleados.
SOAP_EMPLEADOS_URL = "http://127.0.0.1:9091/empleados"

# Endpoint base del flujo REST de Niveles publicado por Mule.
REST_NIVELES_BASE_URL = "http://127.0.0.1:9092/niveles"

# Endpoint del flujo orquestado NENV (Notificar Empleados No Válidos).
PROCESO_NENV_URL = "http://127.0.0.1:9093/procesoNENV"

# Endpoint del flujo orquestado NUNVTS (Notificar Usuario No Válido en Todas las Salas).
PROCESO_NUNVTS_URL = "http://127.0.0.1:9094/procesoNUNVTS"

# -----------------------------------------------------------------------------
# Credenciales por defecto para pruebas locales
# -----------------------------------------------------------------------------

# Clave SOAP de desarrollo usada por defecto en las pruebas del cliente.
SOAP_WSKEY_DEFAULT = "SOAP-DEV-KEY-001"

# Clave REST de desarrollo usada por defecto en las pruebas del cliente.
REST_WSKEY_DEFAULT = "REST-DEV-KEY-001"

# -----------------------------------------------------------------------------
# Configuración de base de datos para la consola de monitorización Office 3
# -----------------------------------------------------------------------------

# Estos valores replican la configuración local usada en la práctica 3 de Mule.
# Se centralizan aquí porque la consola de monitorización necesita consultar el
# estado persistido de la oficina 3 y el histórico reciente de acciones/errores.
DB_HOST = "127.0.0.1"
DB_PORT = 3307
DB_NAME = "mtis"
DB_USER = "root"
DB_PASSWORD = "Jess89"
DB_OFFICE_ID = 3

# Valores por defecto del monitor gráfico de Office 3.
OFFICE3_MONITOR_DEFAULT_REFRESH_SECONDS = "3"
OFFICE3_MONITOR_ACTION_LIMIT = 12
OFFICE3_MONITOR_ERROR_LIMIT = 8

# -----------------------------------------------------------------------------
# Metadatos visuales de la aplicación
# -----------------------------------------------------------------------------

APP_TITLE = "Cliente MTIS - Práctica 3"
APP_SUBTITLE = (
    "Cliente unificado para probar SOAP Empleados, REST Niveles, los procesos "
    "NENV / NUNVTS y la consola de monitorización de Office 3 en MuleSoft."
)
APP_FOOTER = (
    "Entorno previsto: SOAP 9091 · REST 9092 · NENV 9093 · NUNVTS 9094 · "
    "Monitor Office 3 vía MySQL/ActiveMQ"
)
WINDOW_SIZE = "1280x860"
WINDOW_MIN_SIZE = (1160, 800)

# Fuente monoespaciada recomendada para mostrar respuestas HTTP/XML/JSON.
OUTPUT_FONT = ("Consolas", 10)

# -----------------------------------------------------------------------------
# Paleta visual corporativa suave
# -----------------------------------------------------------------------------

# La idea es usar una identidad basada en azul marino oscuro sin oscurecer toda
# la aplicación. Por eso el color intenso se reserva a acentos, cabeceras,
# botones y pestañas seleccionadas, mientras que el fondo de trabajo permanece
# claro para no perjudicar la legibilidad.
COLOR_APP_BG = "#EEF3F8"
COLOR_PANEL_BG = "#F7FAFD"
COLOR_NAVY_DARK = "#17324D"
COLOR_NAVY_MID = "#244A6A"
COLOR_NAVY_LIGHT = "#D6E1EC"
COLOR_NAVY_ACCENT = "#3D6B93"
COLOR_TEXT_MAIN = "#102235"
COLOR_TEXT_SOFT = "#41566B"
COLOR_TEXT_ON_DARK = "#FFFFFF"
COLOR_BORDER = "#90A7BE"

# Colores específicos de las áreas de salida de texto.
OUTPUT_BG = "#FBFDFF"
OUTPUT_FG = COLOR_TEXT_MAIN
OUTPUT_INSERT = COLOR_TEXT_MAIN
