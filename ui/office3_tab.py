"""Consola de monitorización de la Office 3 gestionada por Mule.

Esta pestaña cubre el apartado que faltaba para completar el cliente de la
práctica 3: una consola visual enfocada a supervisar la oficina simulada por
Mule (Office 3). La consola no publica ni consume directamente sobre ActiveMQ;
se apoya en la información persistida por Mule en MySQL para ofrecer una vista
estable y defendible durante la evaluación.

Qué muestra:
- estado actual de temperatura e iluminación
- modos HVAC/LIGHT activos y sus targets
- contadores internos de estabilidad/perturbación
- últimas acciones ejecutadas por los listeners de comandos
- errores recientes del apartado 5

Qué no hace deliberadamente:
- modificar el estado de la oficina
- sustituir la consola principal de la práctica 2

Su objetivo es ser una herramienta ligera de observación, no de control.
"""

from __future__ import annotations

from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from config import (
    COLOR_NAVY_DARK,
    DB_HOST,
    DB_NAME,
    DB_OFFICE_ID,
    DB_PORT,
    DB_USER,
    OFFICE3_MONITOR_ACTION_LIMIT,
    OFFICE3_MONITOR_DEFAULT_REFRESH_SECONDS,
    OFFICE3_MONITOR_ERROR_LIMIT,
    OUTPUT_BG,
    OUTPUT_FG,
    OUTPUT_FONT,
    OUTPUT_INSERT,
)
from services.office_monitor_service import fetch_office3_monitor_snapshot
from utils.formatters import build_exception_report, current_timestamp_text


class Office3MonitorTab:
    """Pestaña dedicada a la supervisión visual de la Office 3 de Mule."""

    def __init__(self, parent: ttk.Frame) -> None:
        """Guardar el contenedor padre e inicializar estado visual y temporización."""
        self.parent = parent

        self.connection_status_var = tk.StringVar(value="Pendiente de primera lectura")
        self.driver_var = tk.StringVar(value="-")
        self.last_ui_refresh_var = tk.StringVar(value="-")
        self.office_id_var = tk.StringVar(value=str(DB_OFFICE_ID))
        self.temperature_var = tk.StringVar(value="-")
        self.temperature_status_var = tk.StringVar(value="-")
        self.light_var = tk.StringVar(value="-")
        self.light_status_var = tk.StringVar(value="-")
        self.hvac_mode_var = tk.StringVar(value="-")
        self.hvac_target_var = tk.StringVar(value="-")
        self.light_mode_var = tk.StringVar(value="-")
        self.light_target_var = tk.StringVar(value="-")
        self.cycles_var = tk.StringVar(value="-")
        self.perturbation_var = tk.StringVar(value="-")
        self.db_timestamp_var = tk.StringVar(value="-")
        self.overall_state_var = tk.StringVar(value="-")

        self.auto_refresh_var = tk.BooleanVar(value=False)
        self.refresh_seconds_var = tk.StringVar(value=OFFICE3_MONITOR_DEFAULT_REFRESH_SECONDS)
        self._scheduled_job_id: str | None = None

        self.actions_text: ScrolledText | None = None
        self.errors_text: ScrolledText | None = None

        self._build()

    def _build(self) -> None:
        """Construir la interfaz completa de la consola de monitorización."""
        ttk.Label(
            self.parent,
            text="Office 3 - Consola de monitorización Mule",
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ttk.Label(
            self.parent,
            text=(
                "Consulta el estado persistido de la Office 3, el histórico de acciones "
                "aplicadas por Mule y los errores recientes del apartado 5."
            )
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))

        control_frame = ttk.LabelFrame(
            self.parent,
            text="Control de monitorización",
            padding=10,
            style="Section.TLabelframe"
        )
        control_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(control_frame, text="Origen de datos:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Label(
            control_frame,
            text=f"MySQL {DB_HOST}:{DB_PORT} · BD {DB_NAME} · Usuario {DB_USER}",
        ).grid(row=0, column=1, sticky="w")

        ttk.Label(control_frame, text="Intervalo auto-refresco (s):").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        refresh_combo = ttk.Combobox(
            control_frame,
            textvariable=self.refresh_seconds_var,
            values=("2", "3", "5", "10", "15"),
            width=8,
            state="readonly",
        )
        refresh_combo.grid(row=1, column=1, sticky="w", pady=(10, 0))

        ttk.Checkbutton(
            control_frame,
            text="Auto-refresco",
            variable=self.auto_refresh_var,
            command=self._on_toggle_auto_refresh,
        ).grid(row=1, column=2, sticky="w", padx=(20, 0), pady=(10, 0))

        ttk.Button(
            control_frame,
            text="Refrescar ahora",
            style="Action.TButton",
            command=self._on_refresh_now,
        ).grid(row=0, column=2, padx=(20, 8), sticky="w")

        ttk.Button(
            control_frame,
            text="Limpiar paneles",
            style="Action.TButton",
            command=self._on_clear_panels,
        ).grid(row=0, column=3, sticky="w")

        control_frame.columnconfigure(1, weight=1)

        summary_frame = ttk.LabelFrame(
            self.parent,
            text="Resumen en tiempo real",
            padding=10,
            style="Section.TLabelframe"
        )
        summary_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        self._add_summary_row(summary_frame, 0, "Estado de conexión:", self.connection_status_var)
        self._add_summary_row(summary_frame, 0, "Driver MySQL:", self.driver_var, column_offset=2)
        self._add_summary_row(summary_frame, 1, "Última actualización UI:", self.last_ui_refresh_var)
        self._add_summary_row(summary_frame, 1, "Office ID:", self.office_id_var, column_offset=2)
        self._add_summary_row(summary_frame, 2, "Temperatura actual:", self.temperature_var)
        self._add_summary_row(summary_frame, 2, "Estado térmico:", self.temperature_status_var, column_offset=2)
        self._add_summary_row(summary_frame, 3, "Iluminación actual:", self.light_var)
        self._add_summary_row(summary_frame, 3, "Estado lumínico:", self.light_status_var, column_offset=2)
        self._add_summary_row(summary_frame, 4, "HVAC mode:", self.hvac_mode_var)
        self._add_summary_row(summary_frame, 4, "HVAC target:", self.hvac_target_var, column_offset=2)
        self._add_summary_row(summary_frame, 5, "LIGHT mode:", self.light_mode_var)
        self._add_summary_row(summary_frame, 5, "LIGHT target:", self.light_target_var, column_offset=2)
        self._add_summary_row(summary_frame, 6, "Ciclos estables:", self.cycles_var)
        self._add_summary_row(summary_frame, 6, "Índice perturbación:", self.perturbation_var, column_offset=2)
        self._add_summary_row(summary_frame, 7, "Timestamp BD:", self.db_timestamp_var)
        self._add_summary_row(summary_frame, 7, "Resumen global:", self.overall_state_var, column_offset=2)

        for column in (1, 3):
            summary_frame.columnconfigure(column, weight=1)

        lower_frame = ttk.Frame(self.parent)
        lower_frame.grid(row=4, column=0, sticky="nsew")

        actions_frame = ttk.LabelFrame(
            lower_frame,
            text=f"Últimas acciones de Office 3 (máx. {OFFICE3_MONITOR_ACTION_LIMIT})",
            padding=10,
            style="Section.TLabelframe"
        )
        actions_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        errors_frame = ttk.LabelFrame(
            lower_frame,
            text=f"Errores recientes del apartado 5 (máx. {OFFICE3_MONITOR_ERROR_LIMIT})",
            padding=10,
            style="Section.TLabelframe"
        )
        errors_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.actions_text = ScrolledText(
            actions_frame,
            wrap="word",
            width=62,
            height=22,
            font=OUTPUT_FONT,
            bg=OUTPUT_BG,
            fg=OUTPUT_FG,
            insertbackground=OUTPUT_INSERT,
            relief="solid",
            borderwidth=1,
        )
        self.actions_text.pack(fill="both", expand=True)

        self.errors_text = ScrolledText(
            errors_frame,
            wrap="word",
            width=62,
            height=22,
            font=OUTPUT_FONT,
            bg=OUTPUT_BG,
            fg=OUTPUT_FG,
            insertbackground=OUTPUT_INSERT,
            relief="solid",
            borderwidth=1,
        )
        self.errors_text.pack(fill="both", expand=True)

        lower_frame.columnconfigure(0, weight=1)
        lower_frame.columnconfigure(1, weight=1)
        lower_frame.rowconfigure(0, weight=1)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(4, weight=1)

    def _add_summary_row(
        self,
        parent: ttk.LabelFrame,
        row: int,
        label_text: str,
        value_var: tk.StringVar,
        column_offset: int = 0,
    ) -> None:
        """Añadir una pareja etiqueta/valor al panel de resumen."""
        ttk.Label(parent, text=label_text).grid(
            row=row,
            column=column_offset,
            sticky="w",
            padx=(0, 10),
            pady=3,
        )
        ttk.Label(parent, textvariable=value_var).grid(
            row=row,
            column=column_offset + 1,
            sticky="w",
            pady=3,
        )

    def _set_text_widget_content(self, widget: ScrolledText | None, text: str) -> None:
        """Sustituir por completo el contenido de un panel de texto."""
        if widget is None:
            return
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)

    def _format_datetime(self, value: object) -> str:
        """Normalizar fechas/horas provenientes de MySQL para la interfaz."""
        if value is None:
            return "-"
        if isinstance(value, datetime):
            return value.strftime("%d/%m/%Y %H:%M:%S")
        return str(value)

    def _derive_temperature_status(self, value: float) -> str:
        """Traducir la temperatura actual a una etiqueta sencilla de confort."""
        if 23 <= value <= 25:
            return "En confort (23-25 ºC)"
        if value < 23:
            return "Por debajo del rango de confort"
        return "Por encima del rango de confort"

    def _derive_light_status(self, value: float) -> str:
        """Traducir la iluminación actual a una etiqueta sencilla de confort."""
        if 450 <= value <= 650:
            return "En confort (450-650 LUX)"
        if value < 450:
            return "Por debajo del rango de confort"
        return "Por encima del rango de confort"

    def _derive_overall_state(self, state: dict[str, object]) -> str:
        """Construir una lectura global compacta del estado de la oficina."""
        hvac_mode = str(state.get("hvac_mode") or "IDLE")
        light_mode = str(state.get("light_mode") or "IDLE")
        temp = float(state.get("temperatura_actual") or 0)
        light = float(state.get("iluminacion_actual") or 0)

        both_idle = hvac_mode == "IDLE" and light_mode == "IDLE"
        both_in_comfort = 23 <= temp <= 25 and 450 <= light <= 650

        if both_idle and both_in_comfort:
            return "Estable y en confort"
        if not both_idle:
            return "En ajuste activo por actuadores"
        return "Idle, pero todavía fuera de confort"

    def _render_state(self, state: dict[str, object], driver_name: str) -> None:
        """Volcar el estado de la Office 3 en el panel de resumen."""
        temp = float(state.get("temperatura_actual") or 0)
        light = float(state.get("iluminacion_actual") or 0)

        self.connection_status_var.set("Lectura correcta")
        self.driver_var.set(driver_name)
        self.last_ui_refresh_var.set(current_timestamp_text())
        self.office_id_var.set(str(state.get("office_id") or DB_OFFICE_ID))
        self.temperature_var.set(f"{temp:.2f} ºC")
        self.temperature_status_var.set(self._derive_temperature_status(temp))
        self.light_var.set(f"{light:.2f} LUX")
        self.light_status_var.set(self._derive_light_status(light))
        self.hvac_mode_var.set(str(state.get("hvac_mode") or "-"))
        self.hvac_target_var.set(str(state.get("hvac_target") or "-"))
        self.light_mode_var.set(str(state.get("light_mode") or "-"))
        self.light_target_var.set(str(state.get("light_target") or "-"))
        self.cycles_var.set(str(state.get("ciclos_estables") or "0"))
        self.perturbation_var.set(str(state.get("indice_perturbacion") or "0"))
        self.db_timestamp_var.set(self._format_datetime(state.get("fecha_hora")))
        self.overall_state_var.set(self._derive_overall_state(state))

    def _render_actions(self, actions: list[dict[str, object]]) -> None:
        """Formatear las últimas acciones de la Office 3 para lectura humana."""
        if not actions:
            text = (
                "No hay acciones registradas todavía para la Office 3.\n\n"
                "Cuando Mule reciba comandos HVAC o LIGHT desde ActiveMQ, las "
                "operaciones aplicadas aparecerán aquí."
            )
            self._set_text_widget_content(self.actions_text, text)
            return

        lines = []
        for action in actions:
            lines.append(
                f"[{self._format_datetime(action.get('fecha_hora'))}] "
                f"{action.get('tipo_variable', '-')} | "
                f"{action.get('accion_realizada', '-')} | "
                f"topic={action.get('topic_origen', '-')} | "
                f"{action.get('valor_anterior', '-')} -> {action.get('valor_nuevo', '-')}"
            )

        self._set_text_widget_content(self.actions_text, "\n".join(lines))

    def _render_errors(self, errors: list[dict[str, object]]) -> None:
        """Formatear los errores recientes del apartado 5 para lectura rápida."""
        if not errors:
            text = (
                "No hay errores recientes registrados para los flujos del apartado 5.\n\n"
                "Esto es una buena señal de estabilidad del publisher y de los "
                "listeners HVAC/LIGHT."
            )
            self._set_text_widget_content(self.errors_text, text)
            return

        lines = []
        for error in errors:
            lines.append(
                f"[{self._format_datetime(error.get('fecha_hora'))}] "
                f"flujo={error.get('flujo', '-')} | "
                f"operación={error.get('operacion', '-')}\n"
                f"Mensaje: {error.get('mensaje_error', '-')}\n"
                f"Detalle: {error.get('detalle_error', '-')}\n"
                f"{'-' * 90}"
            )

        self._set_text_widget_content(self.errors_text, "\n".join(lines))

    def _cancel_scheduled_refresh(self) -> None:
        """Cancelar un refresco programado si existe."""
        if self._scheduled_job_id is not None:
            try:
                self.parent.after_cancel(self._scheduled_job_id)
            except tk.TclError:
                pass
            self._scheduled_job_id = None

    def _schedule_next_refresh(self) -> None:
        """Programar el siguiente refresco automático según el intervalo elegido."""
        self._cancel_scheduled_refresh()

        if not self.auto_refresh_var.get():
            return

        try:
            interval_ms = max(1, int(self.refresh_seconds_var.get())) * 1000
        except ValueError:
            interval_ms = 3000

        self._scheduled_job_id = self.parent.after(interval_ms, self._auto_refresh_tick)

    def _auto_refresh_tick(self) -> None:
        """Ejecutar una iteración de refresco automático."""
        self._scheduled_job_id = None
        if self.auto_refresh_var.get():
            self._refresh_snapshot(schedule_next=True)

    def _refresh_snapshot(self, schedule_next: bool) -> None:
        """Leer la instantánea completa y refrescar toda la pestaña."""
        try:
            snapshot = fetch_office3_monitor_snapshot()
            self._render_state(snapshot["state"], snapshot["driver"])
            self._render_actions(snapshot["actions"])
            self._render_errors(snapshot["errors"])
        except Exception as exc:
            self.connection_status_var.set("Error de lectura")
            self.driver_var.set("-")
            self.last_ui_refresh_var.set(current_timestamp_text())
            self._set_text_widget_content(
                self.errors_text,
                build_exception_report(
                    operation="MONITOR OFFICE 3",
                    exception=exc,
                    extra_lines=[
                        f"Host BD: {DB_HOST}:{DB_PORT}",
                        f"Base de datos: {DB_NAME}",
                    ],
                ),
            )
            if self.actions_text is not None:
                self._set_text_widget_content(
                    self.actions_text,
                    (
                        "No se ha podido refrescar el histórico de acciones porque la "
                        "lectura del monitor ha fallado. Revisa el detalle técnico en el panel de errores."
                    ),
                )
        finally:
            if schedule_next:
                self._schedule_next_refresh()

    def _on_refresh_now(self) -> None:
        """Lanzar una lectura inmediata sin depender del temporizador automático."""
        self._refresh_snapshot(schedule_next=self.auto_refresh_var.get())

    def _on_toggle_auto_refresh(self) -> None:
        """Activar o desactivar el refresco automático."""
        if self.auto_refresh_var.get():
            self._refresh_snapshot(schedule_next=True)
        else:
            self._cancel_scheduled_refresh()
            self.connection_status_var.set("Auto-refresco detenido")

    def _on_clear_panels(self) -> None:
        """Restablecer la consola a un estado visual limpio y controlado."""
        self._cancel_scheduled_refresh()
        self.auto_refresh_var.set(False)

        for variable in (
            self.connection_status_var,
            self.driver_var,
            self.last_ui_refresh_var,
            self.temperature_var,
            self.temperature_status_var,
            self.light_var,
            self.light_status_var,
            self.hvac_mode_var,
            self.hvac_target_var,
            self.light_mode_var,
            self.light_target_var,
            self.cycles_var,
            self.perturbation_var,
            self.db_timestamp_var,
            self.overall_state_var,
        ):
            variable.set("-")

        self.office_id_var.set(str(DB_OFFICE_ID))
        self._set_text_widget_content(self.actions_text, "")
        self._set_text_widget_content(self.errors_text, "")
        self.connection_status_var.set("Paneles limpiados")
