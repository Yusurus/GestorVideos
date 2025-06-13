# vista.py - Vista del patrón MVC
# Contiene la interfaz gráfica de usuario con tkinter

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class DescargadorVista:
    """
    Vista que maneja la interfaz gráfica del descargador
    """
    
    def __init__(self, root):
        self.root = root
        self.controlador = None  # Se asignará desde el controlador
        
        # Configuración de la ventana principal
        self.root.title("Descargador de Videos y Audio")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables de tkinter
        self.var_url = tk.StringVar()
        self.var_directorio = tk.StringVar()
        self.var_formato_video = tk.StringVar(value="mp4")
        self.var_calidad = tk.StringVar(value="best")
        self.var_formato_audio = tk.StringVar(value="mp3")
        self.var_progreso = tk.StringVar(value="Listo para descargar")
        
        # Crear la interfaz
        self._crear_interfaz()
        
    def establecer_controlador(self, controlador):
        """
        Establece la referencia al controlador
        """
        self.controlador = controlador
        
    def _crear_interfaz(self):
        """
        Crea todos los elementos de la interfaz gráfica
        """
        # Frame principal con padding
        frame_principal = ttk.Frame(self.root, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # === SECCIÓN URL ===
        self._crear_seccion_url(frame_principal)
        
        # === SECCIÓN DIRECTORIO ===
        self._crear_seccion_directorio(frame_principal)
        
        # === SECCIÓN INFORMACIÓN ===
        self._crear_seccion_informacion(frame_principal)
        
        # === SECCIÓN OPCIONES ===
        self._crear_seccion_opciones(frame_principal)
        
        # === SECCIÓN BOTONES ===
        self._crear_seccion_botones(frame_principal)
        
        # === SECCIÓN PROGRESO ===
        self._crear_seccion_progreso(frame_principal)
        
    def _crear_seccion_url(self, parent):
        """
        Crea la sección para ingresar la URL
        """
        frame_url = ttk.LabelFrame(parent, text="URL del Video", padding="5")
        frame_url.pack(fill=tk.X, pady=(0, 10))
        
        # Entry para la URL
        entry_url = ttk.Entry(frame_url, textvariable=self.var_url, font=("Arial", 10))
        entry_url.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Botón para obtener información
        btn_info = ttk.Button(frame_url, text="Obtener Info", 
                             command=self._on_obtener_info)
        btn_info.pack(side=tk.RIGHT, padx=(5, 0))
        
    def _crear_seccion_directorio(self, parent):
        """
        Crea la sección para seleccionar el directorio de descarga
        """
        frame_dir = ttk.LabelFrame(parent, text="Directorio de Descarga", padding="5")
        frame_dir.pack(fill=tk.X, pady=(0, 10))
        
        # Entry para mostrar el directorio
        entry_dir = ttk.Entry(frame_dir, textvariable=self.var_directorio, 
                             state="readonly", font=("Arial", 9))
        entry_dir.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Botón para seleccionar directorio
        btn_dir = ttk.Button(frame_dir, text="Seleccionar", 
                            command=self._on_seleccionar_directorio)
        btn_dir.pack(side=tk.RIGHT, padx=(5, 0))
        
    def _crear_seccion_informacion(self, parent):
        """
        Crea la sección que muestra información del video
        """
        frame_info = ttk.LabelFrame(parent, text="Información del Video", padding="5")
        frame_info.pack(fill=tk.X, pady=(0, 10))
        
        # Text widget para mostrar información
        self.text_info = tk.Text(frame_info, height=4, wrap=tk.WORD, 
                                font=("Arial", 9), state=tk.DISABLED)
        self.text_info.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para el text widget
        scrollbar = ttk.Scrollbar(frame_info, orient=tk.VERTICAL, 
                                 command=self.text_info.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_info.config(yscrollcommand=scrollbar.set)
        
    def _crear_seccion_opciones(self, parent):
        """
        Crea la sección de opciones de descarga
        """
        frame_opciones = ttk.LabelFrame(parent, text="Opciones de Descarga", padding="5")
        frame_opciones.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para video
        frame_video = ttk.Frame(frame_opciones)
        frame_video.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(frame_video, text="Formato Video:").pack(side=tk.LEFT)
        combo_formato = ttk.Combobox(frame_video, textvariable=self.var_formato_video,
                                   values=["mp4", "webm", "mkv", "avi"], width=10)
        combo_formato.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(frame_video, text="Calidad:").pack(side=tk.LEFT)
        combo_calidad = ttk.Combobox(frame_video, textvariable=self.var_calidad,
                                   values=["best", "worst", "720p", "480p", "360p"], width=10)
        combo_calidad.pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame para audio
        frame_audio = ttk.Frame(frame_opciones)
        frame_audio.pack(fill=tk.X)
        
        ttk.Label(frame_audio, text="Formato Audio:").pack(side=tk.LEFT)
        combo_audio = ttk.Combobox(frame_audio, textvariable=self.var_formato_audio,
                                 values=["mp3", "aac", "wav", "ogg"], width=10)
        combo_audio.pack(side=tk.LEFT, padx=(5, 0))
        
    def _crear_seccion_botones(self, parent):
        """
        Crea la sección de botones de acción
        """
        frame_botones = ttk.Frame(parent)
        frame_botones.pack(fill=tk.X, pady=(0, 10))
        
        # Botón descargar video
        self.btn_video = ttk.Button(frame_botones, text="Descargar Video", 
                                   command=self._on_descargar_video)
        self.btn_video.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill=tk.X)
        
        # Botón descargar audio
        self.btn_audio = ttk.Button(frame_botones, text="Descargar Solo Audio", 
                                   command=self._on_descargar_audio)
        self.btn_audio.pack(side=tk.LEFT, padx=(5, 0), expand=True, fill=tk.X)
        
    def _crear_seccion_progreso(self, parent):
        """
        Crea la sección que muestra el progreso de descarga
        """
        frame_progreso = ttk.LabelFrame(parent, text="Progreso", padding="5")
        frame_progreso.pack(fill=tk.X)
        
        # Barra de progreso (indeterminada por ahora)
        self.progress_bar = ttk.Progressbar(frame_progreso, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Label para mostrar estado
        self.label_estado = ttk.Label(frame_progreso, textvariable=self.var_progreso)
        self.label_estado.pack()
        
    # === MÉTODOS DE EVENTOS ===
    
    def _on_obtener_info(self):
        """
        Maneja el evento de obtener información del video
        """
        if self.controlador:
            url = self.var_url.get().strip()
            if url:
                self.controlador.obtener_informacion_video(url)
            else:
                messagebox.showwarning("Advertencia", "Por favor ingresa una URL válida")
                
    def _on_seleccionar_directorio(self):
        """
        Maneja el evento de seleccionar directorio
        """
        directorio = filedialog.askdirectory()
        if directorio:
            self.var_directorio.set(directorio)
            if self.controlador:
                self.controlador.cambiar_directorio_descarga(directorio)
                
    def _on_descargar_video(self):
        """
        Maneja el evento de descargar video
        """
        if self.controlador:
            url = self.var_url.get().strip()
            if url:
                formato = self.var_formato_video.get()
                calidad = self.var_calidad.get()
                self.controlador.descargar_video(url, formato, calidad)
            else:
                messagebox.showwarning("Advertencia", "Por favor ingresa una URL válida")
                
    def _on_descargar_audio(self):
        """
        Maneja el evento de descargar audio
        """
        if self.controlador:
            url = self.var_url.get().strip()
            if url:
                formato = self.var_formato_audio.get()
                self.controlador.descargar_audio(url, formato)
            else:
                messagebox.showwarning("Advertencia", "Por favor ingresa una URL válida")
    
    # === MÉTODOS PÚBLICOS PARA EL CONTROLADOR ===
    
    def mostrar_informacion_video(self, info):
        """
        Muestra la información del video en el text widget
        """
        self.text_info.config(state=tk.NORMAL)
        self.text_info.delete(1.0, tk.END)
        
        if info:
            texto = f"Título: {info['titulo']}\n"
            texto += f"Duración: {info['duracion']} segundos\n"
            texto += f"Formatos disponibles: {', '.join(info['formatos'])}"
            self.text_info.insert(1.0, texto)
        else:
            self.text_info.insert(1.0, "No se pudo obtener información del video")
            
        self.text_info.config(state=tk.DISABLED)
        
    def establecer_directorio_inicial(self, directorio):
        """
        Establece el directorio inicial en la interfaz
        """
        self.var_directorio.set(directorio)
        
    def iniciar_progreso(self):
        """
        Inicia la animación de la barra de progreso
        """
        self.progress_bar.start()
        self.var_progreso.set("Descargando...")
        self._deshabilitar_botones()
        
    def detener_progreso(self):
        """
        Detiene la animación de la barra de progreso
        """
        self.progress_bar.stop()
        self._habilitar_botones()
        
    def actualizar_progreso(self, porcentaje, velocidad, tiempo_restante):
        """
        Actualiza la información de progreso
        """
        estado = f"Progreso: {porcentaje} - Velocidad: {velocidad} - Tiempo restante: {tiempo_restante}"
        self.var_progreso.set(estado)
        
    def mostrar_completado(self, archivo):
        """
        Muestra mensaje de descarga completada
        """
        self.detener_progreso()
        self.var_progreso.set("Descarga completada")
        messagebox.showinfo("Éxito", f"Descarga completada:\n{os.path.basename(archivo)}")
        
    def mostrar_error(self, mensaje):
        """
        Muestra mensaje de error
        """
        self.detener_progreso()
        self.var_progreso.set("Error en la descarga")
        messagebox.showerror("Error", mensaje)
        
    def _deshabilitar_botones(self):
        """
        Deshabilita los botones durante la descarga
        """
        self.btn_video.config(state=tk.DISABLED)
        self.btn_audio.config(state=tk.DISABLED)
        
    def _habilitar_botones(self):
        """
        Habilita los botones después de la descarga
        """
        self.btn_video.config(state=tk.NORMAL)
        self.btn_audio.config(state=tk.NORMAL)