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
        Configura los callbacks de la vista para manejar eventos de usuario.
        """
        self.view.set_callbacks(
            on_paste_url=self._on_paste_url,
            on_browse_folder=self._on_browse_folder,
            on_get_info=self._on_get_info,
            on_start_download=self._on_start_download,
            on_cancel_download=self._on_cancel_download,
            on_clear_log=self._on_clear_log,
            on_open_folder=self._on_open_folder,
            on_save_log=self._on_save_log,
            on_closing=self._on_closing
        )
    
    def _setup_initial_download_path(self):
        """
        Configura la ruta inicial de descarga y la crea si no existe.
        """
        default_path = self.model.get_default_download_path()
        
        # Crear carpeta si no existe
        try:
            Path(default_path).mkdir(parents=True, exist_ok=True)
            self.view.set_download_path(default_path)
            self.view.add_log_message(f"📁 Carpeta de descarga: {default_path}")
        except Exception as e:
            self.view.add_log_message(f"⚠️ Error al crear carpeta de descarga: {str(e)}")
            # Usar carpeta actual como alternativa
            self.view.set_download_path("./")
    
    # === CALLBACKS DEL MODELO ===
    
    def _on_download_progress(self, progress_data: Dict[str, Any]):
        """
        Maneja los eventos de progreso de descarga del modelo.
        
        Args:
            progress_data: Datos de progreso de yt-dlp
        """
        if progress_data['status'] == 'downloading':
            # Extraer información de progreso
            filename = progress_data.get('filename', 'Archivo desconocido')
            filename = Path(filename).name  # Solo el nombre del archivo
            
            # Actualizar progreso si está disponible
            if 'downloaded_bytes' in progress_data and 'total_bytes' in progress_data:
                downloaded = progress_data['downloaded_bytes']
                total = progress_data['total_bytes']
                percentage = (downloaded / total) * 100
                
                # Actualizar barra de progreso
                self.view.update_progress(percentage)
                
                # Formatear tamaños
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                
                # Mostrar progreso en el log
                self.view.add_log_message(
                    f"📥 Descargando: {filename} - {downloaded_mb:.1f}/{total_mb:.1f} MB ({percentage:.1f}%)"
                )
            else:
                # Si no hay información de bytes, usar progreso indeterminado
                self.view.update_progress()
                self.view.add_log_message(f"📥 Descargando: {filename}")
        
        elif progress_data['status'] == 'finished':
            # Descarga de archivo individual completada
            filename = progress_data.get('filename', 'Archivo')
            filename = Path(filename).name
            self.view.add_log_message(f"✅ Completado: {filename}")
    
    def _on_model_log(self, message: str):
        """
        Maneja los mensajes de log del modelo.
        
        Args:
            message: Mensaje a mostrar en el log
        """
        self.view.add_log_message(message)
    
    def _on_download_completion(self, success: bool, message: str):
        """
        Maneja la finalización de la descarga.
        
        Args:
            success: True si la descarga fue exitosa
            message: Mensaje de finalización
        """
        # Actualizar estado visual
        self.view.set_download_state(False)
        
        if success:
            self.view.add_log_message("🎉 ¡Descarga completada exitosamente!")
            self.view.show_success_dialog("Descarga Completada", message)
        else:
            self.view.add_log_message(f"❌ Descarga fallida: {message}")
    
    def _on_download_error(self, error_message: str):
        """
        Maneja los errores durante la descarga.
        
        Args:
            error_message: Mensaje de error
        """
        # Actualizar estado visual
        self.view.set_download_state(False)
        
        # Mostrar error
        self.view.add_log_message(f"❌ Error: {error_message}")
        self.view.show_error_dialog("Error de Descarga", error_message)
    
    # === CALLBACKS DE LA VISTA ===
    
    def _on_paste_url(self):
        """
        Maneja el evento de pegar URL desde el portapapeles.
        """
        try:
            # Obtener contenido del portapapeles
            clipboard_content = self.view.root.clipboard_get()
            
            if clipboard_content and clipboard_content.strip():
                # Limpiar y validar URL
                url = clipboard_content.strip()
                
                if self.model.validate_url(url):
                    self.view.set_url(url)
                    self.view.add_log_message(f"📋 URL pegada: {url}")
                else:
                    self.view.add_log_message("⚠️ La URL del portapapeles no parece ser válida")
                    self.view.show_error_dialog("URL Inválida", 
                                              "La URL del portapapeles no es compatible con este descargador.")
            else:
                self.view.add_log_message("⚠️ El portapapeles está vacío")
                
        except tk.TclError:
            self.view.add_log_message("⚠️ No se pudo acceder al portapapeles")
            self.view.show_error_dialog("Error", "No se pudo acceder al portapapeles.")
    
    def _on_browse_folder(self):
        """
        Maneja el evento de seleccionar carpeta de descarga.
        """
        current_path = self.view.get_download_path()
        
        # Abrir diálogo de selección de carpeta
        new_path = self.view.select_folder(current_path)
        
        if new_path:
            try:
                # Verificar que se puede escribir en la carpeta
                Path(new_path).mkdir(parents=True, exist_ok=True)
                
                # Actualizar ruta en la vista
                self.view.set_download_path(new_path)
                self.view.add_log_message(f"📁 Nueva carpeta de descarga: {new_path}")
                
            except Exception as e:
                self.view.add_log_message(f"❌ Error al acceder a la carpeta: {str(e)}")
                self.view.show_error_dialog("Error de Carpeta", 
                                          f"No se pudo acceder a la carpeta seleccionada:\n{str(e)}")
    
    def _on_get_info(self):
        """
        Maneja el evento de obtener información del video/playlist.
        """
        url = self.view.get_url()
        
        # Validar URL
        if not url:
            self.view.show_error_dialog("URL Requerida", "Por favor, ingresa una URL válida.")
            return
        
        if not self.model.validate_url(url):
            self.view.show_error_dialog("URL Inválida", "La URL ingresada no es compatible.")
            return
        
        # Deshabilitar botón mientras se obtiene información
        self.view.info_btn.config(state=tk.DISABLED)
        
        try:
            self.view.add_log_message("🔍 Obteniendo información del video/playlist...")
            
            # Extraer información usando el modelo
            raw_info = self.model.extract_video_info(url)
            self.current_video_info = raw_info
            
            # Determinar si es playlist o video individual
            if 'entries' in raw_info and raw_info['entries']:
                # Es una playlist
                self.is_playlist = True
                formatted_info = self.model.get_playlist_info_formatted(raw_info)
                self.view.add_log_message(f"📋 Playlist detectada: {formatted_info['total_videos']} videos")
            else:
                # Es un video individual
                self.is_playlist = False
                formatted_info = self.model.get_video_info_formatted(raw_info)
                self.view.add_log_message(f"🎥 Video individual detectado: {formatted_info['titulo']}")
            
            # Mostrar información en diálogo
            self.view.show_info_dialog(formatted_info)
            
        except Exception as e:
            self.view.add_log_message(f"❌ Error al obtener información: {str(e)}")
            self.view.show_error_dialog("Error", f"No se pudo obtener información del video:\n{str(e)}")
        
        finally:
            # Rehabilitar botón
            self.view.info_btn.config(state=tk.NORMAL)
    
    def _on_start_download(self):
        """
        Maneja el evento de iniciar descarga.
        """
        # Validar entrada
        url = self.view.get_url()
        if not url:
            self.view.show_error_dialog("URL Requerida", "Por favor, ingresa una URL válida.")
            return
        
        if not self.model.validate_url(url):
            self.view.show_error_dialog("URL Inválida", "La URL ingresada no es compatible.")
            return
        
        # Verificar si ya hay una descarga en curso
        if self.model.is_downloading:
            self.view.show_error_dialog("Descarga en Curso", 
                                      "Ya hay una descarga en progreso. Espera a que termine o cancélala.")
            return
        
        # Obtener configuraciones
        download_path = self.view.get_download_path()
        quality = self.view.get_quality()
        download_type = self.view.get_download_type()
        
        # Verificar carpeta de descarga
        try:
            Path(download_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.view.show_error_dialog("Error de Carpeta", 
                                      f"No se pudo crear la carpeta de descarga:\n{str(e)}")
            return
        
        # Confirmar descarga de playlist si es necesario
        if download_type == "playlist" and self.current_video_info:
            if 'entries' in self.current_video_info:
                total_videos = len(self.current_video_info['entries'])
                if total_videos > 10:  # Confirmar si hay muchos videos
                    confirm = self.view.show_question_dialog(
                        "Confirmar Descarga de Playlist",
                        f"Estás a punto de descargar {total_videos} videos.\n¿Deseas continuar?"
                    )
                    if not confirm:
                        return
        
        # Actualizar estado visual
        self.view.set_download_state(True)
        
        # Iniciar descarga
        success = self.model.start_download(url, download_path, quality, download_type)
        
        if not success:
            self.view.set_download_state(False)
            self.view.show_error_dialog("Error", "No se pudo iniciar la descarga.")
    
    def _on_cancel_download(self):
        """
        Maneja el evento de cancelar descarga.
        """
        if self.model.is_downloading:
            confirm = self.view.show_question_dialog(
                "Cancelar Descarga",
                "¿Estás seguro de que deseas cancelar la descarga actual?"
            )
            
            if confirm:
                self.model.cancel_download()
                self.view.add_log_message("⚠️ Descarga cancelada por el usuario")
                self.view.set_download_state(False)
    
    def _on_clear_log(self):
        """
        Maneja el evento de limpiar el registro de actividad.
        """
        confirm = self.view.show_question_dialog(
            "Limpiar Registro",
            "¿Estás seguro de que deseas limpiar el registro de actividad?"
        )
        
        if confirm:
            self.view.clear_log()
            self.view.add_log_message("🗑️ Registro limpiado")
    
    def _on_open_folder(self):
        """
        Maneja el evento de abrir la carpeta de descargas.
        """
        download_path = self.view.get_download_path()
        
        try:
            # Crear carpeta si no existe
            Path(download_path).mkdir(parents=True, exist_ok=True)
            
            # Abrir carpeta según el sistema operativo
            if platform.system() == "Windows":
                os.startfile(download_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", download_path])
            else:  # Linux y otros
                subprocess.run(["xdg-open", download_path])
            
            self.view.add_log_message(f"📂 Carpeta abierta: {download_path}")
            
        except Exception as e:
            self.view.add_log_message(f"❌ Error al abrir carpeta: {str(e)}")
            self.view.show_error_dialog("Error", f"No se pudo abrir la carpeta:\n{str(e)}")
    
    def _on_save_log(self):
        """
        Maneja el evento de guardar el registro de actividad.
        """
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"registro_descarga_{timestamp}.txt"
        
        # Abrir diálogo de guardado
        file_path = self.view.select_save_file(default_name)
        
        if file_path:
            try:
                # Obtener contenido del log
                log_content = self.view.get_log_content()
                
                # Añadir header con información adicional
                header = f"""# Registro de Descarga de Videos
# Generado el: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Aplicación: Descargador de Videos y Playlists
# ================================================

"""
                
                # Guardar archivo
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(header + log_content)
                
                self.view.add_log_message(f"💾 Registro guardado en: {file_path}")
                self.view.show_success_dialog("Registro Guardado", 
                                            f"El registro se ha guardado exitosamente en:\n{file_path}")
                
            except Exception as e:
                self.view.add_log_message(f"❌ Error al guardar registro: {str(e)}")
                self.view.show_error_dialog("Error", f"No se pudo guardar el registro:\n{str(e)}")
    
    def _on_closing(self):
        """
        Maneja el evento de cierre de la aplicación.
        """
        # Verificar si hay descarga en curso
        if self.model.is_downloading:
            confirm = self.view.show_question_dialog(
                "Confirmar Salida",
                "Hay una descarga en curso. ¿Estás seguro de que deseas salir?\n"
                "La descarga actual se cancelará."
            )
            
            if not confirm:
                return
            
            # Cancelar descarga
            self.model.cancel_download()
        
        # Mensaje de despedida
        self.view.add_log_message("👋 Cerrando aplicación...")
        
        # Cerrar aplicación
        self.view.destroy()
    
    # === MÉTODO PRINCIPAL ===
    
    def run(self):
        """
        Inicia la aplicación ejecutando el bucle principal de la interfaz.
        """
        try:
            self.view.add_log_message("🎬 Aplicación lista para usar")
            self.view.run()
        except KeyboardInterrupt:
            self.view.add_log_message("⚠️ Aplicación interrumpida por el usuario")
        except Exception as e:
            self.view.add_log_message(f"❌ Error crítico: {str(e)}")
            self.view.show_error_dialog("Error Crítico", 
                                      f"Se produjo un error crítico:\n{str(e)}")
        finally:
            # Limpiar recursos
            if self.model.is_downloading:
                self.model.cancel_download()


# === PUNTO DE ENTRADA ===

def main():
    """
    Función principal para ejecutar la aplicación.
    """
    try:
        # Crear y ejecutar controlador
        controller = VideoDownloaderController()
        controller.run()
        
    except ImportError as e:
        print(f"❌ Error de importación: {str(e)}")
        print("💡 Asegúrate de que todos los módulos estén disponibles")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()