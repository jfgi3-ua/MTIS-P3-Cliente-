"""Pestaña de interfaz para lanzar el proceso NUNVTS.

Esta pestaña permite al usuario invocar el flujo Mule
"Notificar Usuario No Válido en Todas las Salas", indicando como entrada el
email destinatario que recibirá las notificaciones detectadas por el proceso.
"""

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from config import OUTPUT_BG, OUTPUT_FG, OUTPUT_FONT, OUTPUT_INSERT
from services.rest_service import lanzar_proceso_nunvts
from utils.formatters import (
    build_exception_report,
    build_response_report,
    build_validation_error_report,
)


class NUNVTSTab:
    """Encapsula la construcción y el comportamiento de la pestaña NUNVTS."""

    def __init__(self, parent: ttk.Frame) -> None:
        """Guardar el contenedor padre e inicializar el estado visual."""
        self.parent = parent
        self.email_var = tk.StringVar()
        self.output_text: ScrolledText | None = None
        self._build()

    def _build(self) -> None:
        """Crear los widgets visibles de la pestaña."""
        ttk.Label(
            self.parent,
            text="Proceso NUNVTS - Notificar Usuario No Válido en Todas las Salas",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        ttk.Label(
            self.parent,
            text=(
                "Introduce el email destinatario que recibirá las notificaciones "
                "de accesos detectados por la orquestación."
            )
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        form_frame = ttk.LabelFrame(
            self.parent,
            text="Parámetros de entrada",
            padding=10,
            style="Section.TLabelframe"
        )
        form_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Label(form_frame, text="Email destinatario:").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        ttk.Entry(
            form_frame,
            textvariable=self.email_var,
            width=50
        ).grid(row=0, column=1, sticky="ew")
        form_frame.columnconfigure(1, weight=1)

        actions_frame = ttk.LabelFrame(
            self.parent,
            text="Acciones",
            padding=10,
            style="Section.TLabelframe"
        )
        actions_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ttk.Button(
            actions_frame,
            text="Lanzar proceso NUNVTS",
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
        output_frame.grid(row=4, column=0, columnspan=2, sticky="nsew")

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

        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(4, weight=1)

    def _is_email_valid(self, email: str) -> bool:
        """Aplicar una validación básica del email antes de invocar el flujo."""
        if not email:
            return False
        if email.count("@") != 1:
            return False

        local_part, domain_part = email.split("@")
        if not local_part or not domain_part:
            return False
        if "." not in domain_part:
            return False
        return True

    def _clear_output(self) -> None:
        """Limpiar el contenido previo de la salida visual."""
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
        """Gestionar el clic del botón y coordinar la ejecución completa."""
        email = self.email_var.get().strip()

        if not self._is_email_valid(email):
            report = build_validation_error_report(
                "Debes introducir un email con un formato básico válido.\n"
                "Ejemplo: seguridad@mtis.local"
            )
            self._set_output(report)
            return

        try:
            status_code, body = lanzar_proceso_nunvts(email)
            report = build_response_report(
                operation="PROCESO NUNVTS",
                status_code=status_code,
                body=body,
                extra_lines=[f"Email enviado: {email}"],
            )
            self._set_output(report)
        except Exception as exc:
            report = build_exception_report(
                operation="PROCESO NUNVTS",
                exception=exc,
                extra_lines=[f"Email intentado: {email}"],
            )
            self._set_output(report)

    def _on_limpiar_formulario(self) -> None:
        """Restablecer la pestaña a un estado limpio."""
        self.email_var.set("")
        self._clear_output()
