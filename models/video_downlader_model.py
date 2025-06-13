#!/usr/bin/env python3
"""
MODELO - Lógica de negocio para el descargador de videos
Este archivo contiene toda la lógica relacionada con la descarga de videos,
extracción de información y configuración de yt-dlp.
"""

import yt_dlp
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import json


class VideoDownloaderModel:
    """
    Modelo que maneja toda la lógica de descarga de videos y playlists.
    
    Responsabilidades:
    - Extraer información de videos/playlists
    - Configurar opciones de descarga
    - Realizar descargas con callbacks de progreso
    - Manejar errores de descarga
    """
    
    def __init__(self):
        """
        Inicializa el modelo con configuraciones por defecto.
        """
        # Configuraciones por defecto
        self.default_download_path = "./descargas"
        self.default_quality = "720p"
        
        # Estado actual de descarga
        self.is_downloading = False
        self.current_download_thread = None
        
        # Callbacks para comunicación con el controlador
        self.progress_callback: Optional[Callable] = None
        self.log_callback: Optional[Callable] = None
        self.completion_callback: Optional[Callable] = None
        self.error_callback: Optional[Callable] = None
    
    def set_callbacks(self, progress_callback: Callable = None, 
                     log_callback: Callable = None,
                     completion_callback: Callable = None,
                     error_callback: Callable = None):
        """
        Establece las funciones callback para comunicación con el controlador.
        
        Args:
            progress_callback: Función llamada durante el progreso de descarga
            log_callback: Función llamada para registrar mensajes
            completion_callback: Función llamada al completar la descarga
            error_callback: Función llamada en caso de error
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback
    
    def _log(self, message: str):
        """
        Registra un mensaje usando el callback correspondiente.
        
        Args:
            message: Mensaje a registrar
        """
        if self.log_callback:
            self.log_callback(message)
    
    def validate_url(self, url: str) -> bool:
        """
        Valida si una URL es válida para yt-dlp.
        
        Args:
            url: URL a validar
            
        Returns:
            bool: True si la URL es válida, False en caso contrario
        """
        if not url or not url.strip():
            return False
        
        # Lista básica de patrones válidos
        valid_patterns = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com'
        ]
        
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in valid_patterns)
    
    def extract_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extrae información de un video o playlist sin descargarlo.
        
        Args:
            url: URL del video o playlist
            
        Returns:
            Dict con la información extraída
            
        Raises:
            Exception: Si hay error al extraer información
        """
        self._log("🔍 Extrayendo información del video/playlist...")
        
        try:
            # Configuración para solo extraer información
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,  # Extraer información completa
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            self._log("✅ Información extraída exitosamente")
            return info
            
        except Exception as e:
            error_msg = f"Error al extraer información: {str(e)}"
            self._log(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def get_video_info_formatted(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Formatea la información de un video para mostrar en la interfaz.
        
        Args:
            info: Información cruda del video desde yt-dlp
            
        Returns:
            Dict con información formateada para mostrar
        """
        formatted_info = {}
        
        # Información básica
        formatted_info['titulo'] = info.get('title', 'Sin título')
        formatted_info['canal'] = info.get('uploader', 'Desconocido')
        formatted_info['fecha'] = info.get('upload_date', 'Desconocida')
        formatted_info['vistas'] = str(info.get('view_count', 'N/A'))
        
        # Formatear duración
        duracion = info.get('duration', 0)
        if duracion:
            minutos = duracion // 60
            segundos = duracion % 60
            formatted_info['duracion'] = f"{minutos}:{segundos:02d}"
        else:
            formatted_info['duracion'] = "Desconocida"
        
        # Extraer calidades disponibles
        calidades = set()
        if 'formats' in info:
            for fmt in info['formats']:
                if fmt.get('height'):
                    calidades.add(f"{fmt['height']}p")
        
        formatted_info['calidades'] = sorted(list(calidades), 
                                           key=lambda x: int(x[:-1]), reverse=True)
        
        return formatted_info
    
    def get_playlist_info_formatted(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea la información de una playlist para mostrar en la interfaz.
        
        Args:
            info: Información cruda de la playlist desde yt-dlp
            
        Returns:
            Dict con información formateada de la playlist
        """
        formatted_info = {}
        
        # Información básica de la playlist
        formatted_info['titulo'] = info.get('title', 'Sin título')
        formatted_info['canal'] = info.get('uploader', 'Desconocido')
        formatted_info['total_videos'] = len(info.get('entries', []))
        
        # Lista de videos
        videos = []
        for i, entry in enumerate(info.get('entries', []), 1):
            if entry:  # Verificar que el entry no sea None
                video_info = {
                    'numero': i,
                    'titulo': entry.get('title', f'Video {i}'),
                    'duracion': self._format_duration(entry.get('duration', 0))
                }
                videos.append(video_info)
        
        formatted_info['videos'] = videos
        
        return formatted_info
    
    def _format_duration(self, duration: int) -> str:
        """
        Formatea la duración en segundos a formato MM:SS.
        
        Args:
            duration: Duración en segundos
            
        Returns:
            String con formato MM:SS
        """
        if not duration:
            return "00:00"
        
        minutos = duration // 60
        segundos = duration % 60
        return f"{minutos}:{segundos:02d}"
    
    def get_ydl_options(self, download_path: str, quality: str, 
                       download_type: str) -> Dict[str, Any]:
        """
        Genera las opciones de configuración para yt-dlp.
        
        Args:
            download_path: Ruta donde guardar los archivos
            quality: Calidad de video seleccionada
            download_type: Tipo de descarga ('single' o 'playlist')
            
        Returns:
            Dict con opciones de configuración para yt-dlp
        """
        # Configuración base
        ydl_opts = {
            'writeinfojson': False,
            'writeautomaticsub': False,
            'ignoreerrors': True,
            'progress_hooks': [self._progress_hook],
        }
        
        # Configurar formato según la calidad
        format_map = {
            "480p": 'best[height<=480]',
            "720p": 'best[height<=720]',
            "1080p": 'best[height<=1080]',
            "Mejor disponible": 'best',
            "Audio únicamente": 'bestaudio/best'
        }
        
        ydl_opts['format'] = format_map.get(quality, 'best[height<=720]')
        
        # Configurar patrón de nombres de archivo
        if download_type == "playlist":
            ydl_opts['noplaylist'] = False
            ydl_opts['outtmpl'] = str(Path(download_path) / 
                                     '%(playlist_title)s/%(playlist_index)02d - %(title)s.%(ext)s')
        else:
            ydl_opts['noplaylist'] = True
            ydl_opts['outtmpl'] = str(Path(download_path) / '%(title)s.%(ext)s')
        
        return ydl_opts
    
    def _progress_hook(self, d: Dict[str, Any]):
        """
        Hook interno llamado por yt-dlp durante la descarga.
        
        Args:
            d: Diccionario con información de progreso
        """
        if self.progress_callback:
            self.progress_callback(d)
    
    def start_download(self, url: str, download_path: str, quality: str, 
                      download_type: str) -> bool:
        """
        Inicia la descarga de video/playlist en un hilo separado.
        
        Args:
            url: URL a descargar
            download_path: Ruta donde guardar
            quality: Calidad de video
            download_type: Tipo de descarga
            
        Returns:
            bool: True si se inició correctamente, False si ya hay descarga activa
        """
        if self.is_downloading:
            return False
        
        # Crear carpeta de descarga si no existe
        Path(download_path).mkdir(parents=True, exist_ok=True)
        
        # Marcar como descargando
        self.is_downloading = True
        
        # Iniciar hilo de descarga
        self.current_download_thread = threading.Thread(
            target=self._download_worker,
            args=(url, download_path, quality, download_type),
            daemon=True
        )
        self.current_download_thread.start()
        
        return True
    
    def _download_worker(self, url: str, download_path: str, 
                        quality: str, download_type: str):
        """
        Función worker que realiza la descarga en un hilo separado.
        
        Args:
            url: URL a descargar
            download_path: Ruta donde guardar
            quality: Calidad de video
            download_type: Tipo de descarga
        """
        try:
            self._log("🚀 Iniciando descarga...")
            self._log(f"📎 URL: {url}")
            self._log(f"📥 Tipo: {'Playlist completa' if download_type == 'playlist' else 'Video individual'}")
            self._log(f"🎥 Calidad: {quality}")
            self._log(f"📁 Guardando en: {download_path}")
            self._log("-" * 50)
            
            # Obtener configuración de yt-dlp
            ydl_opts = self.get_ydl_options(download_path, quality, download_type)
            
            # Realizar descarga
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Descarga exitosa
            self._log("✅ ¡Descarga completada exitosamente!")
            self._log(f"📁 Archivos guardados en: {download_path}")
            
            if self.completion_callback:
                self.completion_callback(True, "Descarga completada exitosamente")
                
        except Exception as e:
            error_msg = f"Error durante la descarga: {str(e)}"
            self._log(f"❌ {error_msg}")
            
            if self.error_callback:
                self.error_callback(error_msg)
                
        finally:
            # Marcar como no descargando
            self.is_downloading = False
            self.current_download_thread = None
    
    def cancel_download(self):
        """
        Cancela la descarga actual (limitado por las capacidades de yt-dlp).
        """
        if self.is_downloading:
            self._log("⚠️ Cancelando descarga...")
            self._log("ℹ️ La descarga actual se completará, pero no se iniciarán nuevas descargas")
            
            # Marcar como no descargando
            self.is_downloading = False
    
    def get_supported_formats(self) -> List[str]:
        """
        Retorna lista de formatos/calidades soportados.
        
        Returns:
            Lista de strings con las calidades disponibles
        """
        return ['480p', '720p', '1080p', 'Mejor disponible', 'Audio únicamente']
    
    def get_default_download_path(self) -> str:
        """
        Retorna la ruta de descarga por defecto.
        
        Returns:
            String con la ruta por defecto
        """
        return self.default_download_path