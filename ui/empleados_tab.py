"""Pestaña SOAP de Empleados.

Esta pestaña implementa un cliente gráfico para probar el CRUD SOAP de
Empleados publicado por Mule.

Su responsabilidad es:
- recoger datos del formulario
- validarlos mínimamente en cliente
- invocar la capa de servicios SOAP
- mostrar la respuesta XML de forma legible con un formato homogéneo
- rellenar automáticamente el formulario cuando una consulta devuelve datos

La construcción del XML SOAP NO se hace aquí. Esa responsabilidad pertenece a
services.soap_service.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import xml.etree.ElementTree as ET

from config import OUTPUT_BG, OUTPUT_FG, OUTPUT_FONT, OUTPUT_INSERT, SOAP_WSKEY_DEFAULT
from services.soap_service import (
    borrar_empleado,
    consultar_empleado,
    consultar_todos_empleados,
    modificar_empleado,
    nuevo_empleado,
)
from utils.formatters import (
    build_exception_report,
    build_response_report,
    build_validation_error_report,
)


class EmpleadosTab:
    """Encapsular la interfaz y el comportamiento de la pestaña SOAP Empleados."""

    def __init__(self, parent: ttk.Frame) -> None:
        """Guardar el contenedor padre e inicializar el estado visual."""
        self.parent = parent
        self.wskey_var = tk.StringVar(value=SOAP_WSKEY_DEFAULT)
        self.nifnie_var = tk.StringVar()
        self.nombre_apellidos_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.naf_var = tk.StringVar()
        self.iban_var = tk.StringVar()
        self.id_nivel_var = tk.StringVar()
        self.usuario_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.valido_var = tk.BooleanVar(value=True)
        self.output_text: ScrolledText | None = None
        self._build()

    def _build(self) -> None:
        """Construir la estructura visual completa de la pestaña."""
        ttk.Label(
            self.parent,
            text="SOAP Empleados - Cliente CRUD",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            self.parent,
            text=(
                "Permite probar todas las operaciones SOAP del servicio Empleados "
                "y reutilizar la consulta para posteriores modificaciones."
            )
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        credentials_frame = ttk.LabelFrame(
            self.parent,
            text="Configuración SOAP",
            padding=10,
            style="Section.TLabelframe"
        )
        credentials_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(credentials_frame, text="WSKey:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(credentials_frame, textvariable=self.wskey_var, width=40).grid(row=0, column=1, sticky="ew")
        credentials_frame.columnconfigure(1, weight=1)

        form_frame = ttk.LabelFrame(
            self.parent,
            text="Datos del empleado",
            padding=10,
            style="Section.TLabelframe"
        )
        form_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="NIF/NIE:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.nifnie_var, width=25).grid(row=0, column=1, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Nombre y apellidos:").grid(row=0, column=2, sticky="w", padx=(20, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.nombre_apellidos_var, width=40).grid(row=0, column=3, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.email_var, width=25).grid(row=1, column=1, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="NAF:").grid(row=1, column=2, sticky="w", padx=(20, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.naf_var, width=25).grid(row=1, column=3, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="IBAN:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.iban_var, width=30).grid(row=2, column=1, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="ID nivel:").grid(row=2, column=2, sticky="w", padx=(20, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.id_nivel_var, width=10).grid(row=2, column=3, sticky="w", pady=(0, 10))

        ttk.Label(form_frame, text="Usuario:").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.usuario_var, width=25).grid(row=3, column=1, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Password:").grid(row=3, column=2, sticky="w", padx=(20, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.password_var, width=25, show="*").grid(row=3, column=3, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Válido:").grid(row=4, column=0, sticky="w", padx=(0, 10))
        ttk.Checkbutton(form_frame, variable=self.valido_var).grid(row=4, column=1, sticky="w")

        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        actions_frame = ttk.LabelFrame(
            self.parent,
            text="Acciones",
            padding=10,
            style="Section.TLabelframe"
        )
        actions_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(actions_frame, text="Nuevo", style="Action.TButton", command=self._on_nuevo).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions_frame, text="Consultar", style="Action.TButton", command=self._on_consultar).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions_frame, text="Consultar todos", style="Action.TButton", command=self._on_consultar_todos).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(actions_frame, text="Modificar", style="Action.TButton", command=self._on_modificar).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(actions_frame, text="Borrar", style="Action.TButton", command=self._on_borrar).grid(row=0, column=4, padx=(0, 8))
        ttk.Button(actions_frame, text="Limpiar formulario", style="Action.TButton", command=self._on_limpiar_formulario).grid(row=0, column=5)

        output_frame = ttk.LabelFrame(
            self.parent,
            text="Salida",
            padding=10,
            style="Section.TLabelframe"
        )
        output_frame.grid(row=5, column=0, sticky="nsew")

        self.output_text = ScrolledText(
            output_frame,
            wrap="word",
            width=110,
            height=24,
            font=OUTPUT_FONT,
            bg=OUTPUT_BG,
            fg=OUTPUT_FG,
            insertbackground=OUTPUT_INSERT,
            relief="solid",
            borderwidth=1,
        )
        self.output_text.pack(fill="both", expand=True)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(5, weight=1)

    def _clear_output(self) -> None:
        """Borrar el contenido actual del área de salida."""
        if self.output_text is None:
            return
        self.output_text.delete("1.0", tk.END)

    def _set_output(self, text: str) -> None:
        """Sustituir por completo el contenido del área de salida."""
        if self.output_text is None:
            return
        self._clear_output()
        self.output_text.insert(tk.END, text)

    def _get_wskey_value(self) -> str | None:
        """Validar que la WSKey SOAP no esté vacía."""
        wskey = self.wskey_var.get().strip()
        if not wskey:
            self._set_output(
                build_validation_error_report("Debes introducir una WSKey SOAP válida.")
            )
            return None
        return wskey

    def _get_required_text(self, value: str, field_name: str) -> str | None:
        """Validar genéricamente que un campo de texto obligatorio no esté vacío."""
        stripped_value = value.strip()
        if not stripped_value:
            self._set_output(
                build_validation_error_report(
                    f"Debes introducir un valor para '{field_name}'."
                )
            )
            return None
        return stripped_value

    def _get_nifnie_value(self) -> str | None:
        """Obtener y validar el NIF/NIE del formulario."""
        return self._get_required_text(self.nifnie_var.get(), "NIF/NIE")

    def _get_id_nivel_value(self) -> int | None:
        """Obtener y validar el campo idNivel como entero no negativo."""
        raw_value = self.id_nivel_var.get().strip()

        if not raw_value:
            self._set_output(
                build_validation_error_report(
                    "Debes introducir un valor para 'ID nivel'."
                )
            )
            return None

        try:
            id_nivel = int(raw_value)
        except ValueError:
            self._set_output(
                build_validation_error_report(
                    "El campo 'ID nivel' debe ser un número entero."
                )
            )
            return None

        if id_nivel < 0:
            self._set_output(
                build_validation_error_report(
                    "El campo 'ID nivel' no puede ser negativo."
                )
            )
            return None

        return id_nivel

    def _build_employee_payload(self) -> dict[str, object] | None:
        """Construir el diccionario empleado a partir del formulario."""
        nifnie = self._get_required_text(self.nifnie_var.get(), "NIF/NIE")
        if nifnie is None:
            return None

        nombre_apellidos = self._get_required_text(self.nombre_apellidos_var.get(), "Nombre y apellidos")
        if nombre_apellidos is None:
            return None

        email = self._get_required_text(self.email_var.get(), "Email")
        if email is None:
            return None

        naf = self._get_required_text(self.naf_var.get(), "NAF")
        if naf is None:
            return None

        iban = self._get_required_text(self.iban_var.get(), "IBAN")
        if iban is None:
            return None

        id_nivel = self._get_id_nivel_value()
        if id_nivel is None:
            return None

        usuario = self._get_required_text(self.usuario_var.get(), "Usuario")
        if usuario is None:
            return None

        password = self._get_required_text(self.password_var.get(), "Password")
        if password is None:
            return None

        return {
            "nifnie": nifnie,
            "nombreApellidos": nombre_apellidos,
            "email": email,
            "naf": naf,
            "iban": iban,
            "idNivel": id_nivel,
            "usuario": usuario,
            "password": password,
            "valido": self.valido_var.get(),
        }

    def _local_name(self, tag: str) -> str:
        """Obtener el nombre local de un tag XML ignorando el namespace."""
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    def _find_first_descendant(self, root: ET.Element, local_name: str) -> ET.Element | None:
        """Buscar el primer descendiente cuyo nombre local coincida."""
        for element in root.iter():
            if self._local_name(element.tag) == local_name:
                return element
        return None

    def _find_text_in_subtree(self, root: ET.Element, local_name: str) -> str:
        """Buscar el texto del primer nodo descendiente con ese nombre local."""
        element = self._find_first_descendant(root, local_name)
        if element is None or element.text is None:
            return ""
        return element.text.strip()

    def _populate_form_from_consultar_response(self, body: str) -> None:
        """Intentar rellenar el formulario a partir de la respuesta SOAP."""
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            return

        out_element = self._find_first_descendant(root, "out")
        if out_element is None:
            return

        self.nifnie_var.set(self._find_text_in_subtree(out_element, "nifnie"))
        self.nombre_apellidos_var.set(self._find_text_in_subtree(out_element, "nombreApellidos"))
        self.email_var.set(self._find_text_in_subtree(out_element, "email"))
        self.naf_var.set(self._find_text_in_subtree(out_element, "naf"))
        self.iban_var.set(self._find_text_in_subtree(out_element, "iban"))
        self.id_nivel_var.set(self._find_text_in_subtree(out_element, "idNivel"))
        self.usuario_var.set(self._find_text_in_subtree(out_element, "usuario"))
        self.password_var.set(self._find_text_in_subtree(out_element, "password"))

        valido_text = self._find_text_in_subtree(out_element, "valido").lower()
        self.valido_var.set(valido_text in ("true", "1"))

    def _on_nuevo(self) -> None:
        """Gestionar la acción SOAP nuevoEmpleado."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        employee_data = self._build_employee_payload()
        if employee_data is None:
            return

        try:
            status_code, body = nuevo_empleado(employee_data, wskey)
            report = build_response_report("NUEVO EMPLEADO", status_code, body)
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("NUEVO EMPLEADO", exc)
            self._set_output(report)

    def _on_consultar(self) -> None:
        """Gestionar la acción SOAP consultarEmpleado."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        nifnie = self._get_nifnie_value()
        if nifnie is None:
            return

        try:
            status_code, body = consultar_empleado(nifnie, wskey)
            report = build_response_report("CONSULTAR EMPLEADO", status_code, body)
            self._set_output(report)
            self._populate_form_from_consultar_response(body)
        except Exception as exc:
            report = build_exception_report("CONSULTAR EMPLEADO", exc)
            self._set_output(report)

    def _on_consultar_todos(self) -> None:
        """Gestionar la acción SOAP consultarTodosEmpleados."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        try:
            status_code, body = consultar_todos_empleados(wskey)
            report = build_response_report("CONSULTAR TODOS LOS EMPLEADOS", status_code, body)
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("CONSULTAR TODOS LOS EMPLEADOS", exc)
            self._set_output(report)

    def _on_modificar(self) -> None:
        """Gestionar la acción SOAP modificarEmpleado."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        employee_data = self._build_employee_payload()
        if employee_data is None:
            return

        try:
            status_code, body = modificar_empleado(employee_data, wskey)
            report = build_response_report("MODIFICAR EMPLEADO", status_code, body)
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("MODIFICAR EMPLEADO", exc)
            self._set_output(report)

    def _on_borrar(self) -> None:
        """Gestionar la acción SOAP borrarEmpleado."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        nifnie = self._get_nifnie_value()
        if nifnie is None:
            return

        try:
            status_code, body = borrar_empleado(nifnie, wskey)
            report = build_response_report("BORRAR EMPLEADO", status_code, body)
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("BORRAR EMPLEADO", exc)
            self._set_output(report)

    def _on_limpiar_formulario(self) -> None:
        """Limpiar todos los campos del formulario, manteniendo la WSKey actual."""
        self.nifnie_var.set("")
        self.nombre_apellidos_var.set("")
        self.email_var.set("")
        self.naf_var.set("")
        self.iban_var.set("")
        self.id_nivel_var.set("")
        self.usuario_var.set("")
        self.password_var.set("")
        self.valido_var.set(True)
        self._clear_output()
