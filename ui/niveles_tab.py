"""Pestaña REST de Niveles.

Esta pestaña implementa un pequeño cliente CRUD para el flujo REST de Niveles.

Responsabilidades de esta clase:
- recoger datos introducidos por el usuario
- validarlos mínimamente en cliente
- invocar la capa de servicios REST
- mostrar de forma legible la respuesta devuelta por Mule
- rellenar automáticamente la descripción tras una consulta exitosa

No se ocupa de la lógica HTTP en sí misma. Esa parte permanece separada en
services.rest_service para mantener una arquitectura simple y clara.
"""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from config import OUTPUT_BG, OUTPUT_FG, OUTPUT_FONT, OUTPUT_INSERT, REST_WSKEY_DEFAULT
from services.rest_service import (
    borrar_nivel,
    consultar_nivel,
    crear_nivel,
    modificar_nivel,
)
from utils.formatters import (
    build_exception_report,
    build_response_report,
    build_validation_error_report,
)


class NivelesTab:
    """Encapsula la construcción y el comportamiento de la pestaña REST Niveles."""

    def __init__(self, parent: ttk.Frame) -> None:
        """Guardar el contenedor padre e inicializar el estado de la pestaña."""
        self.parent = parent
        self.wskey_var = tk.StringVar(value=REST_WSKEY_DEFAULT)
        self.nivel_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.output_text: ScrolledText | None = None
        self._build()

    def _build(self) -> None:
        """Construir todos los widgets visibles de la pestaña."""
        ttk.Label(
            self.parent,
            text="REST Niveles - Cliente CRUD",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            self.parent,
            text=(
                "Permite probar el CRUD completo del flujo REST de Niveles con "
                "una salida homogénea y legible para la evaluación."
            )
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        config_frame = ttk.LabelFrame(
            self.parent,
            text="Configuración REST",
            padding=10,
            style="Section.TLabelframe"
        )
        config_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(config_frame, text="WSKey:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(config_frame, textvariable=self.wskey_var, width=40).grid(row=0, column=1, sticky="ew")
        config_frame.columnconfigure(1, weight=1)

        form_frame = ttk.LabelFrame(
            self.parent,
            text="Datos del nivel",
            padding=10,
            style="Section.TLabelframe"
        )
        form_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Nivel:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(0, 10))
        ttk.Entry(form_frame, textvariable=self.nivel_var, width=20).grid(row=0, column=1, sticky="w", pady=(0, 10))

        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(form_frame, textvariable=self.descripcion_var, width=60).grid(row=1, column=1, sticky="ew")
        form_frame.columnconfigure(1, weight=1)

        actions_frame = ttk.LabelFrame(
            self.parent,
            text="Acciones",
            padding=10,
            style="Section.TLabelframe"
        )
        actions_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(actions_frame, text="Crear", style="Action.TButton", command=self._on_crear).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(actions_frame, text="Consultar", style="Action.TButton", command=self._on_consultar).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions_frame, text="Modificar", style="Action.TButton", command=self._on_modificar).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(actions_frame, text="Borrar", style="Action.TButton", command=self._on_borrar).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(actions_frame, text="Limpiar formulario", style="Action.TButton", command=self._on_limpiar_formulario).grid(row=0, column=4)

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
        """Leer y validar la WSKey REST introducida por el usuario."""
        wskey = self.wskey_var.get().strip()
        if not wskey:
            self._set_output(
                build_validation_error_report("Debes introducir una WSKey REST válida.")
            )
            return None
        return wskey

    def _get_nivel_value(self) -> int | None:
        """Leer y validar el valor del campo 'nivel'."""
        raw_value = self.nivel_var.get().strip()

        if not raw_value:
            self._set_output(
                build_validation_error_report(
                    "Debes introducir un valor para el campo 'nivel'."
                )
            )
            return None

        try:
            nivel = int(raw_value)
        except ValueError:
            self._set_output(
                build_validation_error_report(
                    "El campo 'nivel' debe ser un número entero."
                )
            )
            return None

        if nivel < 0:
            self._set_output(
                build_validation_error_report(
                    "El campo 'nivel' no puede ser negativo."
                )
            )
            return None

        return nivel

    def _get_descripcion_value(self) -> str | None:
        """Leer y validar el campo 'descripcion'."""
        descripcion = self.descripcion_var.get().strip()
        if not descripcion:
            self._set_output(
                build_validation_error_report(
                    "Debes introducir una descripción no vacía."
                )
            )
            return None
        return descripcion

    def _populate_form_from_consultar_response(self, body: str) -> None:
        """Intentar rellenar la descripción a partir de la respuesta JSON.

        Esta pequeña mejora aproxima la UX de REST Niveles a la pestaña SOAP de
        Empleados: primero se consulta, luego el formulario queda listo para
        modificar sin tener que reescribir toda la información manualmente.
        """
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return

        data = payload.get("data")
        if not isinstance(data, dict):
            return

        if "nivel" in data:
            self.nivel_var.set(str(data["nivel"]))
        if "descripcion" in data:
            self.descripcion_var.set(str(data["descripcion"]))

    def _on_crear(self) -> None:
        """Gestionar la acción de crear un nuevo nivel."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        nivel = self._get_nivel_value()
        if nivel is None:
            return

        descripcion = self._get_descripcion_value()
        if descripcion is None:
            return

        try:
            status_code, body = crear_nivel(nivel, descripcion, wskey)
            report = build_response_report("CREAR NIVEL", status_code, body)
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("CREAR NIVEL", exc)
            self._set_output(report)

    def _on_consultar(self) -> None:
        """Gestionar la acción de consultar un nivel concreto."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        nivel = self._get_nivel_value()
        if nivel is None:
            return

        try:
            status_code, body = consultar_nivel(nivel, wskey)
            report = build_response_report("CONSULTAR NIVEL", status_code, body)
            self._set_output(report)
            self._populate_form_from_consultar_response(body)
        except Exception as exc:
            report = build_exception_report("CONSULTAR NIVEL", exc)
            self._set_output(report)

    def _on_modificar(self) -> None:
        """Gestionar la acción de modificar un nivel existente."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        nivel = self._get_nivel_value()
        if nivel is None:
            return

        descripcion = self._get_descripcion_value()
        if descripcion is None:
            return

        try:
            status_code, body = modificar_nivel(nivel, descripcion, wskey)
            report = build_response_report("MODIFICAR NIVEL", status_code, body)
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("MODIFICAR NIVEL", exc)
            self._set_output(report)

    def _on_borrar(self) -> None:
        """Gestionar la acción de borrar un nivel existente."""
        wskey = self._get_wskey_value()
        if wskey is None:
            return

        nivel = self._get_nivel_value()
        if nivel is None:
            return

        try:
            status_code, body = borrar_nivel(nivel, wskey)
            report = build_response_report("BORRAR NIVEL", status_code, body)
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("BORRAR NIVEL", exc)
            self._set_output(report)

    def _on_limpiar_formulario(self) -> None:
        """Restablecer los campos de entrada y limpiar la salida."""
        self.nivel_var.set("")
        self.descripcion_var.set("")
        self._clear_output()
