"""Pestaña de interfaz para lanzar el proceso NENV.

Su misión es ofrecer al usuario una forma sencilla de invocar el flujo Mule
"Notificar Empleados No Válidos" y visualizar tanto el código HTTP como el
cuerpo devuelto por el servidor con un formato homogéneo.
"""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from config import OUTPUT_BG, OUTPUT_FG, OUTPUT_FONT, OUTPUT_INSERT
from services.rest_service import lanzar_proceso_nenv
from utils.formatters import build_exception_report, build_response_report


class NENVTab:
    """Encapsula la construcción y comportamiento de la pestaña NENV."""

    def __init__(self, parent: ttk.Frame) -> None:
        """Guardar el contenedor padre y construir los widgets de la pestaña."""
        self.parent = parent
        self.output_text: ScrolledText | None = None
        self._build()

    def _build(self) -> None:
        """Crear el contenido visual de la pestaña.

        El pulido visual se apoya en dos bloques bien diferenciados:
        - un bloque de acciones, que concentra los botones de operación
        - un bloque de salida, que enmarca la respuesta devuelta por Mule
        """
        ttk.Label(
            self.parent,
            text="Proceso NENV - Notificar Empleados No Válidos",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            self.parent,
            text=(
                "Lanza la orquestación completa sin parámetros de entrada y muestra "
                "el resultado final devuelto por Mule."
            )
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        actions_frame = ttk.LabelFrame(
            self.parent,
            text="Acciones",
            padding=10,
            style="Section.TLabelframe"
        )
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Button(
            actions_frame,
            text="Lanzar proceso NENV",
            style="Action.TButton",
            command=self._on_lanzar
        ).grid(row=0, column=0, padx=(0, 8))

        ttk.Button(
            actions_frame,
            text="Limpiar formulario",
            style="Action.TButton",
            command=self._on_limpiar_formulario
        ).grid(row=0, column=1)

        output_frame = ttk.LabelFrame(
            self.parent,
            text="Salida",
            padding=10,
            style="Section.TLabelframe"
        )
        output_frame.grid(row=3, column=0, sticky="nsew")

        self.output_text = ScrolledText(
            output_frame,
            wrap="word",
            width=110,
            height=26,
            font=OUTPUT_FONT,
            bg=OUTPUT_BG,
            fg=OUTPUT_FG,
            insertbackground=OUTPUT_INSERT,
            relief="solid",
            borderwidth=1,
        )
        self.output_text.pack(fill="both", expand=True)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(3, weight=1)

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

    def _on_lanzar(self) -> None:
        """Gestionar el clic del botón y mostrar un reporte homogéneo."""
        try:
            status_code, body = lanzar_proceso_nenv()
            report = build_response_report(
                operation="PROCESO NENV",
                status_code=status_code,
                body=body,
            )
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report("PROCESO NENV", exc)
            self._set_output(report)

    def _on_limpiar_formulario(self) -> None:
        """Limpiar el estado visible de la pestaña."""
        self._clear_output()
