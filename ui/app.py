"""Construcción de la ventana principal del cliente MTIS.

Esta clase define la estructura global de la interfaz: ventana, estilos,
contenedor principal y pestañas. Su objetivo es centralizar el "esqueleto"
visual de la aplicación, mientras que cada pestaña concreta delega su contenido
funcional en módulos separados.
"""

import tkinter as tk
from tkinter import ttk

from config import (
    APP_FOOTER,
    APP_SUBTITLE,
    APP_TITLE,
    COLOR_APP_BG,
    COLOR_BORDER,
    COLOR_NAVY_ACCENT,
    COLOR_NAVY_DARK,
    COLOR_NAVY_LIGHT,
    COLOR_NAVY_MID,
    COLOR_PANEL_BG,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_ON_DARK,
    COLOR_TEXT_SOFT,
    WINDOW_MIN_SIZE,
    WINDOW_SIZE,
)
from ui.empleados_tab import EmpleadosTab
from ui.nenv_tab import NENVTab
from ui.niveles_tab import NivelesTab
from ui.nunvts_tab import NUNVTSTab
from ui.office3_tab import Office3MonitorTab


class ClienteMTISApp:
    """Clase orquestadora de la interfaz principal."""

    def __init__(self, root: tk.Tk) -> None:
        """Configurar la ventana principal, estilos y layout base."""
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*WINDOW_MIN_SIZE)
        self.root.configure(background=COLOR_APP_BG)

        self._configure_styles()
        self._build_main_layout()

    def _configure_styles(self) -> None:
        """Aplicar un pulido visual basado en azul marino oscuro.

        Se busca una estética más seria y técnica para la evaluación, pero sin
        caer en un tema excesivamente oscuro. La clave está en usar el azul
        marino como color de jerarquía visual (cabeceras, pestañas activas,
        botones y marcos) y mantener fondos claros en las zonas de trabajo.
        """
        style = ttk.Style(self.root)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=COLOR_APP_BG, foreground=COLOR_TEXT_MAIN)
        style.configure("TFrame", background=COLOR_APP_BG)
        style.configure("TLabel", background=COLOR_APP_BG, foreground=COLOR_TEXT_MAIN)
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=COLOR_NAVY_DARK)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=COLOR_TEXT_SOFT)
        style.configure("Footer.TLabel", font=("Segoe UI", 9), foreground=COLOR_TEXT_SOFT)

        style.configure(
            "Section.TLabelframe",
            background=COLOR_PANEL_BG,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_BORDER,
            darkcolor=COLOR_BORDER,
            relief="solid",
        )
        style.configure(
            "Section.TLabelframe.Label",
            background=COLOR_APP_BG,
            foreground=COLOR_NAVY_DARK,
            font=("Segoe UI", 10, "bold"),
        )

        style.configure(
            "Action.TButton",
            background=COLOR_NAVY_MID,
            foreground=COLOR_TEXT_ON_DARK,
            padding=(10, 6),
            borderwidth=0,
            focusthickness=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", COLOR_NAVY_ACCENT), ("pressed", COLOR_NAVY_DARK)],
            foreground=[("active", COLOR_TEXT_ON_DARK), ("pressed", COLOR_TEXT_ON_DARK)],
        )

        style.configure(
            "TEntry",
            fieldbackground="#FFFFFF",
            foreground=COLOR_TEXT_MAIN,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_BORDER,
            darkcolor=COLOR_BORDER,
        )
        style.configure(
            "TCombobox",
            fieldbackground="#FFFFFF",
            foreground=COLOR_TEXT_MAIN,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_BORDER,
            darkcolor=COLOR_BORDER,
        )
        style.configure("TCheckbutton", background=COLOR_APP_BG, foreground=COLOR_TEXT_MAIN)

        style.configure("TNotebook", background=COLOR_APP_BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background=COLOR_NAVY_LIGHT,
            foreground=COLOR_TEXT_MAIN,
            padding=(14, 8),
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLOR_NAVY_MID), ("active", COLOR_NAVY_ACCENT)],
            foreground=[("selected", COLOR_TEXT_ON_DARK), ("active", COLOR_TEXT_ON_DARK)],
        )

    def _build_main_layout(self) -> None:
        """Montar el layout principal y las pestañas de primer nivel."""
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        ttk.Label(
            main_frame,
            text=APP_TITLE,
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            main_frame,
            text=APP_SUBTITLE,
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 10))

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(0, 10))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.tab_empleados = ttk.Frame(self.notebook, padding=10)
        self.tab_niveles = ttk.Frame(self.notebook, padding=10)
        self.tab_nenv = ttk.Frame(self.notebook, padding=10)
        self.tab_nunvts = ttk.Frame(self.notebook, padding=10)
        self.tab_office3 = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_empleados, text="SOAP Empleados")
        self.notebook.add(self.tab_niveles, text="REST Niveles")
        self.notebook.add(self.tab_nenv, text="Proceso NENV")
        self.notebook.add(self.tab_nunvts, text="Proceso NUNVTS")
        self.notebook.add(self.tab_office3, text="Monitor Office 3")

        EmpleadosTab(self.tab_empleados)
        NivelesTab(self.tab_niveles)
        NENVTab(self.tab_nenv)
        NUNVTSTab(self.tab_nunvts)
        Office3MonitorTab(self.tab_office3)

        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=(10, 6))
        ttk.Label(
            main_frame,
            text=APP_FOOTER,
            style="Footer.TLabel"
        ).pack(anchor="w")
