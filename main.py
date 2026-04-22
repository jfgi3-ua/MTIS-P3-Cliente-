"""Punto de entrada del cliente MTIS en Tkinter.

Este módulo tiene una única responsabilidad: arrancar la aplicación gráfica.
La idea es mantenerlo deliberadamente pequeño para que el inicio del programa
sea fácil de localizar y entender.
"""

import tkinter as tk
from ui.app import ClienteMTISApp


def main() -> None:
    """Crear la ventana principal y ceder su construcción a la clase de la UI.

    Flujo de arranque:
    1. Se crea el objeto raíz de Tkinter (la ventana principal real del proceso).
    2. Se inicializa la aplicación, que añade widgets, pestañas y layout.
    3. Se entra en el bucle de eventos de Tkinter para escuchar clics, teclado,
       repintados de pantalla, etc.
    """
    # Tk() instancia la ventana raíz de Tkinter. Solo debe existir una por app.
    root = tk.Tk()

    # La clase ClienteMTISApp encapsula toda la construcción de la interfaz.
    # Se le pasa la ventana raíz para que la configure y añada sus widgets.
    ClienteMTISApp(root)

    # mainloop() deja la aplicación “escuchando” eventos de la interfaz.
    # Sin esta llamada, la ventana se abriría y se cerraría inmediatamente.
    root.mainloop()


# Este patrón evita que el código se ejecute al importar el módulo desde otro.
# Solo arrancará la aplicación si este archivo es el que se ejecuta directamente.
if __name__ == "__main__":
    main()
