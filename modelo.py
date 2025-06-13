# modelo.py - Modelo del patrón MVC
# Contiene la lógica de negocio para descargar videos

import yt_dlp
import os
from pathlib import Path
import threading

class DescargadorModelo:
    """
    Modelo que maneja la lógica de descarga de videos y audio
    """
    
    def __init__(self):
        # Directorio por defecto para las descargas
        self.directorio_descarga = str(Path.home() / "Descargas")
        # Callback para actualizar el progreso
        self.callback_progreso = None
        # Callback para notificar cuando termine la descarga
        self.callback_completado = None
        # Callback para manejar errores
        self.callback_error = None
        
    def establecer_directorio_descarga(self, directorio):
        """
        Establece el directorio donde se guardarán las descargas
        """
        self.directorio_descarga = directorio
        
    def establecer_callbacks(self, progreso=None, completado=None, error=None):
        """
        Establece las funciones callback para comunicarse con el controlador
        """
        self.callback_progreso = progreso
        self.callback_completado = completado
        self.callback_error = error
        
    def _hook_progreso(self, d):
        """
        Hook interno para capturar el progreso de la descarga
        """
        if d['status'] == 'downloading':
            # Extrae información del progreso
            porcentaje = d.get('_percent_str', 'N/A')
            velocidad = d.get('_speed_str', 'N/A')
            tiempo_restante = d.get('_eta_str', 'N/A')
            
            # Llama al callback si está definido
            if self.callback_progreso:
                self.callback_progreso(porcentaje, velocidad, tiempo_restante)
                
        elif d['status'] == 'finished':
            # Notifica que la descarga ha terminado
            if self.callback_completado:
                self.callback_completado(d['filename'])
    
    def obtener_informacion_video(self, url):
        """
        Obtiene información básica del video sin descargarlo
        """
        try:
            # Configuración básica para extraer información
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extrae información relevante
                titulo = info.get('title', 'Sin título')
                duracion = info.get('duration', 0)
                formatos_disponibles = []
                
                # Procesa los formatos disponibles
                if 'formats' in info:
                    for formato in info['formats']:
                        if formato.get('vcodec') != 'none':  # Tiene video
                            ext = formato.get('ext', 'mp4')
                            quality = formato.get('height', 'N/A')
                            formatos_disponibles.append(f"{ext} - {quality}p")
                
                return {
                    'titulo': titulo,
                    'duracion': duracion,
                    'formatos': list(set(formatos_disponibles))  # Elimina duplicados
                }
                
        except Exception as e:
            return None
    
    def descargar_video(self, url, formato='mp4', calidad='best'):
        """
        Descarga el video en el formato y calidad especificados
        """
        def _descargar():
            try:
                # Configuración para la descarga de video
                ydl_opts = {
                    'format': f'{calidad}[ext={formato}]/best[ext={formato}]/best',
                    'outtmpl': os.path.join(self.directorio_descarga, '%(title)s.%(ext)s'),
                    'progress_hooks': [self._hook_progreso],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
            except Exception as e:
                if self.callback_error:
                    self.callback_error(f"Error al descargar video: {str(e)}")
        
        # Ejecuta la descarga en un hilo separado para no bloquear la interfaz
        hilo_descarga = threading.Thread(target=_descargar)
        hilo_descarga.daemon = True
        hilo_descarga.start()
    
    def descargar_audio(self, url, formato_audio='mp3'):
        """
        Descarga solo el audio del video
        """
        def _descargar_audio():
            try:
                # Configuración para extraer solo audio
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.directorio_descarga, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': formato_audio,
                        'preferredquality': '192',
                    }],
                    'progress_hooks': [self._hook_progreso],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
            except Exception as e:
                if self.callback_error:
                    self.callback_error(f"Error al descargar audio: {str(e)}")
        
        # Ejecuta la descarga en un hilo separado
        hilo_descarga = threading.Thread(target=_descargar_audio)
        hilo_descarga.daemon = True
        hilo_descarga.start()
    
    def validar_url(self, url):
        """
        Valida si la URL es compatible con yt-dlp
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Intenta extraer información básica
                ydl.extract_info(url, download=False)
                return True
                
        except:
            return False