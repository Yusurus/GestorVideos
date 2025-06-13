#!/usr/bin/env python3
"""
CONTROLADOR - Coordinador entre modelo y vista para el descargador de videos
Este archivo contiene la lógica de control que coordina las interacciones
entre la vista (interfaz) y el modelo (lógica de negocio).
"""

import os
import sys
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import platform
from datetime import datetime

# Importar modelo y vista
from models.video_downloader_model import VideoDownloaderModel
from views.video_downloader_view import VideoDownloaderView


class VideoDownloaderController:
    """
    Controlador principal que coordina entre el modelo y la vista.
    
    Responsabilidades:
    - Coordinar comunicación entre modelo y vista
    - Manejar eventos de la interfaz
    - Procesar datos antes de enviarlos al modelo o vista
    - Gestionar el flujo de la aplicación
    """
    
    def __init__(self):
        """
        Inicializa el controlador, modelo y vista.
        """
        # Crear instancias del modelo y vista
        self.model = VideoDownloaderModel()
        self.view = VideoDownloaderView()
        
        # Configurar callbacks
        self._setup_model_callbacks()
        self._setup_view_callbacks()
        
        # Estado de la aplicación
        self.current_video_info: Optional[Dict[str, Any]] = None
        self.is_playlist: bool = False
        
        # Configurar ruta de descarga inicial
        self._setup_initial_download_path()
        
        # Mensaje de inicio
        self.view.add_log_message("🚀 Aplicación iniciada correctamente")
        self.view.add_log_message("💡 Consejo: Puedes usar Ctrl+V para pegar URLs rápidamente")
    
    def _setup_model_callbacks(self):
        """
        Configura los callbacks del modelo para comunicarse con la vista.
        """
        self.model.set_callbacks(
            progress_callback=self._on_download_progress,
            log_callback=self._on_model_log,
            completion_callback=self._on_download_completion,
            error_callback=self._on_download_error
        )
    
    def _setup_view_callbacks(self):
        """
        Configura los callbacks