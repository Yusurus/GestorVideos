# main.py - Archivo principal que inicia la aplicación
# Punto de entrada del programa que une todos los componentes MVC

import tkinter as tk
from modelo import DescargadorModelo
from vista import DescargadorVista
from controlador import DescargadorControlador

def main():
    """
    Función principal que inicializa la aplicación
    """
    try:
        # Crea la ventana raíz de tkinter
        root = tk.Tk()
        
        # Inicializa los componentes del patrón MVC
        modelo = DescargadorModelo()
        vista = DescargadorVista(root)
        controlador = DescargadorControlador(modelo, vista)
        
        # Configura el protocolo de cierre de ventana
        root.protocol("WM_DELETE_WINDOW", root.quit)
        
        # Inicia el bucle principal de la aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"Error al inicializar la aplicación: {e}")
        print("Asegúrate de tener instaladas las dependencias:")
        print("pip install yt-dlp")

if __name__ == "__main__":
    main()