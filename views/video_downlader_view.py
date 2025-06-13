#!/usr/bin/env python3
"""
VISTA - Interfaz gráfica para el descargador de videos
Este archivo contiene todos los componentes visuales y la configuración
de la interfaz de usuario usando tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional, List, Dict, Any


class VideoDownloaderView:
    """
    Vista que maneja toda la interfaz gráfica de usuario.
    
    Responsabilidades:
    - Crear y gestionar todos los widgets de la interfaz
    - Proporcionar métodos para actualizar la interfaz
    - Comunicarse con el controlador a través de callbacks
    """
    
    def __init__(self):
        """
        Inicializa la ventana principal y configura todos los componentes visuales.
        """
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("🎬 Descargador de Videos y Playlists")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Intentar configurar ícono (opcional)
        self._setup_window_icon()
        
        # Variables de interfaz
        self.download_path = tk.StringVar(value="./descargas")
        self.download_type = tk.StringVar(value="single")
        
        # Referencias a widgets importantes
        self.url_entry: Optional[ttk.Entry] = None
        self.quality_combo: Optional[ttk.Combobox] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.log_text: Optional[scrolledtext.ScrolledText] = None
        self.download_btn: Optional[ttk.Button] = None
        self.cancel_btn: Optional[ttk.Button] = None
        self.info_btn: Optional[ttk.Button] = None
        
        # Callbacks para comunicación con el controlador
        self.on_paste_url: Optional[Callable] = None
        self.on_browse_folder: Optional[Callable] = None
        self.on_get_info: Optional[Callable] = None
        self.on_start_download: Optional[Callable] = None
        self.on_cancel_download: Optional[Callable] = None
        self.on_clear_log: Optional[Callable] = None
        self.on_open_folder: Optional[Callable] = None
        self.on_save_log: Optional[Callable] = None
        self.on_closing: Optional[Callable] = None
        
        # Configurar estilos y crear interfaz
        self._setup_styles()
        self._create_widgets()
        self._configure_closing_protocol()
    
    def _setup_window_icon(self):
        """
        Configura el ícono de la ventana si está disponible.
        """
        try:
            # Intentar cargar ícono personalizado
            icon_path = Path("assets/video_icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            # Si no se puede cargar el ícono, continuar sin él
            pass
    
    def _setup_styles(self):
        """
        Configura los estilos visuales de la aplicación usando ttk.Style.
        """
        self.style = ttk.Style()
        
        # Estilos para etiquetas
        self.style.configure('Title.TLabel', 
                           font=('Arial', 14, 'bold'),
                           foreground='#2c3e50')
        
        self.style.configure('Subtitle.TLabel', 
                           font=('Arial', 10, 'bold'),
                           foreground='#34495e')
        
        # Estilo para botón principal
        self.style.configure('Action.TButton',
                           font=('Arial', 10, 'bold'))
    
    def _create_widgets(self):
        """
        Crea todos los widgets de la interfaz gráfica.
        """
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión de la ventana
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)  # Hacer que el área de log se expanda
        
        # Crear secciones de la interfaz
        self._create_title_section(main_frame)
        self._create_url_section(main_frame)
        self._create_download_type_section(main_frame)
        self._create_quality_section(main_frame)
        self._create_path_section(main_frame)
        self._create_action_buttons(main_frame)
        self._create_progress_section(main_frame)
        self._create_log_section(main_frame)
        self._create_extra_buttons(main_frame)
        
        # Mensaje de bienvenida
        self._show_welcome_message()
    
    def _create_title_section(self, parent):
        """
        Crea la sección del título principal.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        title_label = ttk.Label(parent, 
                               text="🎬 Descargador de Videos y Playlists", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
    
    def _create_url_section(self, parent):
        """
        Crea la sección de entrada de URL.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Etiqueta
        ttk.Label(parent, text="📎 URL del Video o Playlist:", 
                 style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Campo de entrada
        self.url_entry = ttk.Entry(parent, width=60, font=('Arial', 10))
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Botón pegar
        paste_btn = ttk.Button(parent, text="📋", width=3, 
                              command=self._handle_paste_url)
        paste_btn.grid(row=1, column=2, padx=(5, 0), pady=5)
    
    def _create_download_type_section(self, parent):
        """
        Crea la sección de selección de tipo de descarga.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Etiqueta
        ttk.Label(parent, text="📥 Tipo de Descarga:", 
                 style='Subtitle.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Marco para botones de radio
        type_frame = ttk.Frame(parent)
        type_frame.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Botones de radio
        ttk.Radiobutton(type_frame, text="🎥 Video Individual", 
                       variable=self.download_type, value="single").pack(side=tk.LEFT)
        
        ttk.Radiobutton(type_frame, text="📋 Playlist Completa", 
                       variable=self.download_type, value="playlist").pack(side=tk.LEFT, padx=(20, 0))
    
    def _create_quality_section(self, parent):
        """
        Crea la sección de selección de calidad.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Etiqueta
        ttk.Label(parent, text="🎥 Calidad:", 
                 style='Subtitle.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Combobox de calidad
        self.quality_combo = ttk.Combobox(parent, width=20, state="readonly")
        self.quality_combo['values'] = ('480p', '720p', '1080p', 'Mejor disponible', 'Audio únicamente')
        self.quality_combo.set('720p')
        self.quality_combo.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def _create_path_section(self, parent):
        """
        Crea la sección de selección de carpeta de descarga.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Etiqueta
        ttk.Label(parent, text="📁 Carpeta de Descarga:", 
                 style='Subtitle.TLabel').grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Marco para ruta y botón
        path_frame = ttk.Frame(parent)
        path_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        # Campo de ruta (solo lectura)
        path_entry = ttk.Entry(path_frame, textvariable=self.download_path, 
                              state="readonly", font=('Arial', 9))
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Botón examinar
        browse_btn = ttk.Button(path_frame, text="📂 Examinar", 
                               command=self._handle_browse_folder)
        browse_btn.grid(row=0, column=1)
    
    def _create_action_buttons(self, parent):
        """
        Crea los botones de acción principales.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Marco para botones
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Botón de información
        self.info_btn = ttk.Button(button_frame, text="ℹ️ Ver Información", 
                                  command=self._handle_get_info)
        self.info_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón de descarga
        self.download_btn = ttk.Button(button_frame, text="⬇️ Descargar", 
                                      style='Action.TButton',
                                      command=self._handle_start_download)
        self.download_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón de cancelar
        self.cancel_btn = ttk.Button(button_frame, text="❌ Cancelar", 
                                    command=self._handle_cancel_download, 
                                    state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_progress_section(self, parent):
        """
        Crea la sección de barra de progreso.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Etiqueta
        ttk.Label(parent, text="📊 Progreso:", 
                 style='Subtitle.TLabel').grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(parent, mode='indeterminate')
        self.progress_bar.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), 
                              padx=(10, 0), pady=(10, 5))
    
    def _create_log_section(self, parent):
        """
        Crea la sección del área de registro.
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Etiqueta
        ttk.Label(parent, text="📝 Registro de Actividad:", 
                 style='Subtitle.TLabel').grid(row=7, column=0, sticky=(tk.W, tk.N), pady=(10, 5))
        
        # Área de texto con scroll
        self.log_text = scrolledtext.ScrolledText(parent, width=70, height=15, 
                                                 font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          padx=(10, 0), pady=(10, 5))
    
    def _create_extra_buttons(self, parent):
        """
        Crea los botones adicionales (limpiar, abrir carpeta, etc.).
        
        Args:
            parent: Widget padre donde crear la sección
        """
        # Marco para botones extra
        extra_frame = ttk.Frame(parent)
        extra_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        # Botón limpiar registro
        clear_btn = ttk.Button(extra_frame, text="🗑️ Limpiar Registro", 
                              command=self._handle_clear_log)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón abrir carpeta
        open_folder_btn = ttk.Button(extra_frame, text="📂 Abrir Carpeta", 
                                    command=self._handle_open_folder)
        open_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón guardar registro
        save_log_btn = ttk.Button(extra_frame, text="💾 Guardar Registro", 
                                 command=self._handle_save_log)
        save_log_btn.pack(side=tk.LEFT, padx=5)
    
    def _show_welcome_message(self):
        """
        Muestra mensajes de bienvenida iniciales.
        """
        self.add_log_message("🎬 Bienvenido al Descargador de Videos y Playlists")
        self.add_log_message("💡 Pega una URL de YouTube y selecciona el tipo de descarga")
        self.add_log_message("📁 Los videos se guardarán en: " + self.download_path.get())
    
    def _configure_closing_protocol(self):
        """
        Configura el protocolo de cierre de la ventana.
        """
        self.root.protocol("WM_DELETE_WINDOW", self._handle_closing)
    
    # === MÉTODOS PARA MANEJAR EVENTOS ===
    
    def _handle_paste_url(self):
        """Maneja el evento de pegar URL."""
        if self.on_paste_url:
            self.on_paste_url()
    
    def _handle_browse_folder(self):
        """Maneja el evento de examinar carpeta."""
        if self.on_browse_folder:
            self.on_browse_folder()
    
    def _handle_get_info(self):
        """Maneja el evento de obtener información."""
        if self.on_get_info:
            self.on_get_info()
    
    def _handle_start_download(self):
        """Maneja el evento de iniciar descarga."""
        if self.on_start_download:
            self.on_start_download()
    
    def _handle_cancel_download(self):
        """Maneja el evento de cancelar descarga."""
        if self.on_cancel_download:
            self.on_cancel_download()
    
    def _handle_clear_log(self):
        """Maneja el evento de limpiar registro."""
        if self.on_clear_log:
            self.on_clear_log()
    
    def _handle_open_folder(self):
        """Maneja el evento de